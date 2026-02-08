import json
import os
import sqlite3
import asyncio
from os import path
from os.path import dirname
import tqdm
from datasets import load_dataset, IterableDataset, Dataset
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAIError
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionSystemMessageParam

from core import InferenceTask
from asyncio import Semaphore


class Task(InferenceTask):
    def __init__(self):
        self._db = sqlite3.connect(path.join(dirname(__file__), "db.sqlite"))
        self._cur = self._db.cursor()
        self.dataset = {
            c: load_dataset("NovelHacja/RubricHub_v1_config", c, split="train", streaming=False)
            for c in ["chat", "instruction_following", "medical", "science", "writing"]
        }
        for c in self.dataset.keys():
            table_name = c.replace('-', '_')
            self._cur.execute(f"CREATE TABLE IF NOT EXISTS {table_name}(id INT PRIMARY KEY,content TEXT,source TEXT,reasoning TEXT);")
        self.replace_keys = ["prompt", "reward_model", "Rubrics:reward_model.rubrics"]
        load_dotenv(path.join(dirname(__file__), ".env"))
        self._client = AsyncOpenAI(api_key=os.environ["API_KEY"], base_url=os.environ["BASE_URL"], timeout=None)
        self.temperature = 0.5

    def get_length(self) -> int:
        # streaming==Falseと仮定
        return sum(map(lambda x: len(x), self.dataset.values()))

    def __del__(self):
        self._db.commit()
        self._cur.close()
        self._db.close()

    async def process(self, data, order: int, sem: Semaphore, bar: tqdm.tqdm, config: str = "default"):
        # id列に order の値が存在するか確認、したらスキップ
        table_name = config.replace('-', '_')
        if self._cur.execute(f"SELECT COUNT(*) FROM {table_name} WHERE id=?;", (order,)).fetchone()[0] > 0:
            bar.update(1)
            return
        async with sem:
            try:
                # "extra_info" は dict型
                input_json_str = json.dumps(data["extra_info"], ensure_ascii=False, separators=(",", ":"))
            except json.JSONDecodeError:
                # "extra_info" がデコードできない場合は "prompts" と "reward_model", "Rubrics" を取得
                try:
                    input_json_str = json.dumps({"prompts": data["prompts"], "reward_model": data["reward_model"], "rubrics": data["Rubrics"]}, ensure_ascii=False, separators=(",", ":"))
                except json.JSONDecodeError:
                    # "Rubrics" がデコードできないか存在しない場合は "prompts" と "reward_model" を取得
                    input_json_str = json.dumps({"prompts": data["prompts"], "reward_model": data["reward_model"]}, ensure_ascii=False, separators=(",", ":"))

            original_json = data.copy()
            translated_json = None
            reasoning_text = None

            if original_json != None:
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

                        resp = await self._client.chat.completions.create(
                            messages=[
                            ChatCompletionSystemMessageParam(
                                content=system_string,
                                role="system"
                            ),
                            ChatCompletionUserMessageParam(
                                content=chat_string,
                                role="user"
                            )],
                            model=os.environ["MODEL_NAME"],
                            temperature=self.temperature,
                            extra_body={"separate_reasoning": True},
                            reasoning_effort="medium",
                        )
                        translated_message = resp.choices[0].message.content
                        translated_message = translated_message.replace("```json\n", "").replace("\n```", "")
                        translated_message_json = json.loads(translated_message)
                        translated_json = original_json.copy()
                        for key in self.replace_keys:
                            if ":" in key:
                                key, source_key = key.split(":")
                                if "." in source_key:
                                    sub_keys = source_key.split(".")
                                    val = translated_message_json
                                    for sub_key in sub_keys:
                                        if sub_key in val:
                                            val = val[sub_key]
                                        else:
                                            raise ValueError(f"{source_key} not found in translated message")
                                    translated_json[key] = val.copy()
                            else:
                                if key in translated_message_json:
                                    translated_json[key] = translated_message_json[key].copy()
                                else:
                                    raise ValueError(f"{key} not found in translated message")
                        translated_json["extra_info"] = translated_message_json.copy()
                        reasoning_text = getattr(resp.choices[0].message, "reasoning", None)
                        break
                    except OpenAIError as e:
                        if sleep_time > 16.0:
                            translated_message = {"role": "assistant", "content": "<-- output is missing -->"}
                            break
                        print(f"OpenAI API Error: {e}")
                        await asyncio.sleep(sleep_time)
                        sleep_time = sleep_time ** 2
                    except (json.JSONDecodeError, ValueError) as e:
                        if sleep_time > 16.0:
                            translated_message = {"role": "assistant", "content": "<-- output is missing JSON -->"}
                            break
                        print(f"JSON Error: {e}")
                        await asyncio.sleep(sleep_time)
                        sleep_time = sleep_time ** 2
                # print(json.dumps(translated_json, ensure_ascii=False))
        self._cur.execute(f"REPLACE INTO {table_name}(id, content, source, reasoning) VALUES (?,?,?,?);",
            (order,
             json.dumps(translated_json, ensure_ascii=False),
             json.dumps(original_json.copy(), ensure_ascii=False),
             reasoning_text),
        )
        self._db.commit()
        bar.update(1)
