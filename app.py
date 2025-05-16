from flask import Flask, request, abort, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,
                            FlexSendMessage, LocationSendMessage,
                            VideoSendMessage, ImageSendMessage, StickerSendMessage)
import json
import requests
import os

app = Flask(__name__)

#歷史對話
message_history = []

#LINE Bot token 和 secret
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

# Gemini 回覆
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
        return "Error"

    try:
        result = response.json()
        reply_text = result['candidates'][0]['content']['parts'][0]['text']
        return reply_text
    except Exception:
        return "Error"

#LINE 文字訊息
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

        # 儲存歷史對話
        message_history.append({
            'user': user_id,
            'message': message,
            'reply': reply_text
        })

    # 回覆使用者
    line_bot_api.reply_message(event.reply_token, output)

# RESTful API：儲存使用者訊息
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

# RESTful API：取得所有歷史訊息
@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify(message_history), 200

# RESTful API：刪除所有對話紀錄
@app.route('/messages', methods=['DELETE'])
def delete_messages():
    message_history.clear()
    return jsonify({'status': 'All messages deleted'}), 200

# 啟動伺服器
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000)) 
    app.run(host="0.0.0.0", port=port)
