import httpx
import json
import time

base = 'http://127.0.0.1:8000/api/v1'
email = f'debuguser{int(time.time())}@example.com'
print('signup', email)

try:
    r = httpx.post(
        f'{base}/auth/signup',
        json={'name': 'debug', 'email': email, 'password': 'Pass1234!'},
        timeout=30.0,
    )
    print('signup status', r.status_code)
    print(r.text)
except Exception as e:
    print('signup failed', e)
    raise

try:
    r2 = httpx.post(
        f'{base}/auth/login',
        json={'email': email, 'password': 'Pass1234!'},
        timeout=30.0,
    )
    print('login status', r2.status_code)
    print(r2.text)
    r2.raise_for_status()
    data = r2.json()
    token = data['access_token']
except Exception as e:
    print('login failed', e)
    raise

headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

try:
    r3 = httpx.post(
        f'{base}/ai/chat-tutor',
        json={'topic_title': 'DBMS', 'question': 'What is a relational database?', 'chat_history': []},
        headers=headers,
        timeout=60.0,
    )
    print('chat status', r3.status_code)
    print(r3.text)
except Exception as e:
    print('chat failed', e)
    raise
