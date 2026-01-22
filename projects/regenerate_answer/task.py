import json
import os
import sqlite3
import asyncio
from os import path
from os.path import dirname
import tqdm

from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAIError
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionSystemMessageParam

from core import InferenceTask
from asyncio import Semaphore


def clean_reason_text(text: str) -> str:
    lowered = (text or "").lower()
    keywords = ("verdict", "boolean", "therefore", "answer", "result", "decision")
    kept_lines = []
    for line in lowered.splitlines():
        if "false" in line and any(keyword in line for keyword in keywords):
            continue
        kept_lines.append(line)
    return "\n".join(kept_lines)


class Task(InferenceTask):
    def __init__(self):
        self._db = sqlite3.connect(path.join(dirname(__file__), "..", "gpt_oss", "db.sqlite"))
        self._cur = self._db.cursor()
        self._cur.execute("CREATE TABLE IF NOT EXISTS regenerate_answer(id INT PRIMARY KEY,content TEXT,reason TEXT);")
        self.dataset = [row[0] for row in
                        self._cur.execute("SELECT id FROM check_language WHERE appropriate = 0;").fetchall()]
        load_dotenv(path.join(dirname(__file__), ".env"))
        self._client = AsyncOpenAI(api_key=os.environ["API_KEY"], base_url=os.environ["BASE_URL"], timeout=None)

    def get_length(self) -> int:
        return self.dataset.__len__()

    def __del__(self):
        self._db.commit()
        self._cur.close()
        self._db.close()

    async def process(self, data, order: int, sem: Semaphore, bar: tqdm.tqdm):
        # id列に data の値が存在するか確認、したらスキップ
        if self._cur.execute("SELECT COUNT(*) FROM regenerate_answer WHERE id=?;", (data,)).fetchone()[0] > 0:
            bar.update(1)
            return
        async with ((sem)):
            input_json = json.loads(self._cur.execute("SELECT source FROM result WHERE id = ?;", (data,)).fetchone()[0])

            original_messages = []
            translated_messages = []

            for message in input_json:
                original_messages.append(message.copy())
                if message["content"] == "":
                    translated_messages.append(message.copy())
                    continue
                sleep_time = 4.0

                while True:
                    try:
                        reason_text = clean_reason_text(
                            self._cur.execute("SELECT reason FROM check_language WHERE id = ?;", (data,), ).fetchone()[0]
                        )
                        chat_string = "======誤っている出力に対する指摘=======\n\n" + \
                                      reason_text + \
                                      "\n===============================\n\n\n" + \
                                      "過去の会話履歴(一貫性のある翻訳のためのコンテキスト):\n\n\n" + \
                                      "\n\n\n".join(filter(None, [
                                          f"===={orig['role']}=============\n" +
                                          (orig['content'] or "") +
                                          "\n\n-------↓↓↓↓↓↓-------\n\n" +
                                          (trans['content'] or "") +
                                          "\n============================="
                                          if (orig["content"] or "") != "" else None for orig, trans in
                                          zip(original_messages, translated_messages)
                                      ])) + "\n\n\n\n" + \
                                      "\n===文章A==========================\n\n\n" + str(message["content"])

                        # print(f"{chat_string}")
                        resp = await self._client.chat.completions.create(
                            messages=[
                                ChatCompletionSystemMessageParam(
                                    content="外国語の文章Aが与えられます。誤りの指摘を参考にして、その文章を適切に日本語に翻訳してください。なお、以下の条件を**遵守**すること。\n" + \
                                            "\n" + \
                                            " - 人名については翻訳せず原文での表記のまま書くこと。\n" + \
                                            " - 原文に忠実に翻訳し原文に存在する情報を欠落させたり書かれていないことを付け加えないこと。\n" + \
                                            " - 原文の雰囲気や文脈に基づいて翻訳すること。\n" + \
                                            " - 翻訳済みの文章のみを出力し、余計な説明や注釈を加えないこと。\n"
                                            " - 外国語が要件である場合にはそれに従い、必ずしも翻訳する必要があるわけではない。\n"
                                            " - 会話履歴を参照し、一貫性のある・辻褄の合う・**会話のやりとりとして正しい**文章を生成すること。\n",
                                    role="system"
                                ),
                                ChatCompletionUserMessageParam(
                                    content=chat_string,
                                    role="user"
                                )],
                            model=os.environ["MODEL_NAME"],
                            extra_body={"separate_reasoning": True},
                            reasoning_effort="medium",
                        )
                        # '{"callable": "80049556000000000000008c2a73676c616e672e7372742e73616d706c696e672e637573746f6d5f6c6f6769745f70726f636573736f72948c23476c6d344d6f655468696e6b696e674275646765744c6f67697450726f636573736f729493942e"}'
                        translated_messages.append(resp.choices[0].message.to_dict())
                        break
                    except OpenAIError as e:
                        if sleep_time > 16.0:
                            translated_messages.append({"role": "assistant", "content": "<-- output is missing -->"})
                            break
                        print(f"OpenAI API Error: {e}")
                        await asyncio.sleep(sleep_time)
                        sleep_time *= 2
            # print(json.dumps(translated_messages, ensure_ascii=False))
            for i in range(input_json.__len__()):
                translated_messages[i].update(role=input_json[i]["role"])
        self._cur.execute("REPLACE INTO regenerate_answer(id, content) VALUES (?,?);", (
            data,
            json.dumps(translated_messages, ensure_ascii=False)),
        )
        self._db.commit()
        bar.update(1)
