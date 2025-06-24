import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

# --- ВАШИ ДАННЫЕ (как и в прошлый раз) ---
BOT_TOKEN = '7693222286:AAEYgYzbn_Jiwxmc1kUSoqzaq7auRru1No8'
ADMIN_CHAT_ID = 5642066382 # Ваш Chat ID

# --- Настройка логирования, чтобы видеть ошибки в консоли ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- ЛОГИКА БОТА ---

# Команда /start - приветствие
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"Привет, {user_name}! 👋\n\n"
        "Я помогу Глазу собрать все фотографии в одном месте.\n\n"
        "Просто отправьте мне ваши лучшие фото, видео или другие файлы. Я всё бережно сохраню и перешлю ему."
    )

# Универсальный обработчик для всех файлов
async def handle_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user = update.effective_user
    
    # Пытаемся переслать сообщение
    try:
        await message.forward(chat_id=ADMIN_CHAT_ID)
        
        # Если пересылка удалась, отвечаем пользователю
        await message.reply_text(
            "Отлично, файл получен и переслан! 👍\n"
            "Если хотите отправить что-то еще, просто пришлите следующий файл."
        )
        logger.info(f"Файл от {user.full_name} (@{user.username}) успешно переслан.")

    # Ловим ошибку, если что-то пошло не так
    except TelegramError as e:
        logger.error(f"Не удалось переслать файл от {user.full_name}. Ошибка: {e}")
        # Сообщаем пользователю о проблеме
        await message.reply_text(
            "🚫 Произошла ошибка при пересылке вашего файла.\n\n"
            "Пожалуйста, попробуйте отправить его еще раз через пару минут. "
            "Если проблема повторится, свяжитесь с глазом."
        )

# Функция для ответа на обычный текст, чтобы пользователь не терялся
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Я умею работать только с файлами. Пожалуйста, отправьте мне фото, видео или документ."
    )

# Главная функция для запуска бота
def main():
    print("Бот запускается...")
    application = Application.builder().token(BOT_TOKEN).build()

    # ИСПРАВЛЕННАЯ СТРОКА: Фильтры для всех типов медиафайлов
    # Названия фильтров теперь с заглавной буквы
    media_filters = (
        filters.PHOTO | filters.VIDEO | filters.AUDIO | 
        filters.Document.ALL | filters.VOICE | filters.VIDEO_NOTE
    )

    # Добавляем обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(media_filters, handle_files))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("Бот запущен и готов к работе!")
    application.run_polling()

if __name__ == '__main__':
    main()