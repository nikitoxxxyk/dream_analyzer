from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Dream
from .serializers import DreamSerializer
import requests
import os
import base64
import uuid
from django.core.cache import cache
from dotenv import load_dotenv

# env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
# load_dotenv(env_path)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_dream(request):
    """Создание сна с интерпретацией от GigaChat"""
    user_id = request.data.get('user_id')
    text = request.data.get('text')
    
    if not user_id or not text:
        return Response({'error': 'user_id and text are required'}, status=400)
    
    print(f"📥 Получен сон от {user_id}: {text[:50]}...")
    
    dream = Dream.objects.create(user_id=str(user_id), text=text)
    
    try:
        client_id = os.getenv('GIGACHAT_CLIENT_ID')
        client_secret = os.getenv('GIGACHAT_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            dream.interpretation = "⚠️ GigaChat не настроен. Напишите текст сна для анализа."
            dream.save()
            serializer = DreamSerializer(dream)
            return Response(serializer.data)
        
        print("🔄 Получаю токен GigaChat...")
        
        auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        credentials = f"{client_id}:{client_secret}"
        base64_credentials = base64.b64encode(credentials.encode()).decode()
        
        auth_headers = {
            "Authorization": f"Basic {base64_credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid.uuid4()),
            "User-Agent": "Mozilla/5.0"
        }
        auth_data = {"scope": "GIGACHAT_API_PERS"}
        
        auth_response = requests.post(auth_url, headers=auth_headers, data=auth_data, verify=False, timeout=10)
        
        if auth_response.status_code != 200:
            dream.interpretation = f"❌ Ошибка авторизации GigaChat: {auth_response.status_code}"
            dream.save()
            serializer = DreamSerializer(dream)
            return Response(serializer.data)
        
        access_token = auth_response.json()["access_token"]
        print(f"✅ Токен получен: {access_token[:20]}...")
        
        api_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "GigaChat",
            "messages": [
                {"role": "system", "content": "Ты психолог. Дай интерпретацию сна."},
                {"role": "user", "content": f"Сон: {text}"}
            ],
            "temperature": 0.7,
            "max_tokens": 1024  # ← УВЕЛИЧЕНО
        }
        
        print("🧠 Отправляю запрос на анализ...")
        response = requests.post(api_url, headers=headers, json=payload, timeout=30, verify=False)
        
        print(f"📊 Статус анализа: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                interpretation = result['choices'][0]['message']['content']
                print(f"✅ Анализ успешен: {interpretation[:100]}...")
            except Exception as e:
                print(f"❌ Ошибка парсинга JSON: {e}")
                print(f"📝 Ответ: {response.text[:500]}")
                interpretation = "⚠️ Ошибка обработки ответа от GigaChat."
        else:
            interpretation = f"❌ Ошибка анализа: {response.status_code}"
            print(f"❌ Ответ GigaChat: {response.text}")
            
    except Exception as e:
        print(f"💥 Исключение: {e}")
        interpretation = f"❌ Ошибка: {str(e)}"
    
    dream.interpretation = interpretation
    dream.save()
    
    serializer = DreamSerializer(dream)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def user_dreams(request):
    user_id = request.GET.get('user_id')
    dreams = Dream.objects.filter(user_id=str(user_id)).order_by('-created_at')[:10]
    serializer = DreamSerializer(dreams, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def last_dream(request):
    user_id = request.GET.get('user_id')
    dream = Dream.objects.filter(user_id=str(user_id)).order_by('-created_at').first()
    if dream:
        serializer = DreamSerializer(dream)
        return Response(serializer.data)
    return Response({})

