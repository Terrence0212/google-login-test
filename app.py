import os
from flask import Flask, redirect, request, render_template
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth/google/callback')
def google_callback():
    code = request.args.get('code')
    token_url = 'https://oauth2.googleapis.com/token'
    token_data = {
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': 'http://127.0.0.1:5000/auth/google/callback',
        'grant_type': 'authorization_code'
    }

    token_res = requests.post(token_url, data=token_data)

    print("Google Token 回應狀態：", token_res.status_code)
    print("Google Token 回應內容：", token_res.text)

    # 如果 Google 回傳的狀態碼不是 200，直接回傳錯誤頁面
    if token_res.status_code != 200:
        return f"<h1>Google Token 取得失敗</h1><pre>{token_res.text}</pre>"

    try:
        token_json = token_res.json()
        access_token = token_json['access_token']
    except Exception as e:
        return f"<h1>Token JSON 解析失敗</h1><pre>{token_res.text}</pre>"

    user_info = requests.get(
        'https://www.googleapis.com/oauth2/v3/userinfo',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    # 同樣加錯誤檢查
    if user_info.status_code != 200:
        return f"<h1>使用者資訊取得失敗</h1><pre>{user_info.text}</pre>"

    user_data = user_info.json()
    return f"<h1>Google 登入成功</h1><pre>{user_data}</pre>"

    try:
        token_json = token_res.json()
        access_token = token_json['access_token']
    except Exception as e:
        return f"<h1>Token 解析錯誤</h1><pre>{token_res.text}</pre>"

    # 拿 access_token 去取得使用者資訊
    user_info = requests.get(
        'https://www.googleapis.com/oauth2/v3/userinfo',
        headers={'Authorization': f'Bearer {access_token}'}
    ).json()

    return f"<h1>Google 登入成功</h1><pre>{user_info}</pre>"

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
