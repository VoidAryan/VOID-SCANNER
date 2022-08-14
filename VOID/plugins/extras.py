from telethon.utils import resolve_invite_link
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest

from VOID.plugins.Mongo_DB.tree import add_inspector, add_enforcers, get_data
from VOID import ENFORCERS, INSPECTORS, SIBYL, session
from VOID import System, system_cmd
from VOID import Sibyl_logs

from datetime import datetime
from urllib.parse import urlparse, urlunparse
import heroku3
import os
import re
import json

try:
    from VOID import HEROKU_API_KEY, HEROKU_APP_NAME

    heroku_conn = heroku3.from_key(HEROKU_API_KEY)
    app = heroku_conn.app(HEROKU_APP_NAME)
    config = app.config()
    HEROKU = True
except BaseException:
    HEROKU = False

json_file = os.path.join(os.getcwd(), "VOID/elevated_users.json")


@System.on(system_cmd(pattern=r"addenf", allow_inspectors=True))
async def addenf(event) -> None:
    if event.message.reply_to_msg_id:
        replied = await event.get_reply_message()
        if replied:
            u_id = replied.sender.id
        else:
            return
    else:
        u_id = event.text.split(" ", 2)[1]
        try:
            u_id = (await System.get_entity(u_id)).id
        except BaseException:
            await event.reply(
                "I haven't interacted with that user! Meh, Will add them anyway"
            )
    if u_id in ENFORCERS:
        await System.send_message(event.chat_id, "That person is already Enforcer!")
        return
    if HEROKU:
        config["ENFORCERS"] = os.environ.get("ENFORCERS") + " " + str(u_id)
    else:
        with open(json_file, "r") as file:
            data = json.load(file)
        data["ENFORCERS"].append(u_id)
        with open(json_file, "w") as file:
            json.dump(data, file, indent=4)
        await System.send_message(event.chat_id, "Added to enforcers, Restarting 【V๏ɪ፝֟𝔡】•  SᴄᴀɴɴᴇƦ...")
        if not event.from_id.user_id in SIBYL:
            await add_enforcers(event.from_id.user_id, u_id)
        await System.disconnect()
        os.execl(sys.executable, sys.executable, *sys.argv)
        quit()
    if not event.from_id.user_id in SIBYL:
        await add_enforcers(event.from_id.user_id, u_id)
    await System.send_message(
        event.chat_id, f"Added [{u_id}](tg://user?id={u_id}) to Enforcers"
    )


@System.on(system_cmd(pattern=r"rmenf", allow_inspectors=True))
async def rmenf(event) -> None:
    if event.message.reply_to_msg_id:
        replied = await event.get_reply_message()
        u_id = replied.sender.id
    else:
        u_id = event.text.split(" ", 2)[1]
    try:
        u_id = (await System.get_entity(u_id)).id
    except BaseException:
        await event.reply("Invalid ID/Username!")
    u_id = int(u_id)
    if u_id not in ENFORCERS:
        await System.send_message(event.chat_id, "Is that person even a Enforcer?")
        return
    if HEROKU:
        str(u_id)
        ENF = os.environ.get("ENFORCERS")
        if ENF.endswith(u_id):
            config["ENFORCERS"] = ENF.strip(" " + str(u_id))
        elif ENF.startswith(u_id):
            config["ENFORCERS"] = ENF.strip(str(u_id) + " ")
        else:
            config["ENFORCERS"] = ENF.strip(" " + str(u_id) + " ")
    else:
        with open(json_file, "r") as file:
            data = json.load(file)
        data["ENFORCERS"].remove(u_id)
        with open(json_file, "w") as file:
            json.dump(data, file, indent=4)
        await System.send_message(
            event.chat_id, "Removed from enforcers, Restarting..."
        )
        await System.disconnect()
        os.execl(sys.executable, sys.executable, *sys.argv)
        quit()
    await System.send_message(
        event.chat_id, f"Removed [{u_id}](tg://user?id={u_id}) from Enforcers"
    )


@System.on(system_cmd(pattern=r"enforcers", allow_inspectors=True))
async def listuser(event) -> None:
    msg = "Enforcers:\n"
    for z in ENFORCERS:
        try:
            user = await System.get_entity(z)
            msg += f"•[{user.first_name}](tg://user?id={user.id}) | {z}\n"
        except BaseException:
            msg += f"•{z}\n"
    await System.send_message(event.chat_id, msg)


@System.on(system_cmd(pattern=r"join", allow_enforcer=True))
async def join(event) -> None:
    try:
        link = event.text.split(" ", 1)[1]
    except BaseException:
        return
    private = re.match(
        r"(https?://)?(www\.)?t(elegram)?\.(dog|me|org)/joinchat/(.*)", link
    )
    if private:
        await System(ImportChatInviteRequest(private.group(5)))
        await System.send_message(event.chat_id, "Joined chat!")
        await System.send_message(
            Sibyl_logs,
            f"{(await event.get_sender()).first_name} made Iɴꜰɪɴɪᴛᴇ • SᴄᴀɴɴᴇƦ join {private.group(5)}",
        )
    else:
        await System(JoinChannelRequest(link))
        await System.send_message(event.chat_id, "Iɴꜰɪɴɪᴛᴇ • SᴄᴀɴɴᴇƦ Joined chat!")
        await System.send_message(
            Sibyl_logs,
            f"{(await event.get_sender()).first_name} made Iɴꜰɪɴɪᴛᴇ • SᴄᴀɴɴᴇƦ join {link}",
        )


@System.on(system_cmd(pattern=r"addins"))
async def addins(event) -> None:
    if event.reply:
        replied = await event.get_reply_message()
        if replied:
            u_id = replied.sender.id
        else:
            return
    else:
        u_id = event.text.split(" ", 2)[1]
    try:
        u_id = (await System.get_entity(u_id)).id
    except BaseException:
        await event.reply("Ivalid ID/Username!")
        return
    if u_id in INSPECTORS:
        await System.send_message(event.chat_id, "That person is already an Inspector!")
        return
    if HEROKU:
        config["INSPECTORS"] = os.environ.get("INSPECTORS") + " " + str(u_id)
    else:
        with open(json_file, "r") as file:
            data = json.load(file)
        data["INSPECTORS"].append(u_id)
        with open(json_file, "w") as file:
            json.dump(data, file, indent=4)
        await System.send_message(event.chat_id, "Added to Inspectors, Restarting 【V๏ɪ፝֟𝔡】•  SᴄᴀɴɴᴇƦ...")
        await add_inspector(event.from_id.user_id, u_id)
        await System.disconnect()
        os.execl(sys.executable, sys.executable, *sys.argv)
        quit()
    await add_inspector(event.from_id.user_id, u_id)
    await System.send_message(
        event.chat_id, f"Added [{u_id}](tg://user?id={u_id}) to INSPECTORS"
    )


@System.on(system_cmd(pattern=r"rmins"))
async def rmins(event) -> None:
    if event.message.reply_to_msg_id:
        replied = await event.get_reply_message()
        u_id = replied.sender.id
    else:
        u_id = event.text.split(" ", 2)[1]
    try:
        u_id = (await System.get_entity(u_id)).id
    except BaseException:
        await event.reply("Ivalid ID/Username!")
    if u_id not in INSPECTORS:
        await System.send_message(event.chat_id, "Is that person even an Inspector?")
        return
    u_id = str(u_id)
    if HEROKU:
        ENF = os.environ.get("INSPECTORS")
        if ENF.endswith(u_id):
            config["INSPECTORS"] = ENF.strip(" " + str(u_id))
        elif ENF.startswith(u_id):
            config["INSPECTORS"] = ENF.strip(str(u_id) + " ")
        else:
            config["INSPECTORS"] = ENF.strip(" " + str(u_id) + " ")
    else:
        with open(json_file, "r") as file:
            data = json.load(file)
        data["INSPECTORS"].remove(u_id)
        with open(json_file, "w") as file:
            json.dump(data, file, indent=4)
        await System.send_message(
            event.chat_id, "Removed from Inspectors, Restarting..."
        )
        await System.disconnect()
        os.execl(sys.executable, sys.executable, *sys.argv)
        quit()
    await System.send_message(
        event.chat_id,
        f"Removed Inspector status of [{u_id}](tg://user?id={u_id}), Now that user is a mere enforcers.",
    )


@System.on(system_cmd(pattern=r"ainfo ", allow_inspectors=True))
async def info(event) -> None:
    data = (await get_data())["standalone"]
    if not event.text.split(" ", 1)[1] in data.keys():
        return
    u = event.text.split(" ", 1)[1]
    msg = f"User: {u}\n"
    msg += f"Added by: {data[u]['addedby']}\n"
    msg += f"Timestamp: {datetime.fromtimestamp(data[u]['timestamp']).strftime('%d/%m/%Y - %H:%M:%S')}(`{data[u]['timestamp']}`)"
    await event.reply(msg)


@System.on(system_cmd(pattern=r"inspectors", allow_inspectors=True))
async def listuserI(event) -> None:
    msg = "Inspectors:\n"
    for z in INSPECTORS:
        try:
            user = await System.get_entity(z)
            msg += f"•[{user.first_name}](tg://user?id={user.id}) | {z}\n"
        except BaseException:
            msg += f"•{z}\n"
    await System.send_message(event.chat_id, msg)


@System.on(system_cmd(pattern=r"resolve", allow_inspectors=True))
async def resolve(event) -> None:
    try:
        link = event.text.split(" ", 1)[1]
    except BaseException:
        return
    match = re.match(
        r"(https?://)?(www\.)?t(elegram)?\.(dog|me|org)/joinchat/(.*)", link
    )
    if match:
        try:
            data = resolve_invite_link(match.group(5))
        except BaseException:
            await System.send_message(
                event.chat_id, "Couldn't fetch data from that link"
            )
            return
        await System.send_message(
            event.chat_id,
            f"Info from hash {match.group(5)}:\n**Link Creator**: {data[0]}\n**Chat ID**: {data[1]}",
        )


@System.on(system_cmd(pattern=r"leave"))
async def leave(event) -> None:
    try:
        link = event.text.split(" ", 1)[1]
    except BaseException:
        return
    c_id = re.match(r"-(\d+)", link)
    if c_id:
        await System(LeaveChannelRequest(int(c_id.group(0))))
        await System.send_message(
            event.chat_id, f"Iɴꜰɪɴɪᴛᴇ • SᴄᴀɴɴᴇƦ has left chat with id[-{c_id.group(1)}]"
        )
    else:
        await System(LeaveChannelRequest(link))
        await System.send_message(event.chat_id, f"Iɴꜰɪɴɪᴛᴇ • SᴄᴀɴɴᴇƦ has left chat[{link}]")


@System.on(system_cmd(pattern=r"get_redirect ", allow_inspectors=True))
async def redirect(event) -> None:
    try:
        of = event.text.split(" ", 1)[1]
    except BaseException:
        return
    of = urlunparse(urlparse(of, "https"))
    async with session.get(of) as r:
        url = r.url
    await System.send_message(event.chat_id, f"URL: {url}")


help_plus = """
۞  ʜᴇʟᴘ!

→  ᴀᴅᴅᴇɴғ  -  ᴀᴅᴅs  ᴀ  ᴜsᴇʀ  ᴀs  ᴀɴ  ᴇɴғᴏʀᴄᴇʀ.
ғᴏʀᴍᴀᴛ  :  ᴀᴅᴅᴇɴғ  <ᴜsᴇʀ  ɪᴅ  /  ᴀs  ʀᴇᴘʟʏ>

→  ʀᴍᴇɴғ  -  ʀᴇᴍᴏᴠᴇs  ᴀ  ᴜsᴇʀ  ғʀᴏᴍ  ᴇɴғᴏʀᴄᴇʀs.
ғᴏʀᴍᴀᴛ  :  ʀᴍᴇɴғ  <ᴜsᴇʀ  ɪᴅ  /  ᴀs  ʀᴇᴘʟʏ>

→  ᴇɴғᴏʀᴄᴇʀs  -  ʟɪsᴛs  ᴀʟʟ  ᴇɴғᴏʀᴄᴇʀs.

→  ᴀᴅᴅɪɴs  -  ᴀᴅᴅs  ᴀ  ᴜsᴇʀ  ᴀs  ᴀɴ  ɪɴsᴘᴇᴄᴛᴏʀ.
ғᴏʀᴍᴀᴛ  :  ᴀᴅᴅɪɴs  <ᴜsᴇʀ  ɪᴅ  /  ᴀs  ʀᴇᴘʟʏ>

→  ʀᴍɪɴs  -  ʀᴇᴍᴏᴠᴇs  ᴀ  ᴜsᴇʀ  ғʀᴏᴍ  ɪɴsᴘᴇᴄᴛᴏʀ.
ғᴏʀᴍᴀᴛ  :  ʀᴍɪɴs  <ᴜsᴇʀ  ɪᴅ  /  ᴀs  ʀᴇᴘʟʏ>

→  ɪɴsᴘᴇᴄᴛᴏʀs  -  ʟɪsᴛs  ᴀʟʟ  ɪɴsᴘᴇᴄᴛᴏʀᴊᴏɪɴ

→  ᴊᴏɪɴ  -  ᴊᴏɪɴs  ᴀ  ᴄʜᴀᴛ.
ғᴏʀᴍᴀᴛ  :  ᴊᴏɪɴ  <ᴄʜᴀᴛ  ᴜsᴇʀɴᴀᴍᴇ  ᴏʀ  ɪɴᴠɪᴛᴇ  ʟɪɴᴋ>

→  ʟᴇᴀᴠᴇ  -  ʟᴇᴀᴠᴇs  ᴀ  ᴄʜᴀᴛ.
ғᴏʀᴍᴀᴛ  :  ʟᴇᴀᴠᴇ  <ᴄʜᴀᴛ  ᴜsᴇʀɴᴀᴍᴇ  ᴏʀ  ɪᴅ>

→  ʀᴇsᴏʟᴠᴇ  -  ʀᴇsᴏʟᴠᴇ  ᴀ  ᴄʜᴀᴛ  ɪɴᴠɪᴛᴇ  ʟɪɴᴋ.
ғᴏʀᴍᴀᴛ  :  ʀᴇsᴏʟᴠᴇ  <ᴄʜᴀᴛ  ɪɴᴠɪᴛᴇ  ʟɪɴᴋ>

→  ɢᴇᴛ_ʀᴇᴅɪʀᴇᴄᴛ  -  ғᴏʟʟᴏᴡs  ʀᴇᴅɪʀᴇᴄᴛ  ᴏғ  ᴀ  ʟɪɴᴋ.
ғᴏʀᴍᴀᴛ  :  ɢᴇᴛ_ʀᴇᴅɪʀᴇᴄᴛ  <ᴜʀʟ>

۞  ɴᴏᴛᴇs:
/  ?  .  !  ᴀʀᴇ  sᴜᴘᴘᴏʀᴛᴇᴅ  ᴘʀᴇғɪxᴇs.

ᴇxᴀᴍᴘʟᴇ:  /ᴀᴅᴅᴇɴғ  ᴏʀ  ?ᴀᴅᴅᴇɴғ  ᴏʀ  .ᴀᴅᴅᴇɴғ
"""

__plugin_name__ = "extras"
