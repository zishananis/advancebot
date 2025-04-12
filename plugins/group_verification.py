from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from Vps import app  # Adjust import as per your main bot instance
from config import REQ_CHANNEL

approved_groups = set()  # In-memory, ideally should be a DB or file

@app.on_message(filters.new_chat_members)
async def handle_new_group(client: Client, message: Message):
    for member in message.new_chat_members:
        if member.id == (await client.get_me()).id:
            chat_id = message.chat.id
            chat_title = message.chat.title
            btn = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Approve", callback_data=f"approve_{chat_id}")],
                [InlineKeyboardButton("❌ Reject", callback_data=f"reject_{chat_id}")]
            ])
            text = f"🆕 <b>New Group Added</b>\n\n<b>Group Name:</b> {chat_title}\n<b>ID:</b> <code>{chat_id}</code>"
            await client.send_message(REQ_CHANNEL, text, reply_markup=btn)
