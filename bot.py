from telethon import TelegramClient, events
from telethon.tl.types import ChatBannedRights
import asyncio
import json
from datetime import datetime

api_id = 123456
api_hash = "API_HASH"
bot_token = "BOT_TOKEN"

OWNER_ID = 111111111  # مالك البوت الأساسي AX

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

ranks = {}
banned = {}
muted = {}
replies = {}
warnings = {}
messages = {}

def save(file,data):
    with open(file,"w") as f:
        json.dump(data,f)

def load(file):
    try:
        with open(file) as f:
            return json.load(f)
    except:
        return {}

ranks = load("ranks.json")
banned = load("banned.json")
muted = load("muted.json")
replies = load("replies.json")
warnings = load("warn.json")
messages = load("messages.json")

def rank_name(user):

    if str(user) == str(OWNER_ID):
        return "مالك البوت AX"

    if str(user) in ranks:
        return ranks[str(user)]

    return "عضو"

@client.on(events.NewMessage(pattern="الاوامر"))
async def commands(event):

    text = """
📜 اوامر البوت

معلومات
ايدي
ايدي القروب
معلوماتي

الرتب
رفع ادمن
تنزيل ادمن
رفع مشرف
تنزيل مشرف
رفع مدير
تنزيل مدير

العقوبات
حظر
الغاء الحظر
كتم
الغاء الكتم
طرد

التفاعل
توب المتفاعلين

الردود
اضف رد
حذف رد
الردود

الترحيب
تفعيل الترحيب
تعطيل الترحيب
وضع ترحيب

الحماية
قفل الروابط
فتح الروابط
قفل الصور
فتح الصور
"""

    await event.reply(text)

@client.on(events.NewMessage(pattern="ايدي"))
async def myid(event):
    await event.reply(f"🆔 ايديك: {event.sender_id}")

@client.on(events.NewMessage(pattern="ايدي القروب"))
async def gid(event):
    await event.reply(f"🆔 ايدي القروب: {event.chat_id}")

@client.on(events.NewMessage(pattern="معلوماتي"))
async def info(event):

    rank = rank_name(event.sender_id)

    text = f"""
👤 معلوماتك

الايدي : {event.sender_id}
الرتبة : {rank}
"""

    await event.reply(text)

@client.on(events.NewMessage(pattern="رفع ادمن"))
async def promote(event):

    if event.sender_id != OWNER_ID:
        return

    if not event.is_reply:
        return await event.reply("رد على الشخص")

    user = await event.get_reply_message()

    ranks[str(user.sender_id)] = "ادمن"

    save("ranks.json",ranks)

    await event.reply("تم رفعه ادمن")

@client.on(events.NewMessage(pattern="تنزيل ادمن"))
async def demote(event):

    if event.sender_id != OWNER_ID:
        return

    if not event.is_reply:
        return

    user = await event.get_reply_message()

    if str(user.sender_id) in ranks:
        del ranks[str(user.sender_id)]

    save("ranks.json",ranks)

    await event.reply("تم تنزيله")

@client.on(events.NewMessage(pattern="حظر"))
async def ban(event):

    if not event.is_reply:
        return

    user = await event.get_reply_message()

    banned[str(user.sender_id)] = True

    save("banned.json",banned)

    rights = ChatBannedRights(
        until_date=None,
        view_messages=True
    )

    await client.edit_permissions(event.chat_id,user.sender_id,rights)

    await event.reply("🚫 تم حظره")

@client.on(events.NewMessage(pattern="الغاء الحظر"))
async def unban(event):

    if not event.is_reply:
        return

    user = await event.get_reply_message()

    if str(user.sender_id) in banned:
        del banned[str(user.sender_id)]

    save("banned.json",banned)

    await client.edit_permissions(event.chat_id,user.sender_id,None)

    await event.reply("✅ تم الغاء الحظر")

@client.on(events.NewMessage(pattern="كتم"))
async def mute(event):

    if not event.is_reply:
        return

    user = await event.get_reply_message()

    muted[str(user.sender_id)] = True

    save("muted.json",muted)

    rights = ChatBannedRights(
        until_date=None,
        send_messages=True
    )

    await client.edit_permissions(event.chat_id,user.sender_id,rights)

    await event.reply("🔇 تم كتمه")

@client.on(events.NewMessage(pattern="الغاء الكتم"))
async def unmute(event):

    if not event.is_reply:
        return

    user = await event.get_reply_message()

    if str(user.sender_id) in muted:
        del muted[str(user.sender_id)]

    save("muted.json",muted)

    await client.edit_permissions(event.chat_id,user.sender_id,None)

    await event.reply("🔊 تم الغاء الكتم")

@client.on(events.NewMessage)
async def auto_reply(event):

    msg = event.raw_text

    if msg in replies:

        await event.reply(replies[msg])

@client.on(events.NewMessage(pattern="اضف رد"))
async def add_reply(event):

    if event.sender_id != OWNER_ID:
        return

    try:
        txt = event.raw_text.split(" ",2)

        trigger = txt[1]
        response = txt[2]

        replies[trigger] = response

        save("replies.json",replies)

        await event.reply("تم حفظ الرد")

    except:
        await event.reply("اكتب: اضف رد الكلمة الرد")

@client.on(events.NewMessage(pattern="الردود"))
async def list_replies(event):

    if not replies:
        return await event.reply("لا يوجد ردود")

    text="📂 الردود\n\n"

    for r in replies:
        text += f"- {r}\n"

    await event.reply(text)

@client.on(events.NewMessage)
async def count_messages(event):

    uid = str(event.sender_id)

    if uid not in messages:
        messages[uid] = 0

    messages[uid] += 1

    save("messages.json",messages)

@client.on(events.NewMessage(pattern="توب المتفاعلين"))
async def top(event):

    top_users = sorted(messages.items(),key=lambda x:x[1],reverse=True)[:10]

    text="🏆 توب المتفاعلين\n\n"

    for i,u in enumerate(top_users,1):
        text += f"{i}- {u[0]} | {u[1]} رسالة\n"

    await event.reply(text)

print("BOT STARTED")

client.run_until_disconnected()
