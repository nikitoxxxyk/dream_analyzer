import os
import tempfile
import speech_recognition as sr
from pydub import AudioSegment
import requests
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class VoiceProcessor:
    def __init__(self, temp_dir="temp_audio"):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.recognizer = sr.Recognizer()
    
    async def download_voice_file(self, voice_file, user_id):
        """Скачивает голосовое сообщение из Telegram"""
        try:
            # Получаем файл из Telegram
            file = await voice_file.get_file()
            
            # Создаем временный файл
            temp_path = self.temp_dir / f"{user_id}_{voice_file.file_id}.ogg"
            
            # Скачиваем
            await file.download_to_drive(temp_path)
            
            logger.info(f"Голосовое скачано: {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"Ошибка скачивания голосового: {e}")
            return None
    
    def convert_ogg_to_wav(self, ogg_path):
        """Конвертирует .ogg в .wav для распознавания"""
        try:
            wav_path = ogg_path.with_suffix('.wav')
            
            # Конвертация через pydub
            audio = AudioSegment.from_ogg(ogg_path)
            
            # Устанавливаем параметры для лучшего распознавания
            audio = audio.set_frame_rate(16000)
            audio = audio.set_channels(1)
            
            audio.export(wav_path, format="wav", parameters=["-ac", "1", "-ar", "16000"])
            
            logger.info(f"Конвертировано в WAV: {wav_path}")
            return wav_path
            
        except Exception as e:
            logger.error(f"Ошибка конвертации: {e}")
            # Пробуем через ffmpeg напрямую
            return self._convert_with_ffmpeg(ogg_path)
    
    def _convert_with_ffmpeg(self, ogg_path):
        """Альтернативная конвертация через ffmpeg"""
        try:
            wav_path = ogg_path.with_suffix('.wav')
            
            import subprocess
            subprocess.run([
                'ffmpeg', '-i', str(ogg_path),
                '-acodec', 'pcm_s16le',
                '-ac', '1',
                '-ar', '16000',
                '-y', str(wav_path)
            ], check=True, capture_output=True)
            
            return wav_path
        except Exception as e:
            logger.error(f"Ошибка ffmpeg: {e}")
            return None
    
    def speech_to_text(self, audio_path, language="ru-RU"):
        """Преобразует речь в текст"""
        try:
            # Конвертируем если нужно
            if audio_path.suffix == '.ogg':
                audio_path = self.convert_ogg_to_wav(audio_path)
                if not audio_path:
                    return None
            
            # Распознаем речь
            with sr.AudioFile(str(audio_path)) as source:
                # Убираем шум
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Записываем аудио
                audio_data = self.recognizer.record(source)
                
                # Используем Google Speech Recognition (бесплатно)
                try:
                    text = self.recognizer.recognize_google(
                        audio_data, 
                        language=language
                    )
                    logger.info(f"Распознано: {text[:50]}...")
                    return text
                    
                except sr.UnknownValueError:
                    logger.warning("Речь не распознана")
                    return "Не удалось распознать речь. Попробуйте говорить четче."
                    
                except sr.RequestError as e:
                    logger.error(f"Ошибка API: {e}")
                    # Пробуем через Yandex SpeechKit (если настроен)
                    return self._recognize_with_yandex(audio_path, language)
                    
        except Exception as e:
            logger.error(f"Ошибка распознавания: {e}")
            return None
    
    def _recognize_with_yandex(self, audio_path, language):
        """Распознавание через Yandex SpeechKit (нужен API ключ)"""
        # Если у вас есть Yandex Cloud API ключ
        yandex_api_key = os.getenv('YANDEX_SPEECHKIT_KEY')
        
        if not yandex_api_key:
            return "Ошибка распознавания. Пожалуйста, отправьте текст."
        
        try:
            with open(audio_path, 'rb') as audio_file:
                response = requests.post(
                    'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize',
                    headers={
                        'Authorization': f'Api-Key {yandex_api_key}',
                    },
                    params={
                        'lang': language,
                        'sampleRateHertz': 16000,
                    },
                    data=audio_file.read()
                )
                
                if response.status_code == 200:
                    return response.json().get('result', '')
                else:
                    return f"Ошибка Yandex: {response.status_code}"
                    
        except Exception as e:
            logger.error(f"Ошибка Yandex: {e}")
            return "Ошибка распознавания"
    
    def cleanup(self, *file_paths):
        """Очищает временные файлы"""
        for file_path in file_paths:
            if file_path and file_path.exists():
                try:
                    file_path.unlink()
                    logger.debug(f"Удален файл: {file_path}")
                except:
                    pass

# Синглтон
voice_processor = VoiceProcessor()