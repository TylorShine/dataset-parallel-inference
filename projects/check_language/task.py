import json
import os
import sqlite3
import asyncio
from os import path
from os.path import dirname
import tqdm
from datasets import load_dataset
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAIError
from openai.types.chat import ChatCompletion
from pydantic import BaseModel

from core import InferenceTask
from asyncio import Semaphore


class Task(InferenceTask):

    def __init__(self):
        self._db = sqlite3.connect(path.join(dirname(__file__), "..", "gpt_oss", "db.sqlite"))
        self._cur = self._db.cursor()
        self._cur.execute('CREATE TABLE IF NOT EXISTS check_language(id INT PRIMARY KEY,appropriate INT,reason TEXT);')
        self.dataset = range(self._cur.execute("SELECT COUNT(*) FROM result;").fetchone()[0])
        load_dotenv(path.join(dirname(__file__), ".env"))
        self._client = AsyncOpenAI(api_key=os.environ["API_KEY"], base_url=os.environ["BASE_URL"], timeout=None)

    def get_length(self) -> int:
        return self._cur.execute("SELECT COUNT(*) FROM result;").fetchone()[0]

    def __del__(self):
        self._db.commit()
        self._cur.close()
        self._db.close()

    async def process(self, data, order: int, sem: Semaphore, bar: tqdm.tqdm):
        # id列に order の値が存在するか確認、したらスキップ
        if self._cur.execute("SELECT COUNT(*) FROM check_language WHERE id=?;", (order,)).fetchone()[0] > 0:
            bar.update(1)
            return
        async with sem:
            content, source = self._cur.execute("SELECT content,source FROM result WHERE id=?;", (order,)).fetchone()
            prompt = [
                {
                    "role": "system",
                    "content": "以下の翻訳前・翻訳後の文章について、翻訳によって言語のニュアンス・文脈が正しく伝わっているかを確認し、BOOLEANで答えてください。"
                               "例えば、翻訳前文章で、英語の発音・イントネーションやつづりに関するコンテンツを含む場合、そのまま全訳しても日本語では意味が通じません。"
                }, {
                    "role": "user",
                    "content": "=======翻訳前=============\n"
                               + "\n".join([item["content"] or "" for item in json.loads(source)]) +
                               "=========================\n"
                               "\n=======翻訳後=============\n"
                               + "\n".join([item["content"] or "" for item in json.loads(content)]) +
                               "\n=========================\n"
                               ""
                }
            ]

            class IsAppropriate(BaseModel):
                appropriate: bool

            sleep_time = 4.0
            resp: ChatCompletion
            while True:
                try:
                    resp = await self._client.chat.completions.parse(
                        messages=prompt,
                        model=os.environ["MODEL_NAME"],
                        extra_body={
                            "separate_reasoning": True
                        },
                        reasoning_effort="medium",
                        response_format=IsAppropriate
                    )
                    if resp.choices[0].message.parsed is None:
                        raise OpenAIError("Failed to parse response: ", resp.choices[0].message)
                    break
                except OpenAIError as e:
                    if sleep_time > 16.0:
                        bar.update(1)
                        return
                    print(f"OpenAI API Error: {e}")
                    await asyncio.sleep(sleep_time)
                    sleep_time *= 2
            # print(json.dumps(output_json, ensure_ascii=False))
            reasoning_content = resp.choices[0].message.reasoning_content
            decision = resp.choices[0].message.parsed.appropriate
            self._cur.execute("REPLACE INTO check_language(id, appropriate,reason) VALUES (?,?,?);",
                              (order, decision, reasoning_content))
            self._db.commit()
            bar.update(1)
