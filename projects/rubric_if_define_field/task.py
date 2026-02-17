import glob
import json
import os
import sqlite3
import asyncio
from os import path
from os.path import dirname, basename
from pathlib import Path

import jsonpath_ng
import tqdm
from datasets import load_dataset
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAIError
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam
from pydantic import BaseModel

from core import InferenceTask
from asyncio import Semaphore


class Task(InferenceTask):
    def __init__(self):
        self._db = sqlite3.connect(path.join(dirname(__file__), "db.sqlite"))
        self._cur = self._db.cursor()
        self.dataset = load_dataset("NovelHacja/RubricHub_v1_config", "instruction_following", split="train",
                                    streaming=False)
        self._cur.execute("CREATE TABLE IF NOT EXISTS result(id INT PRIMARY KEY,content TEXT,source TEXT,reason TEXT);")
        load_dotenv(path.join(dirname(__file__), ".env"))
        self._client = AsyncOpenAI(api_key=os.environ["API_KEY"], base_url=os.environ["BASE_URL"], timeout=None)
        self.function_definitions = {basename(_file).removesuffix(".py") for _file in
                                     glob.glob(path.join(dirname(__file__), "functions", "*.py"))}

    def get_length(self) -> int:
        return self.dataset.info.splits["train"].num_examples

    def __del__(self):
        self._db.commit()
        self._cur.close()
        self._db.close()

    class Paths(BaseModel):
        json_paths: list[str]

    def shrink_long_string_of_json(self, json_obj, max_length=1000):
        if isinstance(json_obj, dict):
            return {k: self.shrink_long_string_of_json(v, max_length) for k, v in json_obj.items()}
        elif isinstance(json_obj, list):
            return [self.shrink_long_string_of_json(item, max_length) for item in json_obj]
        elif isinstance(json_obj, str) and len(json_obj) > max_length:
            return json_obj[:max_length // 3] + "..." + json_obj[-max_length // 3:]
        else:
            return json_obj

    async def process(self, data, order: int, sem: Semaphore, bar: tqdm.tqdm):
        # id列に order の値が存在するか確認、したらスキップ
        if self._cur.execute("SELECT COUNT(*) FROM result WHERE id=?;", (order,)).fetchone()[0] > 0:
            bar.update(1)
            return
        async with sem:
            input_json = data["extra_info"].copy()
            input_json = self.shrink_long_string_of_json(input_json)
            prompt = """以下のJSONデータはRL用のリワードモデルのデータセットです。データセットを翻訳するにあたって、まず、翻訳する必要のあるフィールドを列挙する必要があります。
            翻訳する必要のあるフィールドをJSONPathの形式のテキストのリストで全て列挙してください。必ずルート記述子`$`をつけてください。
            翻訳する必要のあるフィールドは全て文字列型です。
            フィルタ演算やワイルドカードを用いず、単純な子孫アクセスや配列アクセスのみを用いて、翻訳する必要のあるフィールドを特定してください。
            """
            _functions = []
            for _function in jsonpath_ng.parse("$.reward_model.rubrics[*].function").find(input_json):
                if _function in self.function_definitions:
                    _functions.append(Path(__file__).parent.joinpath("functions", _function + ".py").read_text())
            if _functions:
                prompt += "\n\n以下にバリデーション用関数の実装を示すので参考にしてください。\n" + "\n".join(
                    _functions)

            prompt += "\n=======JSONデータ=======\n\n" + json.dumps(input_json, ensure_ascii=False, indent=2)
            sleep_time = 4.0
            messages = [
                ChatCompletionUserMessageParam(
                    content=prompt,
                    role="user"
                )
            ]
            while True:
                try:
                    resp = await self._client.chat.completions.parse(
                        messages=messages,
                        model=os.environ["MODEL_NAME"],
                        extra_body={"separate_reasoning": True},
                        reasoning_effort="high",
                        response_format=self.Paths
                    )
                    messages.append(resp.choices[0].message.model_dump())
                    if resp.choices[0].message.parsed is None:
                        raise OpenAIError("Failed to parse response: ", resp.choices[0].message)
                    _unexisting_paths = []
                    _unexpected_paths = []
                    for _path in resp.choices[0].message.parsed.json_paths:
                        if jsonpath_ng.parse(_path).find(input_json).__len__() == 0:
                            _unexisting_paths.append(_path)
                    for _path in resp.choices[0].message.parsed.json_paths:
                        if jsonpath_ng.parse(_path).find(input_json).__len__() != 0 and \
                                not isinstance(jsonpath_ng.parse(_path).find(input_json)[0], str):
                            _unexpected_paths.append(_path)
                    messages.append(ChatCompletionUserMessageParam(
                        content=f"以下のJSONPathは入力JSONのどの要素にもマッチしませんでした。再確認して、全て出力しなおしてください。"
                                f"JSONPath: {', '.join(_unexisting_paths)}\n"
                                f"以下のJSONPathは文字列型に一致しませんでした。再確認して、全て出力しなおしてください。"
                                f"JSONPath: {', '.join(_unexpected_paths)}\n"
                        ,
                        role="user"
                    ))
                    if _unexisting_paths:
                        raise ValueError(f"JSONPath '{_path}' does not match any element in the input JSON.")
                    break
                except (OpenAIError, ValueError) as e:
                    if sleep_time > 32.0:
                        print(f"OpenAI API Error: {e}")
                        bar.update(1)
                        return
                    await asyncio.sleep(sleep_time)
                    sleep_time *= 2

        self._cur.execute("REPLACE INTO result(id, content, source,reason) VALUES (?,?,?,?);",
                          (order,
                           json.dumps(resp.choices[0].message.parsed.json_paths, ensure_ascii=False),
                           json.dumps(data["extra_info"], ensure_ascii=False),
                           resp.choices[0].message.reasoning_content),
                          )
        self._db.commit()
        bar.update(1)
