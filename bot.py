import os
import httpx

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
HF_TOKEN = os.getenv("HF_TOKEN")

MODEL = "Qwen/Qwen2.5-7B-Instruct"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Salom! Men Aieshonbekov AI.\n\n"
        "Savolingizni yozing — yordam beraman. 🚀"
    )


async def ask_ai(user_text: str) -> str:
    url = "https://router.huggingface.co/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Aieshonbekov AI, a helpful Telegram AI assistant. "
                    "Answer naturally and clearly. "
                    "If the user writes Uzbek, answer in Uzbek."
                ),
            },
            {
                "role": "user",
                "content": user_text,
            },
        ],
        "max_tokens": 1000,
        "temperature": 0.7,
    }

    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.post(
            url,
            headers=headers,
            json=payload,
        )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]


async def message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text.strip()

    await update.message.chat.send_action(
        action=ChatAction.TYPING
    )

    try:
        answer = await ask_ai(user_text)

        await update.message.reply_text(
            answer,
            disable_web_page_preview=True,
        )

    except Exception as error:
        print("AI ERROR:", error)

        await update.message.reply_text(
            "❌ Afsus, hozir AI javob bera olmadi.\n"
            "Birozdan keyin yana urinib ko‘ring."
        )


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN mavjud emas!")

    if not HF_TOKEN:
        raise RuntimeError("HF_TOKEN mavjud emas!")

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

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
