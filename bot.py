import os
import subprocess
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    mp3_file = "speech.mp3"
    ogg_file = "speech.ogg"

    try:
        # Generate TTS
        subprocess.run([
            "edge-tts",
            "--voice", "km-KH-PisethNeural",
            "--text", text,
            "--write-media", mp3_file
        ], check=True)

        # Convert to Telegram voice format
        subprocess.run([
            "ffmpeg",
            "-y",
            "-i", mp3_file,
            "-c:a", "libopus",
            "-b:a", "32k",
            "-ar", "48000",
            "-ac", "1",
            ogg_file
        ], check=True)

        # Send voice message
        await update.message.reply_voice(
            voice=open(ogg_file, "rb")
        )

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

    finally:
        for f in [mp3_file, ogg_file]:
            if os.path.exists(f):
                os.remove(f)

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()