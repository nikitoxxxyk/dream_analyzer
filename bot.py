import sys
import os
import logging
import asyncio
import aiohttp 
from dotenv import load_dotenv
import requests 
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
import re
from voice_handler import voice_processor
import requests

load_dotenv()

# ============================================
# НАСТРОЙКА ЛОГИРОВАНИЯ
# ============================================
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ************** Для удаленного сервака!!! *************
# BOT_TOKEN = os.getenv('BOT_TOKEN')
# DJANGO_API_URL = "https://dream-analyzer.tw1.ru/api/create-dream/"
# DJANGO_API_BASE = "https://dream-analyzer.tw1.ru/api/"
# USER_DREAMS_URL = "https://dream-analyzer.tw1.ru/api/user-dreams/"
# LAST_DREAM_URL = "https://dream-analyzer.tw1.ru/api/last-dream/"

# ************** На локальном ******************
BOT_TOKEN = os.getenv('BOT_TOKEN')
# DJANGO_API_URL = "http://127.0.0.1:8000/api/create-dream/"
# DJANGO_API_BASE = "http://127.0.0.1:8000/api/"
# USER_DREAMS_URL = "http://127.0.0.1:8000/api/user-dreams/"
# LAST_DREAM_URL = "http://127.0.0.1:8000/api/last-dream/"

if os.getenv('DOCKER_ENV') == 'true':
    DJANGO_API_URL = 'http://web:8000/api/create-dream/'
    DJANGO_API_BASE = 'http://web:8000/api/'
    USER_DREAMS_URL = 'http://web:8000/api/user-dreams/'
    LAST_DREAM_URL = 'http://web:8000/api/last-dream/'

else:
    DJANGO_API_URL = "http://127.0.0.1:8000/api/create-dream/"
    DJANGO_API_BASE = "http://127.0.0.1:8000/api/"
    USER_DREAMS_URL = "http://127.0.0.1:8000/api/user-dreams/"
    LAST_DREAM_URL = "http://127.0.0.1:8000/api/last-dream/"


if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в .env файле!")

# ============================================
# КЛАВИАТУРА
# ============================================
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("📝 Записать сон"), KeyboardButton("🎤 Голосовой ввод")],
        [KeyboardButton("🔮 Последний сон"), KeyboardButton("📖 История снов")],
        [KeyboardButton("🌐 Веб-приложение"), KeyboardButton("ℹ️ Помощь")]
    ]   
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ============================================
# ОБРАБОТЧИКИ КОМАНД
# ============================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение при старте"""
    user_name = update.message.from_user.first_name
    
    # ИСПРАВЛЕНО: Используем f-строку для подстановки имени
    welcome_text = f"""
🤖 *{user_name}, Добро пожаловать в Dream Analyzer от Nikitoxxxyk!*

Я помогу вам анализировать и интерпретировать ваши сны с помощью искусственного интеллекта.

*🎤 НОВОЕ: Голосовой ввод!*
Теперь вы можете описывать сны голосом!

*Доступные команды:*
📝 Записать сон - опишите свой сон для анализа
🎤 Голосовой ввод - отправьте голосовое сообщение 🆕 
📖 История снов - просмотр ваших последних снов  
🔮 Последний сон - детали последнего записанного сна
🌐 Веб-приложение - полная версия в браузере
ℹ️ Помощь - справка по использованию бота

*Просто опишите свой сон или выберите команду ниже!*
    """
    await update.message.reply_text(
        welcome_text, 
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

async def web_version(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о веб-версии"""
    web_url = "dream-analyzer.tw1.ru"
    
    message = f"""
🌐 *Веб-версия Dream Analyzer*

Откройте полную версию в браузере для:
• 📊 Детальной статистики и графиков
• 🔍 Удобного поиска по всем снам  
• 📈 Анализа паттернов и тенденций
• 🎨 Красивого интерфейса

*Ссылка:* {web_url}
    
*💡 Совет:* Для быстрого доступа добавьте сайт в закладки!
    """
    
    await update.message.reply_text(
        message, 
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Справка по использованию"""
    help_text = """
*📋 Как пользоваться ботом:*

1. *📝 Записать сон* - нажмите кнопку или просто опишите свой сон
2. *📖 История снов* - просмотр ваших последних записей
3. *🔮 Последний сон* - детальный просмотр последнего сна

*💡 Советы:*
• Описывайте сны максимально подробно
• Регулярно ведите дневник снов
• Обращайте внимание на повторяющиеся символы

*Для начала просто опишите свой сон!*
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

# ============================================
# АСИНХРОННЫЕ ЗАПРОСЫ К API
# ============================================
# async def make_api_request(url, method='GET', data=None):
#     """Универсальная функция для асинхронных запросов к API"""
#     try:
#         timeout = aiohttp.ClientTimeout(total=30)
#         async with aiohttp.ClientSession(timeout=timeout) as session:
#             if method == 'GET':
#                 async with session.get(url) as response:
#                     return response
#             elif method == 'POST':
#                 async with session.post(url, json=data) as response:
#                     return response
#     except aiohttp.ClientError as e:
#         logger.error(f"Ошибка API запроса: {e}")
#         return None

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает историю снов пользователя"""
    user_id = update.message.from_user.id
    
    await update.message.chat.send_action(action="typing")
    
    try:
        url = f"{USER_DREAMS_URL}?user_id={user_id}"
        logger.info(f"📤 GET запрос на {url}")
        
        response = requests.get(url, timeout=10)
        logger.info(f"📥 Статус: {response.status_code}")
        
        if response.status_code == 200:
            dreams = response.json()
            if dreams:
                message = "📖 *Ваши последние сны:*\n\n"
                for i, dream in enumerate(dreams[:5], 1):
                    date = dream.get('created_at', '')[:10]
                    text_preview = dream.get('text', '')[:40] + "..." if len(dream.get('text', '')) > 40 else dream.get('text', '')
                    message += f"{i}. 📅 {date}: {text_preview}\n"
                message += "\n💡 *Напишите номер сна для подробного просмотра*"
                
                context.user_data['dreams_history'] = dreams[:5]
            else:
                message = "📝 У вас пока нет записанных снов"
        else:
            message = f"❌ Ошибка загрузки истории (код: {response.status_code})"
            
    except Exception as e:
        logger.error(f"Ошибка в history: {e}")
        message = "❌ Сервер недоступен"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def last_dream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает последний сон пользователя"""
    user_id = update.message.from_user.id
    
    await update.message.chat.send_action(action="typing")
    
    try:
        url = f"{LAST_DREAM_URL}?user_id={user_id}"
        logger.info(f"📤 GET запрос на {url}")
        
        response = requests.get(url, timeout=10)
        logger.info(f"📥 Статус: {response.status_code}")
        
        if response.status_code == 200:
            dream = response.json()
            if dream:
                message = f"""🔮 *Ваш последний сон*

*📅 Дата:* {dream.get('created_at', '')[:10]}
*💭 Сон:* {dream.get('text', '')}

*✨ Интерпретация:*
{dream.get('interpretation', 'Нет интерпретации')}"""
            else:
                message = "📝 У вас пока нет записанных снов"
        else:
            message = f"❌ Ошибка загрузки (код: {response.status_code})"
            
    except Exception as e:
        logger.error(f"Ошибка в last_dream: {e}")
        message = "❌ Сервер недоступен"
    
    await update.message.reply_text(message, parse_mode='Markdown')

# ============================================
# ОБРАБОТЧИК ГОЛОСОВЫХ СООБЩЕНИЙ
# ============================================
def escape_markdown(text):
    """Экранирует спецсимволы для Telegram Markdown"""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка голосовых сообщений"""
    user_id = update.message.from_user.id
    voice = update.message.voice
    
    logger.info(f"Получено голосовое от пользователя {user_id}")
    
    await update.message.chat.send_action(action="typing")
    
    status_message = await update.message.reply_text(
        "🎤 Обрабатываю ваше голосовое сообщение..."
    )
    
    try:
        audio_path = await voice_processor.download_voice_file(voice, user_id)
        
        if not audio_path:
            await status_message.edit_text("❌ Не удалось скачать голосовое сообщение")
            return
        
        await status_message.edit_text("🔍 Распознаю речь...")
        text = voice_processor.speech_to_text(audio_path)
        
        if not text or text == "Не удалось распознать речь":
            await status_message.edit_text(
                "❌ Не удалось распознать речь.\n\n"
                "Попробуйте:\n"
                "• Говорить четче и громче\n"
                "• Отправить текст сообщением\n"
                "• Записать в тихом месте"
            )
            voice_processor.cleanup(audio_path)
            return
        
        await status_message.edit_text(
            f"✅ Распознано:\n\n{text}\n\n📝 Отправляю на анализ нейросети..."
        )
        
        # --- ИСПОЛЬЗУЕМ requests ВМЕСТО aiohttp ---
        try:
            logger.info(f"📤 Отправка POST на {DJANGO_API_URL}")
            response = requests.post(
                DJANGO_API_URL,
                json={'user_id': user_id, 'text': text},
                timeout=30
            )
            logger.info(f"📥 Статус ответа: {response.status_code}")
            logger.info(f"📥 Тело ответа (первые 200 символов): {response.text[:200]}...")
            
            if response.status_code == 200:
                result = response.json()
                interpretation = result.get('interpretation', 'Анализ не получен')
                
                # Отправляем результат (без Markdown)
                await update.message.reply_text(
                    f"✨ Анализ голосового сна завершен!\n\n"
                    f"🎤 Распознанный текст:\n{text}\n\n"
                    f"🔮 Интерпретация:\n{interpretation}"
                )
                
                await status_message.delete()
                logger.info(f"✅ Голосовой сон от {user_id} успешно обработан")
            else:
                logger.error(f"❌ Ошибка API: статус {response.status_code}")
                await status_message.edit_text(
                    f"❌ Ошибка анализа сна (код: {response.status_code})"
                )
                
        except requests.exceptions.Timeout:
            logger.error("❌ Таймаут запроса к Django")
            await status_message.edit_text(
                "❌ Сервер не отвечает. Попробуйте позже."
            )
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ Ошибка подключения: {e}")
            await status_message.edit_text(
                "❌ Не удалось подключиться к серверу. Проверьте, что Django запущен."
            )
        except Exception as e:
            logger.error(f"❌ Ошибка при запросе: {e}")
            await status_message.edit_text(
                "❌ Ошибка при обработке сна. Попробуйте позже."
            )
            
    except Exception as e:
        logger.error(f"Ошибка обработки голосового: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ Произошла ошибка при обработке голосового сообщения\n\n"
            "Попробуйте отправить сон текстом."
        )
        await status_message.delete()
        
    finally:
        if 'audio_path' in locals():
            voice_processor.cleanup(audio_path)

# ============================================
# ОБРАБОТЧИК ТЕКСТОВЫХ СООБЩЕНИЙ
# ============================================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    user_id = update.message.from_user.id
    text = update.message.text

    logger.info(f"Получено сообщение от {user_id}: {text[:50]}...")

    # Обработка кнопок (оставляем без изменений)
    if text == "📝 Записать сон":
        await update.message.reply_text("📝 Опишите ваш сон...")
        return
        
    elif text == "🎤 Голосовой ввод":
        await update.message.reply_text(
            "🎤 *Отправьте голосовое сообщение с описанием сна*\n\n"
            "*Советы:*\n"
            "• Говорите четко и не слишком быстро\n"
            "• Записывайте в тихом месте\n"
            "• Описывайте детали\n\n"
            "Или просто нажмите на иконку микрофона в Telegram",
            parse_mode='Markdown'
        )
        return
        
    elif text == "📖 История снов":
        await history(update, context)
        return
        
    elif text == "🔮 Последний сон":
        await last_dream(update, context)
        return
        
    elif text == "ℹ️ Помощь":
        await help_command(update, context)
        return
        
    elif text == "🌐 Веб-приложение":  
        await web_version(update, context)
        return
    
    # Проверка на ввод номера сна из истории
    if text.isdigit() and context.user_data.get('dreams_history'):
        dream_number = int(text)
        dreams_history = context.user_data['dreams_history']
        
        if 1 <= dream_number <= len(dreams_history):
            dream = dreams_history[dream_number - 1]
            
            await update.message.reply_text(
                f"🔍 *Сон #{dream_number}*\n\n"
                f"📅 {dream.get('created_at', '')[:10]}\n"
                f"💭 {dream.get('text', 'Текст отсутствует')}\n\n"
                f"✨ Интерпретация:\n{dream.get('interpretation', 'Нет интерпретации')}",
                parse_mode='Markdown'
            )
            return
    
    # Если это описание сна — используем синхронный requests
    await update.message.chat.send_action(action="typing")
    
    try:
        logger.info(f"📤 Отправка POST запроса на {DJANGO_API_URL}")
        logger.info(f"📦 Данные: user_id={user_id}, text={text[:50]}...")
        
        # СИНХРОННЫЙ ЗАПРОС (вместо aiohttp)
        response = requests.post(
            DJANGO_API_URL,
            json={'user_id': user_id, 'text': text},
            timeout=30
        )
        
        logger.info(f"📥 Статус ответа: {response.status_code}")
        logger.info(f"📥 Тело ответа (первые 200 символов): {response.text[:200]}...")
        
        if response.status_code == 200:
            try:
                result = response.json()
                interpretation = result.get('interpretation', 'Анализ не получен')
                
                # Проверяем, что интерпретация не пустая
                if interpretation and interpretation != "Анализ не получен":
                    await update.message.reply_text(
                        f"✨ *Анализ завершен!*\n\n{interpretation}",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text(
                        "⚠️ *Анализ получен, но интерпретация отсутствует*\n\n"
                        "Попробуйте описать сон подробнее.",
                        parse_mode='Markdown'
                    )
            except ValueError as e:
                logger.error(f"❌ Ошибка парсинга JSON: {e}")
                logger.error(f"📝 Ответ: {response.text[:500]}")
                await update.message.reply_text(
                    "❌ *Ошибка обработки ответа от сервера*\n\n"
                    "Попробуйте позже.",
                    parse_mode='Markdown'
                )
        else:
            logger.error(f"❌ Ошибка API: статус {response.status_code}")
            logger.error(f"📝 Ответ: {response.text[:500]}")
            
            await update.message.reply_text(
                f"❌ *Ошибка анализа сна*\n\n"
                f"Код ошибки: {response.status_code}\n"
                f"Попробуйте позже или опишите сон подробнее.",
                parse_mode='Markdown'
            )
            
    except requests.exceptions.ConnectionError as e:
        logger.error(f"❌ Сетевая ошибка: {e}")
        await update.message.reply_text(
            "❌ *Сетевая ошибка*\n\n"
            "Не удалось подключиться к серверу. Проверьте, что Django запущен.",
            parse_mode='Markdown'
        )
        
    except requests.exceptions.Timeout:
        logger.error(f"❌ Таймаут запроса")
        await update.message.reply_text(
            "❌ *Сервер не отвечает*\n\n"
            "Превышено время ожидания. Попробуйте позже.",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_message: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ *Внутренняя ошибка*\n\n"
            "Произошла непредвиденная ошибка. Попробуйте позже.",
            parse_mode='Markdown'
        )

# ============================================
# ЗАПУСК БОТА
# ============================================
def main():
    """Главная функция запуска бота"""
    app = Application.builder().token(BOT_TOKEN).build()

    # Обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CommandHandler("last", last_dream))

    # Обработчики сообщений
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🤖 Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()
