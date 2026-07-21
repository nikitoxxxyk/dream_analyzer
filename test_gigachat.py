
import os

import base64

import uuid

import requests

from dotenv import load_dotenv



load_dotenv()



print("=== ТЕСТ GIGACHAT API ===")

print(f".env path: {os.path.abspath('.env')}")



client_id = os.getenv('GIGACHAT_CLIENT_ID')

client_secret = os.getenv('GIGACHAT_CLIENT_SECRET')



print(f"Client ID: {'✅' if client_id else '❌'} {client_id[:10] if client_id else 'НЕТ'}")

print(f"Client Secret: {'✅' if client_secret else '❌'} {client_secret[:10] if client_secret else 'НЕТ'}")



if not client_id or not client_secret:

    print("❌ Ошибка: нет credentials в .env")

    exit(1)



try:

    auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    credentials = f"{client_id}:{client_secret}"

    base64_credentials = base64.b64encode(credentials.encode()).decode()

    

    print(f"Credentials base64: {base64_credentials[:30]}...")

    

    auth_headers = {

        "Authorization": f"Basic {base64_credentials}",

        "Content-Type": "application/x-www-form-urlencoded",

        "Accept": "application/json",

        "RqUID": str(uuid.uuid4()),

        "User-Agent": "Mozilla/5.0"

    }

    auth_data = {"scope": "GIGACHAT_API_PERS"}

    

    print("Отправляю запрос на токен...")

    response = requests.post(auth_url, headers=auth_headers, data=auth_data, 

                           verify=False, timeout=15)

    

    print(f"Статус: {response.status_code}")

    print(f"Ответ: {response.text[:200]}")

    

    if response.status_code == 200:

        token = response.json()["access_token"]

        print(f"✅ Токен получен: {token[:30]}...")

        

        # Проверка моделей

        models_resp = requests.get(

            "https://gigachat.devices.sberbank.ru/api/v1/models",

            headers={"Authorization": f"Bearer {token}"},

            verify=False,

            timeout=10

        )

        print(f"Модели статус: {models_resp.status_code}")

        print(f"Модели ответ: {models_resp.text[:200]}")

    else:

        print("❌ Ошибка получения токена")

        

except Exception as e:

    print(f"❌ Исключение: {e}")

