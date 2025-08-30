#!/usr/bin/env python
from telegram.ext import Application, MessageHandler, filters
import requests, re

def resolve_share_google(url: str) -> str:
    """Dada una URL de share.google, devuelve la URL final."""
    r = requests.get(url, allow_redirects=True, timeout=10)
    return r.url

async def handle_message(update, context):
    text = update.message.text
    # buscar todas las URLs de share.google en el mensaje
    urls = re.findall(r'https?://share\.google/\S+', text)
    if urls:
        cleaned_text = text
        # sustituir cada URL por su destino final
        for u in urls:
            try:
                final_url = resolve_share_google(u)
                cleaned_text = cleaned_text.replace(u, final_url)
            except Exception:
                cleaned_text = cleaned_text.replace(u, f"[error resolviendo {u}]")

        chat_type = update.effective_chat.type
        if chat_type in ["group", "supergroup"]:
            origin_name = update.message.sender_chat.title if hasattr(update.message, 'sender_chat') else "Group"
            if origin_name == "Group" and getattr(update.message.sender_chat, "username", None):
                origin_name = f"@{update.message.sender_chat.username}"
            message_text = f"🔗 Enlace limpio compartido por {origin_name}:\n{cleaned_text}"

            # borrar el mensaje original con la URL sucia
            try:
                await update.message.delete()
            except Exception as e:
                print(f"No pude borrar el mensaje: {e}")
        else:
            # chat privado
            message_text = f"🔗 Enlace limpio:\n{cleaned_text}"

        # enviar el mensaje limpio
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)

app = Application.builder().token("TOKEN_AQUI").build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()

