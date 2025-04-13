import pymongo
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_ID = int(environ.get('API_ID', '25251875'))
API_HASH = environ.get('API_HASH', '9f413b540c859573a91299d252e6e389')
BOT_TOKEN = environ.get('BOT_TOKEN', "8057778876:AAH8j1gFYHgRvi-bsnhf0HQPrAO72NUCipk")
DATABASE_URI = "mongodb+srv://150rs-buy-Barun-dey:150rs-buy-Barun-dey@cluster0.skj2m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
ADMIN_IDS = [7348205141]
LOG_CHANNEL = -1002497411601

# -------------------- DATABASE --------------------
mongo_client = pymongo.MongoClient(DATABASE_URI)
db = mongo_client["VpsBot"]
approved_groups = db.approved_groups

def is_group_approved(group_id: int) -> bool:
    return approved_groups.find_one({"group_id": group_id}) is not None

def add_approved_group(group_id: int):
    if not is_group_approved(group_id):
        approved_groups.insert_one({"group_id": group_id})

# -------------------- BOT CLIENT --------------------
app = Client("strict_group_verifier_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# -------------------- GROUP JOIN HANDLER --------------------
@app.on_my_chat_member()
async def on_group_join(client, message):
    if message.chat.type in ["group", "supergroup"] and message.new_chat_member.status == "member":
        group_id = message.chat.id
        group_name = message.chat.title

        if is_group_approved(group_id):
            return

        approve_button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("✅ Approve Group", callback_data=f"approve:{group_id}")]]
        )

        await client.send_message(
            LOG_CHANNEL,
            f"📢 **New Group Joined**\n\n"
            f"**Group Name:** {group_name}\n"
            f"**Group ID:** `{group_id}`\n\n"
            f"Click the button below to approve this group:",
            reply_markup=approve_button
        )

# -------------------- APPROVAL CALLBACK --------------------
@app.on_callback_query(filters.regex(r"^approve:(-?\d+)$"))
async def approve_callback(client, callback_query):
    user_id = callback_query.from_user.id
    if user_id not in ADMIN_IDS:
        await callback_query.answer("You are not authorized to approve groups.", show_alert=True)
        return

    group_id = int(callback_query.data.split(":")[1])
    add_approved_group(group_id)

    await callback_query.answer("Group approved!", show_alert=True)
    await callback_query.edit_message_text(f"✅ Group `{group_id}` has been approved successfully.")

# -------------------- MESSAGE FILTER: ALLOW ONLY APPROVED GROUPS --------------------
@app.on_message(filters.group)
async def group_message_handler(client, message):
    group_id = message.chat.id

    if not is_group_approved(group_id):
        return  # Silent mode: no response at all

    # Example command
    if message.text and message.text.startswith("/start"):
        await message.reply("✅ This group is approved. Bot is active.")

# -------------------- BOT START --------------------
if __name__ == "__main__":
    print("Bot is running...")
    app.run()
