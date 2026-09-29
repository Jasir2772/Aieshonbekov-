import os
from groq import Groq

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODEL = "llama-3.3-70b-versatile"

client = Groq(api_key=GROQ_API_KEY)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Salom! Men Aieshonbekov AI.\n\n"
        "Savolingizni yozing — yordam beraman. 🚀"
    )


async def ask_ai(user_text: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Aieshonbekov AI, a helpful Telegram AI assistant. "
                    "Answer clearly and naturally. "
                    "If the user writes Uzbek, answer in Uzbek."
                ),
            },
            {
                "role": "user",
                "content": user_text,
            },
        ],
        temperature=0.7,
        max_tokens=1000,
    )

    return response.choices[0].message.content


async def message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    await update.message.chat.send_action(
        action=ChatAction.TYPING
    )

    try:
        answer = await ask_ai(text)
        await update.message.reply_text(answer)

    except Exception as error:
        print("ERROR:", error)

        await update.message.reply_text(
            "❌ Hozir AI javob bera olmadi. "
            "Birozdan keyin yana urinib ko‘ring."
        )


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN topilmadi!")

    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY topilmadi!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler,
        )
    )

    print("🚀 Aieshonbekov AI ishga tushdi!")

    app.run_polling()


if __name__ == "__main__":
    main()
