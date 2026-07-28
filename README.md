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

* ❔Как запустить проект

** Запуск локально через npm

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/ваш-ник/dream_analyzer.git
cd dream_analyzer

# 2. Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Установите зависимости
pip install -r requirements.txt

# 4. Настройте .env
cp .env.example .env
# Заполните BOT_TOKEN, GIGACHAT_CLIENT_ID, GIGACHAT_CLIENT_SECRET

# 5. Примените миграции
python manage.py migrate

# 6. Запустите Django-сервер
python manage.py runserver

# 7. В отдельном терминале запустите бота
python bot.py
