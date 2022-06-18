from VOID import System, session
from VOID.strings import scan_request_string, reject_string, check_ban_string

from telethon import events, custom

import re
import asyncio

data = []
DATA_LOCK = asyncio.Lock()


async def get_message_paste(message: str):
    async with session.post(
        "https://nekobin.com/api/documents", json={"content": message}
    ) as r:
        paste = f"https://nekobin.com/{(await r.json())['result']['key']}"
    return paste


def can_ban(event):
    status = False
    if event.chat.admin_rights:
        status = event.chat.admin_rights.ban_users
    return status


@System.bot.on(events.NewMessage(pattern="[/!?]start"))
async def sup(event):
    await event.reply("ɪ ᴀᴍ ʀᴇᴀᴅʏ ᴛᴏ ꜱᴇɴᴅ ᴘᴜɴᴋꜱ ɪɴ ɪɴꜰɪɴɪᴛᴇ ᴠᴏɪᴅ [🤞](https://telegra.ph/file/693871aaf0f8e81573d68.png)")


@System.bot.on(events.NewMessage(pattern="[/!?]vhelp"))
async def help(event):
    if not event.is_private:
        return
    await event.reply("""
Add this bot to any group and It will warn/ban If any gbanned user joins.
**Commands:**
    `help` - This text.
    `start` - Start the bot.
    `alertmode` - Change alertmode.
        **Available modes:**
        `silent-ban` - Silently ban user.
        `ban` - Ban and send a message In the chat to say the user was banned.
        `warn` - Warn that a gbanned user has joined but do nothing.
All commands can be used with ! , / or ?""")


@System.bot.on(events.CallbackQuery(pattern=r"(approve|reject)_(\d*)"))
async def callback_handler(event):
    split = event.data.decode().split("_", 1)
    index = int(split[1])
    message = await event.get_message()
    async with DATA_LOCK:
        try:
            dict_ = data[index]
        except IndexError:
            dict_ = None
    if not dict_:
        await event.answer(
            "Message is too old (Bot was restarted after message was sent), Use /approve on it instead",
            alert=True,
        )
        return
    await event.answer(
        "I have sent you a message, Reply to it to overwrite reason/specify reject reason, Otherwise ignore",
        alert=True,
    )
    sender = await event.get_sender()
    async with event.client.conversation(sender.id, timeout=15) as conv:
        if split[0] == "approve":
            await conv.send_message(
                "You approved a scan it seems, Would you like to overwrite reason?"
            )
        else:
            await conv.send_message(
                "You rejected a scan it seems, Would you like to give rejection reason?"
            )
        try:
            r = await conv.get_response()
        except asyncio.exceptions.TimeoutError:
            r = None
    if r:
        if split[0] == "approve":
            async with DATA_LOCK:
                dict_["reason"] = r.message
                data[index] = dict_
            msg = f"New Reason:\nU_ID: {dict_['u_id']}\n"
            msg += f"Enforcer: {dict_['enforcer']}\n"
            msg += f"Source: {dict_['source']}\n"
            msg += f"Reason: {dict_['reason']}\n"
            msg += f"Message: {dict_['message']}\n"
            await event.respond(msg)
            await message.edit(
                re.sub(
                    "(\*\*)?(Scan)? ?Reason:(\*\*)? (`([^`]*)`|.*)",
                    f"**Scan Reason:** {r.message}",
                    message.message,
                )
            )
        else:
            await message.edit(reject_string)
            async with DATA_LOCK:
                del data[index]
    else:
        await event.respond("no respond, bye bye")


@System.bot.on(events.InlineQuery)
async def inline_handler(event):
    builder = event.builder
    query = event.text
    split = query.split(" ", 1)
    if query.startswith("check"):
        if len(split) == 1:
            result = builder.article(
                "Type User-ID", text="No User was provided")
        else:
            user_id: int = None
            try:
                user_id = int(split[1])
            except:
                try:
                    user_id = (await System.get_entity(split[1])).id
                except BaseException:
                    result = builder.article(
                        "User Not Found", text="I haven't interacted with this user yet")
            if user_id:
                try:
                    c_user = apiClient.get_ban(user_id)
                    btn = []
                    if c_user.message:
                        btn = buttons = [custom.Button.url("Message", (await get_message_paste(c_user.message)))]
                    result = builder.article("Banned User", text=check_ban_string.format(
                        user_id=c_user.id, reason=c_user.reason, date=c_user.date, timestamp=c_user.timestamp), buttons=btn)
                except:
                    result = builder.article(
                        "User Not Banned", text="This user isn't banned!")
                pass
    elif query.startswith("builder"):
        split = query.replace("builder", "").split(":::", 4)
        print(split)
        if len(split) != 5:
            result = builder.article("Not enough info provided...")
        else:
            u_id, enforcer, source, reason, message = split
            dict_ = {
                "u_id": u_id,
                "enforcer": enforcer,
                "source": source,
                "reason": reason,
                "message": message,
            }
            print(dict_)
            async with DATA_LOCK:
                data.append(dict_)
                index = data.index(dict_)
            buttons = [
                custom.Button.inline("Approve", data=f"approve_{index}"),
                custom.Button.inline("Reject", data=f"reject_{index}"),
            ]
            result = builder.article(
                "Output",
                text=scan_request_string.format(
                    enforcer=enforcer,
                    spammer=u_id,
                    reason=reason,
                    chat=source,
                    message=message,
                ),
                buttons=buttons,
            )

    else:
        result = builder.article(
            "No type provided",
            text="Use check user_id\nbuilder id:::enforcer:::source:::reason:::message",
        )
    await event.answer([result])
