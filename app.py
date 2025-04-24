import os
from flask import Flask, redirect, request, render_template
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")

@app.route('/')
def index():
    return render_template('index.html',
        google_client_id=GOOGLE_CLIENT_ID,
        google_redirect_uri="https://google-login-test-8r50.onrender.com/auth/google/callback",
        facebook_app_id=FACEBOOK_APP_ID,
        facebook_redirect_uri="https://google-login-test-8r50.onrender.com/auth/facebook/callback"
    )

@app.route('/auth/google/callback')
def google_callback():
    code = request.args.get('code')
    token_url = 'https://oauth2.googleapis.com/token'
    token_data = {
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': 'https://google-login-test-8r50.onrender.com/auth/google/callback',
        'grant_type': 'authorization_code'
    }

    token_res = requests.post(token_url, data=token_data)
    if token_res.status_code != 200:
        return f"<h1>Google Token 取得失敗</h1><pre>{token_res.text}</pre>"

    try:
        access_token = token_res.json()['access_token']
    except Exception as e:
        return f"<h1>Token JSON 解析失敗</h1><pre>{token_res.text}</pre>"

    user_info = requests.get(
        'https://www.googleapis.com/oauth2/v3/userinfo',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    if user_info.status_code != 200:
        return f"<h1>使用者資訊取得失敗</h1><pre>{user_info.text}</pre>"

    return f"<h1>Google 登入成功</h1><pre>{user_info.json()}</pre>"

@app.route('/auth/facebook/callback')
def facebook_callback():
    code = request.args.get('code')
    token_url = 'https://graph.facebook.com/v13.0/oauth/access_token'
    token_params = {
        'client_id': FACEBOOK_APP_ID,
        'client_secret': FACEBOOK_APP_SECRET,
        'redirect_uri': 'https://google-login-test-8r50.onrender.com/auth/facebook/callback',
        'code': code
    }

    token_res = requests.get(token_url, params=token_params)
    token_json = token_res.json()

    if 'access_token' not in token_json:
        return f"<h1>Facebook Token 錯誤</h1><pre>{token_json}</pre>"

    access_token = token_json['access_token']

    user_info_res = requests.get(
        'https://graph.facebook.com/me',
        params={
            'fields': 'id,name,email',
            'access_token': access_token
        }
    )
    if user_info_res.status_code != 200:
        return f"<h1>使用者資訊取得失敗</h1><pre>{user_info_res.text}</pre>"

    return f"<h1>Facebook 登入成功</h1><pre>{user_info_res.json()}</pre>"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
