# from flask import Flask, request, abort
# from linebot import LineBotApi, WebhookHandler
# from linebot.exceptions import InvalidSignatureError
# from linebot.models import (MessageEvent, TextMessage, TextSendMessage,FlexSendMessage,LocationSendMessage,
#                             VideoSendMessage,ImageSendMessage,StickerSendMessage)
# import json
# import requests  # 加上這一行來匯入 requests 库

# # 初始化 Flask App
# app = Flask(__name__)

# # LINE bot 資訊（請填上你自己的 Token 和 Secret）
# ACCESS_TOKEN = 'Pgo+htulCicresZzk4EOQFwqDGNauaAt2SvjaAc6frVNO1QTBj3CfL495pOVkLyp03hGLDddSEfHLMcCkt3QmUn8E8dNqDSD35Uyr3t+4mFHUI/7DPQvsjJl0Pra0xqTZrogfB+E1uyjmgfkmxsIcAdB04t89/1O/w1cDnyilFU='
# CHANNEL_SECRET = 'c9d3bf4f2296c16b417e048415f3cbbd'

# line_bot_api = LineBotApi(ACCESS_TOKEN)
# handler = WebhookHandler(CHANNEL_SECRET)

# # 根目錄：支援 GET 方法，方便測試 server 有沒有啟動
# @app.route("/", methods=['GET'])
# def home():
#     return "LINE bot webhook is alive!"

# # 處理 webhook：LINE 平台會送 POST 請求過來
# @app.route("/", methods=['POST'])
# def callback():
#     signature = request.headers['X-Line-Signature']
#     body = request.get_data(as_text=True)

#     try:
#         handler.handle(body, signature)
#     except InvalidSignatureError:
#         abort(400)

#     return 'OK'

# # 處理事件（這邊只處理文字訊息）

# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     message = event.message.text
#     if message == 'image':
#         output = ImageSendMessage(
#         original_content_url='https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Cat_August_2010-3.jpg/1200px-Cat_August_2010-3.jpg',
#         preview_image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Cat_August_2010-3.jpg/1200px-Cat_August_2010-3.jpg'
#     )
#     elif message == 'sticker':
#         output = StickerSendMessage(
#             package_id='6325',
#             sticker_id='10979907'
#         )
#     elif message == 'video':
#         output = VideoSendMessage(
#             original_content_url='https://media.w3.org/2010/05/sintel/trailer.mp4',  # LINE 官方影片
#         preview_image_url='https://peach.blender.org/wp-content/uploads/title_anouncement.jpg?x11217'  # 預覽圖
#         )
#     elif message == 'location':
#         output = LocationSendMessage(
#             title='元智大學',
#             address='桃園市中壢區遠東路135號',
#             latitude=24.970579866790025,
#             longitude=121.26343149758962
#         )
#     else:
#         reply_text = get_gemini_response(message)
#         output = TextSendMessage(text=reply_text)
    
#     line_bot_api.reply_message(
#         event.reply_token,
#         output
#     )

# def get_gemini_response(user_message):
#     # Gemini API 請求資料
#     url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=AIzaSyDAlxFa-T_KD7BWbmJt3DZO6-I5Br-lC0o"
    
#     headers = {
#         "Content-Type": "application/json"
#     }
    
#     # 請求資料
#     data = {
#         "contents": [{
#             "parts": [{"text": user_message}]
#         }]
#     }
    
#     # 發送 POST 請求
#     response = requests.post(url, headers=headers, data=json.dumps(data))
    
#     if response.status_code == 200:
#         result = response.json()
#         return result['candidates'][0]['content']['parts'][0]['text']
#     else:
#         print(f"Gemini API 請求錯誤: {response.status_code}")
#         return "對不起，我無法理解你的問題，請稍後再試。"



# # 啟動 server
# if __name__ == "__main__":
#     app.run(port=5000)

from flask import Flask, request, abort, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,
                            FlexSendMessage, LocationSendMessage,
                            VideoSendMessage, ImageSendMessage, StickerSendMessage)
import json
import requests

app = Flask(__name__)

# 👉 記憶體中儲存歷史對話
message_history = []

# 替換成你的 LINE Bot token 和 secret
ACCESS_TOKEN = 'Pgo+htulCicresZzk4EOQFwqDGNauaAt2SvjaAc6frVNO1QTBj3CfL495pOVkLyp03hGLDddSEfHLMcCkt3QmUn8E8dNqDSD35Uyr3t+4mFHUI/7DPQvsjJl0Pra0xqTZrogfB+E1uyjmgfkmxsIcAdB04t89/1O/w1cDnyilFU='
CHANNEL_SECRET = 'c9d3bf4f2296c16b417e048415f3cbbd'
GEMINI_API_KEY = 'AIzaSyBtZCKBXy4vUUMWuJ4A5Q2JGpxeNQ09uVI'

line_bot_api = LineBotApi(ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/", methods=['GET'])
def home():
    return "LINE bot webhook is alive!"

@app.route("/", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# ✅ Gemini 回覆函式
def get_gemini_response(user_message):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": user_message
                    }
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code != 200:
        return "AI 無法處理請求，請稍後再試。"

    try:
        result = response.json()
        reply_text = result['candidates'][0]['content']['parts'][0]['text']
        return reply_text
    except Exception:
        return "AI 回應異常，請稍後再試。"

# ✅ 處理 LINE 文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    message = event.message.text

    if message == 'image':
        output = ImageSendMessage(
            original_content_url='https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Cat_August_2010-3.jpg/1200px-Cat_August_2010-3.jpg',
            preview_image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Cat_August_2010-3.jpg/1200px-Cat_August_2010-3.jpg'
        )
    elif message == 'sticker':
        output = StickerSendMessage(
            package_id='6325',
            sticker_id='10979907'
        )
    elif message == 'video':
        output = VideoSendMessage(
            original_content_url='https://media.w3.org/2010/05/sintel/trailer.mp4',
            preview_image_url='https://peach.blender.org/wp-content/uploads/title_anouncement.jpg?x11217'
        )
    elif message == 'location':
        output = LocationSendMessage(
            title='元智大學',
            address='桃園市中壢區遠東路135號',
            latitude=24.970579866790025,
            longitude=121.26343149758962
        )
    else:
        reply_text = get_gemini_response(message)
        output = TextSendMessage(text=reply_text)

        # ✅ 儲存歷史對話
        message_history.append({
            'user': user_id,
            'message': message,
            'reply': reply_text
        })

    # 回覆使用者
    line_bot_api.reply_message(event.reply_token, output)

# ✅ RESTful API：儲存使用者訊息（可手動送入）
@app.route('/messages', methods=['POST'])
def save_message():
    data = request.get_json()
    user = data.get('user')
    message = data.get('message')
    reply = data.get('reply', '')

    if not user or not message:
        return jsonify({'error': 'Missing user or message'}), 400

    message_history.append({'user': user, 'message': message, 'reply': reply})
    return jsonify({'status': 'Message saved'}), 201

# ✅ RESTful API：取得所有歷史訊息
@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify(message_history), 200

# ✅ RESTful API：刪除所有對話紀錄
@app.route('/messages', methods=['DELETE'])
def delete_messages():
    message_history.clear()
    return jsonify({'status': 'All messages deleted'}), 200

# ✅ 啟動伺服器
if __name__ == "__main__":
    app.run(port=5000)
