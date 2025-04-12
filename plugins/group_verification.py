import json
import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from Vps import app
from config import REQ_CHANNEL  # Make sure to define this in config.py

# Load approved group IDs from file
APPROVED_FILE = "approved_groups.json"
approved_groups = set()

if os.path.exists(APPROVED_FILE):
    with open(APPROVED_FILE, "r") as f:
        try:
            approved_groups = set(json.load(f))
        except Exception:
            approved_groups = set()

def save_groups():
    with open(APPROVED_FILE, "w") as f:
        json.dump(list(approved_groups), f)


@app.on_message(filters.new_chat_members)
async def handle_new_group(client: Client, message: Message):
    for member in message.new_chat_members:
        if member.id == (await client.get_me()).id:
            chat_id = message.chat.id
            chat_title = message.chat.title
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Approve", callback_data=f"approve_{chat_id}")],
                [InlineKeyboardButton("❌ Reject", callback_data=f"reject_{chat_id}")]
            ])
            text = (
                "🆕 <b>New Group Added</b>\n\n"
                f"<b>Group Name:</b> {chat_title}\n"
                f"<b>Group ID:</b> <code>{chat_id}</code>"
            )
            await client.send_message(REQ_CHANNEL, text, reply_markup=buttons)


@app.on_callback_query(filters.regex("^(approve|reject)_"))
async def handle_group_verification(client: Client, query: CallbackQuery):
    action, group_id = query.data.split("_")
    group_id = int(group_id)

    if action == "approve":
        approved_groups.add(group_id)
        save_groups()
        await query.edit_message_text(f"✅ Group <code>{group_id}</code> approved.")
        await query.answer("Approved.")
    else:
        await query.edit_message_text(f"❌ Group <code>{group_id}</code> rejected.")
        await query.answer("Rejected.")


@app.on_message(filters.group & filters.command(["start", "help", "id", "alive"]))
async def verify_group_commands(client: Client, message: Message):
    if message.chat.id not in approved_groups:
        await message.reply("⛔ This group is not approved to use this bot. Please wait for manual approval.")
        return
    # Allow actual command functionality here if needed
    await message.reply("✅ This group is approved to use the bot!")
