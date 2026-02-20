import ast
import glob
import json
import os
import sqlite3
import asyncio
from os import path
from os.path import dirname, basename
from pathlib import Path
from typing import Iterator

import jsonpath_ng
import tqdm
from datasets import load_dataset
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAIError
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam
from core import InferenceTask
from asyncio import Semaphore


def _parse_function_definitions(_paths: Iterator[Path]) -> dict[str, list[str]]:
    _ret = dict()
    for _path in _paths:
        for _item in ast.parse(_path.read_text()).body[0].body:
            if isinstance(_item, ast.FunctionDef):
                if _item.name == "build_description":
                    args = [a.arg for a in _item.args.args]
                    args.remove("self")
                    _ret[ast.parse(_path.read_text()).body[0].name] = args
    return _ret


def _define_fields(json_obj: dict, available_args: dict[str, list[str]]) -> list[str]:
    _fields = []
    if "prompt" in json_obj.keys():
        for order, _ in enumerate(json_obj["prompt"].values()):
            _fields.append(f"$.prompt[{order}].content")
    if "reward_model" in json_obj.keys():
        for order, _rubric in enumerate(json_obj["reward_model"]["rubrics"]):
            if _rubric["tags"]["verifier"] == "llm":
                _fields.append(f"$.reward_model.rubrics[{order}].tags.criterion")
            if _rubric["tags"]["function"] in available_args.keys():
                for _arg in available_args[_rubric["tags"]["function"]]:
                    if _rubric["tags"]["parameters"].get(_arg, None) is not None:
                        if isinstance(_rubric["tags"]["parameters"][_arg], str):
                            _fields.append(f"$.reward_model.rubrics[{order}].tags.parameters.{_arg}")
    return _fields


class Task(InferenceTask):
    def __init__(self):
        self._db = sqlite3.connect(Path(__file__).parent.joinpath("db.sqlite"))
        self._cur = self._db.cursor()
        self._cur.execute(
            "CREATE TABLE IF NOT EXISTS translate(id INT PRIMARY KEY,content TEXT,loc TEXT,source TEXT,reason TEXT);"
        )
        load_dotenv(path.join(dirname(__file__), ".env"))
        self._client = AsyncOpenAI(api_key=os.environ["API_KEY"], base_url=os.environ["BASE_URL"], timeout=None)
        self.function_definitions = _parse_function_definitions(
            Path(__file__).parent.joinpath("functions").glob("*.py"))
        self.dataset = load_dataset("NovelHacja/RubricHub_v1_config", "instruction_following", split="train",
                                    streaming=False)
        load_dotenv(path.join(dirname(__file__), ".env"))

    def get_length(self) -> int:
        return self.dataset.info.splits["train"].num_examples

    def __del__(self):
        self._db.commit()
        self._cur.close()
        self._db.close()

    async def process(self, data, order: int, sem: Semaphore, bar: tqdm.tqdm):
        # id列に order の値が存在するか確認、したらスキップ
        if self._cur.execute("SELECT COUNT(*) FROM translate WHERE id=?;", (order,)).fetchone()[0] > 0:
            bar.update(1)
            return
        async with sem:
            elaborate_prompt = """日本語への翻訳タスクです。以降、外国語の翻訳対象の文章が与えられます。その文章を日本語に翻訳するにあたって、注意すべきと思われる点を全ての条件について具体的にどのような訳語を用いるべきかについてまで、確実と言い切れるまで** 何度も **推敲してください。なお、議論にあたっては以下の条件を**遵守**すること。

 - 人名・固有名詞については翻訳せず、原文での表記のまま書くこと。
 - 原文に忠実に翻訳し、原文に存在する情報を欠落させたり、書かれていないことを付け加えないこと。
 - 原文の雰囲気や文脈に基づいて翻訳すること。
 - 推敲とは原文の文脈を分析し、次に多義語の選択肢を挙げ、最後に最も適切な表現を決定するプロセスを順を追って説明することです。
 - 最終的な翻訳結果自体は出力しないでください。"""
            if json.dumps(data, ensure_ascii=False).__len__() > 30000:
                bar.update(1)
                return
            _contents = []
            _reasons = []
            _positions = []
            for _translate_pos in _define_fields(data, self.function_definitions):
                _positions.append(_translate_pos)
                subject_txt = jsonpath_ng.parse(_translate_pos).find(data)[0]
                prompt = f"""以下のデータセットのうち、{_translate_pos}に該当する部分について処理します。

{json.dumps(data, ensure_ascii=False, indent=2)}

=======(翻訳の一貫性のための)翻訳履歴=========
{"\n".join(["\n=======" + _pos + "=========\n" + _cont for _cont, _pos in zip(_contents, _positions)])}
==============================
{elaborate_prompt}
======={_translate_pos}=======
{subject_txt}"""
                sleep_time = 4.0
                while True:
                    try:
                        resp_1 = await self._client.responses.create(
                            input=prompt,  # noqa
                            model=os.environ["MODEL_NAME"],
                            extra_body={
                                "top_k": 20,
                                "chat_template_kwargs": {"enable_thinking": False},
                            },
                            temperature=0.7,
                            top_p=0.8,
                        )
                        resp_2 = await self._client.responses.create(
                            previous_response_id=resp_1.id,
                            input="推敲をもとに、全文の和訳のみを出力してください。",
                            model=os.environ["MODEL_NAME"],
                            extra_body={
                                "top_k": 20,
                                "chat_template_kwargs": {"enable_thinking": False},
                            },
                            temperature=0.7,
                            top_p=0.8,
                        )
                        break
                    except (OpenAIError, ValueError) as e:
                        if sleep_time > 32.0:
                            print(f"OpenAI API Error: {e}")
                            bar.update(1)
                            return
                        await asyncio.sleep(sleep_time)
                        sleep_time *= 2
                _contents.append(resp_2.output_text)
                _reasons.append(resp_1.output_text)
            self._cur.execute("REPLACE INTO translate(id, content, loc, source, reason) VALUES (?,?,?,?,?);", (
                order,
                json.dumps(_contents, ensure_ascii=False),
                json.dumps(_positions, ensure_ascii=False),
                json.dumps(data, ensure_ascii=False),
                json.dumps(_reasons, ensure_ascii=False)
            ))
            self._db.commit()
            bar.update(1)
