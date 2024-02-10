from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, WebSocketDisconnect
from fastapi.websockets import WebSocket
from fastapi.responses import HTMLResponse
import csv
from dotenv import load_dotenv
import os
import speech_recognition as sr
import MeCab

import cybozu


def read_csv_file(file_name: str) -> list[list[str]]:
    """CSVデータをファイルから読み込む

    Args:
        file_name (str): ファイルパス

    Returns:
        list[list[str]]: CSVレコードのリスト
    """
    data = []
    with open(file_name, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # ヘッダーレコードを除く
        for row in reader:
            data.append(row)
    return data


tagger = MeCab.Tagger("-Owakati")


def extract_nouns(text: str) -> list[str]:
    """人名を抽出します。

    Args:
        text (str): テキスト

    Returns:
        list[str]: 人名のリスト
    """
    nouns = []
    node = tagger.parseToNode(text)
    while node:
        if node.feature.startswith("名詞") and "人名" in node.feature:
            if node.surface not in nouns:
                nouns.append(node.surface)
        node = node.next
    return nouns


load_dotenv()
account = os.environ["CYBOZU_ACCOUNT"]
password = os.environ["CYBOZU_PASSWORD"]


async def send_schedule(websocket, uid):
    events = cybozu.get_events(account, password, uid)
    if len(events) > 0:
        for e in events:
            await websocket.send_text("今日のスケジュール: " + e.text)
    else:
        await websocket.send_text("今日のスケジュール: なし")


file_name = "users.csv"
data = read_csv_file(file_name)


app = FastAPI()


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Voice Reception</title>
    </head>
    <body>
        <h1>Voice Reception</h1>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            await websocket.send_text("話してください:")
            r.adjust_for_ambient_noise(source, duration=1)  # 話している間に環境音を調整
            audio = r.listen(source)
            await websocket.send_text("音声認識中...")
            try:
                text = r.recognize_google(audio, language="ja-JP")
                await websocket.send_text("あなたが言ったこと: " + text)
                names = extract_nouns(text)
                await websocket.send_text("人名: " + str(names))
                filtered_data = [
                    record
                    for record in data
                    if any(name in record[1] for name in names)
                ]
                await websocket.send_text("検索結果: " + str(filtered_data))
                await websocket.send_text("予定検索中")
                # for user in filtered_data:
                #     await get_schedule(websocket, user[0])
                with ThreadPoolExecutor(max_workers=1) as executor:
                    for user in filtered_data:
                        executor.submit(send_schedule, websocket, user[0])
            except sr.UnknownValueError:
                await websocket.send_text("Google Speech Recognitionが音声を理解できませんでした")
            except sr.RequestError as e:
                await websocket.send_text(
                    "Google Speech Recognitionサービスから結果をリクエストできませんでした; {0}".format(e)
                )
            except WebSocketDisconnect:
                break
