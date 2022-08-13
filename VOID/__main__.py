from VOID.plugins import to_load
from VOID import (
    System,
    system_cmd,
    INSPECTORS,
    ENFORCERS,
    Sibyl_logs,
)
from VOID.strings import on_string, shtart_string
from telethon import events, custom, Button
import logging
import importlib
import asyncio
import time

INFOPIC = "https://telegra.ph/file/95f9d0b2854218dc42a53.jpg"
VOID_IMG = "https://telegra.ph/file/720bbed1c8c67ae973cfa.jpg"
START_IMG = "https://telegra.ph/file/8da5a311bc80410bee59c.jpg"
NINFO = "https://telegra.ph/file/0d4386d2d18d0c0bbf027.jpg"
IINFO = "https://telegra.ph/file/9a878eaec44d8963a7d69.jpg"

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=logging.WARNING
)


HELP = {}
IMPORTED = {}
FAILED_TO_LOAD = {}

for load in to_load:
    try:
        imported = importlib.import_module("VOID.plugins." + load)
        if not hasattr(imported, "__plugin_name__"):
            imported.__plugin_name__ = imported.__name__

        if not imported.__plugin_name__.lower() in IMPORTED:
            IMPORTED[imported.__plugin_name__.lower()] = imported

        if hasattr(imported, "help_plus") and imported.help_plus:
            HELP[imported.__plugin_name__.lower()] = imported
    except Exception as e:
        print(f"Error while loading plugin: {load}")
        print("------------------------------------")
        print(e)
        FAILED_TO_LOAD[load] = e
        print("------------------------------------")


@System.on(events.NewMessage(pattern=r"[/|\.|\?|!]vinfo"))
async def status(event):
    msg = await event.reply("۞ ꜱᴇᴀʀᴄʜɪɴɢ ɪɴ ᴅᴀᴛᴀʙᴀꜱᴇ....")
    sender = await event.get_sender()
    user_status = "ɪɴꜱᴘᴇᴄᴛᴏʀ" if sender.id in INSPECTORS else "ᴇɴғᴏʀᴄᴇʀ" if sender.id in ENFORCERS else 'ɴᴏʀᴍᴀʟ ᴜꜱᴇʀ'
    if user_status == 'ɴᴏʀᴍᴀʟ ᴜꜱᴇʀ':
        await System.send_file(event.chat_id, NINFO, caption=on_string.format(Enforcer=user_status, name=sender.first_name))
    if user_status == 'ɪɴꜱᴘᴇᴄᴛᴏʀ':
        await System.send_file(event.chat_id, ɪINFO, caption=on_string.format(Enforcer=user_status, name=sender.first_name))
    else:
        await System.send_file(event.chat_id, INFOPIC, caption=on_string.format(Enforcer=user_status, name=sender.first_name))
    await msg.delete()
    
@System.on(events.NewMessage(pattern=r"[/|\.|\?|!]start"))
async def status(event):
    msg = await event.reply("ꜱᴛᴀʀᴛɪɴɢ ᴠᴏɪᴅ ꜱʏꜱᴛᴇᴍ....")
    sender = await event.get_sender()
    user_status = "ɪɴꜱᴘᴇᴄᴛᴏʀ" if sender.id in INSPECTORS else "ᴇɴғᴏʀᴄᴇʀ" if sender.id in ENFORCERS else 'ɴᴏʀᴍᴀʟ ᴜꜱᴇʀ'
    if user_status == 'ɴᴏʀᴍᴀʟ ᴜꜱᴇʀ':
        await System.send_file(event.chat_id, START_IMG, caption=shtart_string.format(Enforcer=user_status, name=sender.first_name))
    else:
        await System.send_file(event.chat_id, START_IMG, caption=shtart_string.format(Enforcer=user_status, name=sender.first_name))
    await msg.delete()    


@System.on(system_cmd(pattern="vstats"))
async def stats(event):
    msg = f"❂ ᴍᴇꜱꜱᴀɢᴇꜱ ᴘʀᴏᴄᴇꜱꜱᴇᴅ : {System.processed}"
    msg += f"\n\n{len(ENFORCERS)} ᴇɴғᴏʀᴄᴇʀꜱ & {len(INSPECTORS)} ɪɴꜱᴘᴇᴄᴛᴏʀꜱ"
    g = 0
    async for d in event.client.iter_dialogs(limit=None):
        if d.is_channel and not d.entity.broadcast:
            g += 1
        elif d.is_group:
            g += 1
    msg += f"\n\n❂ ᴄᴏɴᴛʀᴏʟʟɪɴɢ : {g} ᴄʜᴀᴛs"
    await event.reply(msg)


@System.on(system_cmd(pattern=r"vhelp", allow_slash=False, allow_enforcer=True))
async def send_help(event):
    try:
        help_for = event.text.split(" ", 1)[1].lower()
    except IndexError:
        msg = "ʟɪꜱᴛ ᴏꜰ ᴘʟᴜɢɪɴꜱ ɪɴ ᴠᴏɪᴅ ꜱʏꜱᴛᴇᴍ :\n\n"
        for x in HELP.keys():
            msg += f"۞ `{x.capitalize()}`\n"
        await event.reply(msg)
        return
    if help_for in HELP:
        await event.reply(HELP[help_for].help_plus)
    else:
        return


async def main():
    try:
        me = await System.bot.get_me()
        System.bot.id = me.id
    except Exception as e:
        FAILED_TO_LOAD["main"] = e
    await System.start()
    await System.catch_up()
    if FAILED_TO_LOAD:
        msg = "Few plugins failed to load:"
        for plugin in FAILED_TO_LOAD:
            msg += f"\n**{plugin}**\n\n`{FAILED_TO_LOAD[plugin]}`"
        await System.send_message(Sibyl_logs, msg)
    else:
         await System.send_file(Sibyl_logs, VOID_IMG, caption="""
ꜱʏꜱᴛᴇᴍ ʙᴇᴄᴀᴍᴇ ᴀᴄᴛɪᴠᴇ
━━━━━━━━━━━━━━━
۞ [ᴠᴏɪᴅ ꜱʏꜱᴛᴇᴍ](t.me/voidsystem)
۞ [ᴠᴏɪᴅ ɴᴇᴛᴡᴏʀᴋ](t.me/voidxnetwork)
━━━━━━━━━━━━━━━
ʙᴏᴛ ʙᴜɪʟᴛ ɪɴ ᴛᴇʟᴇᴛʜᴏɴ.
    
""")
    await System.run_until_disconnected()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
