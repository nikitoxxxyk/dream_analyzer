# 🌙 Dream Analyzer

Анализ снов с помощью искусственного интеллекта. Telegram-бот + веб-приложение на Django.

---

## 📌 О проекте

Dream Analyzer — это сервис, который помогает пользователям анализировать и интерпретировать свои сны с использованием нейросетей.

**Ключевые возможности:**
- 📝 Запись снов через Telegram-бота
- 🎤 Голосовой ввод с распознаванием речи
- 🧠 AI-анализ сна через GigaChat
- 📊 Личный кабинет с историей снов и статистикой
- 📈 Визуализация категорий и активности
- 🐳 Упаковка в Docker

---

## 🛠️ Технологии

| Компонент | Технология |
|-----------|------------|
| **Веб-приложение** | Django 4.2, Django REST Framework |
| **Бот** | python-telegram-bot 20.3 |
| **AI** | GigaChat API (анализ снов), SpeechRecognition (распознавание голоса) |
| **База данных** | SQLite (PostgreSQL для продакшена) |
| **Распознавание речи** | Google Speech Recognition + ffmpeg |
| **Контейнеризация** | Docker, Docker Compose |
| **Тестирование** | Django Test Framework, pytest |

#❔Как запустить проект

## Запуск локально через npm

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/nikitoxxxyk/dream_analyzer.git
cd dream_analyzer

# 2. Создайте виртуальное окружение
Для Windows: python -m venv venv
Для Mac/Linux: python3 -m venv venv

# 3. Активируйте виртуальное окружение
Windows: venv\Scripts\activate
Mac/Linux: source venv/bin/activate

# 4. Установите зависимости
pip install -r requirements.txt

# 5. Настройте .env
cp .env.example .env
# Заполните BOT_TOKEN, GIGACHAT_CLIENT_ID, GIGACHAT_CLIENT_SECRET

# 6. Примените миграции
python manage.py migrate

# 7. Запустите Django-сервер
python manage.py runserver

# 8. В отдельном терминале запустите бота
python bot.py
```

## 🐳 Через Docker и Docker-compose
``` bash
# 1. Соберите и запустите контейнеры
docker-compose up -d --build

# 2. Проверьте статус
docker-compose ps

# 3. Если хотите проверить все контейнеры, включая незапущенные
docker-compose ps -a

# 4. Просмотреть логи
docker-compose logs -f

# 5. Остановить контейнер
docker-compose down
```

# ✅ Тестирование проекта
``` bash
python manage.py test # Тестировка всего проекта

# API
python manage.py test dream_api.test_api

# Веб-приложение
python manage.py test dream_web.tests
```

