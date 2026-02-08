import json
import os
import sqlite3
import asyncio
from os import path
from os.path import dirname
from typing import Any
import tqdm
from datasets import load_dataset
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAIError

from core import InferenceTask
from asyncio import Semaphore

from projects.example_3_follow.model import RootModel


class Task(InferenceTask):
    def __init__(self):
        self._db = sqlite3.connect(path.join(dirname(__file__), "db.sqlite"))
        self._cur = self._db.cursor()
        self._db_write_sem = Semaphore(value=1)
        self.dataset = load_dataset("NovelHacja/RubricHub_v1_config", "instruction_following", split="train", streaming=False)
        self._cur.execute(f"CREATE TABLE IF NOT EXISTS result(id INT PRIMARY KEY,content TEXT,source TEXT,reasoning TEXT);")
        self._replace_keys = ["prompt", "reward_model", "Rubrics:reward_model.rubrics"]
        load_dotenv(path.join(dirname(__file__), ".env"))
        self._client = AsyncOpenAI(api_key=os.environ["API_KEY"], base_url=os.environ["BASE_URL"], timeout=None)
        self._temperature = 0.5

    def get_length(self) -> int:
        # streaming==Falseと仮定
        return sum(map(len, self.dataset.values()))

    def __del__(self):
        self._db.commit()
        self._cur.close()
        self._db.close()

    async def process(self, data, order: int, sem: Semaphore, bar: tqdm.tqdm):
        # id列に order の値が存在するか確認、したらスキップ
        if self._cur.execute(f"SELECT COUNT(*) FROM result WHERE id=?;", (order,)).fetchone()[0] > 0:
            bar.update(1)
            return
        async with sem:
            try:
                # "extra_info" は dict型
                input_json_str = json.dumps(data["extra_info"], ensure_ascii=False, separators=(",", ":"))
            except (KeyError, ValueError):
                # "extra_info" がデコードできない場合は "prompts" と "reward_model", "Rubrics" を取得
                try:
                    input_json_str = json.dumps({"prompts": data["prompts"], "reward_model": data["reward_model"], "rubrics": data["Rubrics"]}, ensure_ascii=False, separators=(",", ":"))
                except (KeyError, ValueError):
                    # "Rubrics" がデコードできないか存在しない場合は "prompts" と "reward_model" を取得
                    input_json_str = json.dumps({"prompts": data["prompts"], "reward_model": data["reward_model"]}, ensure_ascii=False, separators=(",", ":"))

            original_obj = data.copy()
            translated_obj = None
            reasoning_text = None

            if original_obj != None:
                sleep_time = 2.0
                while True:
                    try:
                        if "/" not in os.environ["MODEL_NAME"]:
                            model_provider_text = ""
                            model_name = os.environ["MODEL_NAME"]
                        else:
                            model_provider, model_name = os.environ["MODEL_NAME"].split("/")[:2]
                            model_provider_text = f"{model_provider}製の"
                        system_string = f"あなたは{model_provider_text}大規模言語モデル、{model_name}です。広範な知識を伴う言語理解力やユーザ指示への忠実性に秀でており、完全な回答を提供します。"
                        chat_string = f'続くJSONのデータのフィールド`"content"`と`"criterion"`の値のみを、構造をそのままに、全ての文を省略無しで正確に日本語へと翻訳してください。ただし、特に日本語に翻訳したことによって生じる可能性もある`"criterion"`の矛盾は解決してください。`"criterion"`の内容は"`"content"`の回答に対する評価基準"です。JSONのみ出力すること。:\n\n{input_json_str}'
                        # print(f"{chat_string}")

                        resp = await self._client.responses.parse(
                            input=[
                                {"role": "system", "content": system_string},
                                {"role": "user", "content": chat_string}
                            ],
                            text_format=RootModel,
                            model=os.environ["MODEL_NAME"],
                            temperature=self._temperature,
                            extra_body={"separate_reasoning": True},
                            reasoning={"effort": "medium"},
                        )
                        if resp.output_parsed is None:
                            raise ValueError("Failed to parse response, output_parsed is None")
                        translated_resp: dict[str, Any] = resp.output_parsed.model_dump()
                        translated_obj = original_obj.copy()
                        
                        for key in self._replace_keys:
                            if key in translated_resp.keys():
                                translated_obj[key] = translated_resp[key].copy()
                            elif ":" in key:
                                # keyが「dst:src.subkey」の形式の場合は、「src」のデータを「dst」にコピーする
                                key, source_key = key.split(":")
                                if "." in source_key:
                                    # subkeyがある場合のtraverse
                                    source_key = source_key.split(".")
                                    val = translated_resp
                                    for sub_key in source_key:
                                        val = val[sub_key].copy()
                                else:
                                    translated_obj[key] = translated_obj[source_key].copy()
                            else:
                                raise ValueError(f"key {key} not found in translated message")
                            
                        # reasoningの文字列を取得
                        reasoning_text = [m.content for m in resp.output if m.type == "reasoning"][0]
                        reasoning_text = None if reasoning_text is None else reasoning_text[0]
                        reasoning_text = "" if "text" not in reasoning_text.keys() else reasoning_text["text"]
                        # print(f"reasoning: {reasoning_text}")
                        break
                    except OpenAIError as e:
                        if sleep_time > 16.0:
                            translated_obj = {"role": "assistant", "content": "<-- output is missing -->"}
                            break
                        print(f"OpenAI API Error: {e}")
                        await asyncio.sleep(sleep_time)
                        sleep_time = sleep_time ** 2
                    except (json.JSONDecodeError, ValueError) as e:
                        if sleep_time > 16.0:
                            translated_obj = {"role": "assistant", "content": "<-- output is missing JSON -->"}
                            break
                        print(f"JSON Error: {e}")
                        await asyncio.sleep(sleep_time)
                        sleep_time = sleep_time ** 2
                # print(json.dumps(translated_obj, ensure_ascii=False))
        async with self._db_write_sem:
            self._cur.execute(f"REPLACE INTO result(id, content, source, reasoning) VALUES (?,?,?,?);",
                (order,
                json.dumps(translated_obj, ensure_ascii=False),
                json.dumps(original_obj.copy(), ensure_ascii=False),
                reasoning_text),
            )
            self._db.commit()
        bar.update(1)
