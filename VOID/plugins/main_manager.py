from Sibyl_System import Sibyl_logs, ENFORCERS, SIBYL, INSPECTORS
from Sibyl_System.strings import (
    scan_request_string,
    reject_string,
    forced_scan_string,
    group_admin_scan_string,
    revert_request_string,
    revert_reject_string,
    group_admin_request_string
)
from Sibyl_System import System, system_cmd
from Sibyl_System.utils import seprate_flags, Flag
from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantCreator
import asyncio

import re


tgurl_regex = re.compile("(http(s)?://)?t.me/(c/)?(\w+)/(\d+)")
url_regex = re.compile("(https?)?(://)?(\w+\.)?(\w+\.\w+)(/.*)?")

def get_data_from_url(url: str) -> tuple:
    """
    >>> get_data_from_url("https://t.me/c/1476401326/36963")
    (1476401326, 36963)
    """

    match = tgurl_regex.match(url)
    if not match:
        return False
    return (match.group(4), match.group(5))

def parse_url(url: str):
    match = url_regex.match(url)
    if not match:
        return False
    return {"full": match.group(0), "protocol": match.group(1), "domain": match.group(4), "path": match.group(5) or "/"}

def find_urls(string, exclude_telegram=False):
    match = url_regex.findall(string)
    if exclude_telegram:
        for m in match:
            if "telegram.me" in m or "t.me" in m:
                match.remove(m)
    if not match:
        return None
    return [parse_url("".join(m)) for m in match]

def getChatEntity(string):
    string = str(string)
    if string.startswith("-100"):
        string = string.replace("-100", "", 1)
    try:
        return int(string)
    except:
        return string

async def get_chat_creator_and_admins(event, chat_id, need_admins=False):
    creator = 0
    admins = ""
    async for user in event.client.iter_participants(chat_id, filter=ChannelParticipantsAdmins):
        if isinstance(user.participant, ChannelParticipantCreator):
            creator = user.id
            if not need_admins:
                return creator
        admins += f"\n{user.id}"
    return creator, admins

async def is_member(event, chat_id, user_id):
    async for user in event.client.iter_participants(chat_id):
        if user.id == user_id:
            return True
    return False


association_scan_request = {}

@System.command(
    e=system_cmd(pattern=r"scan ", allow_enforcer=True),
    group="main",
    help="Reply to a message WITH reason to send a request to Inspect",
    flags=[
        Flag(
            "-f",
            "Force approve a scan. Using this with scan will auto approve it",
            "store_true"
        ),
        Flag(
            "-u",
            "Grab message from url. Use this with message link to scan the user the message link redirects to.",
        ),
        Flag(
            "-o",
            "Original Sender. Using this will gban orignal sender instead of forwarder.",
            "store_true",
        ),
        Flag(
            "-a",
            "Blacklist all admins of a chat using this flag.",
            nargs="*",
            default=None
        ),
        Flag(
            "-r",
            "Reason to scan message with.",
            nargs="*",
            default=None
        )
    ],
    allow_unknown=True
)
async def scan(event, flags):
    replied = await event.get_reply_message()
    if flags.r:
        reason = " ".join(flags.r)
    elif not flags.a and not flags.u:
        split = event.text.split(' ', 1)
        if len(split) == 1:
            return
        reason = seprate_flags(split[1]).strip()
    else:
        await event.reply("You need to provide me a valid reason to blacklist them.\nUse scan with -r reason here")
        return
    if flags.u:
        url = flags.u
        data = get_data_from_url(url)
        if not data:
            await event.reply("Invalid url")
            return
        try:
            message = await System.get_messages(
                int(data[0]) if data[0].isnumeric() else data[0], ids=int(data[1])
            )
        except:
            await event.reply("Failed to get data from url")
            return
        executer = await event.get_sender()
        executor = f"[{executer.first_name}](tg://user?id={executer.id})"
        if not message:
            await event.reply("Failed to get data from url")
            return
        if message.from_id.user_id in ENFORCERS:
            return
        if message.media:
            await replied.forward_to(Sibyl_logs)
        if flags.f and executer.id in INSPECTORS:
            msg = await System.send_message(
                Sibyl_logs,
                forced_scan_string.format(
                    ins=executor, spammer=message.from_id.user_id, chat=f"https://t.me/{data[0]}/{data[1]}", message=message.text, reason=reason
                ),
                link_preview=False
            )
            await System.gban(
                executer.id, message.from_id.user_id, reason, msg.id, executer, message=message.text
            )
        else:
            msg = await System.send_message(
                Sibyl_logs,
                scan_request_string.format(
                    enforcer=executor,
                    spammer=message.from_id.user_id,
                    chat=f"https://t.me/{data[0]}/{data[1]}",
                    message=message.text,
                    reason=reason,
                ),
                link_preview=False
            )
        return
    executer = await event.get_sender()
    executor = f"[{executer.first_name}](tg://user?id={executer.id})"
    chat = (
        f"t.me/{event.chat.username}/{event.message.id}"
        if event.chat.username
        else f"t.me/c/{event.chat.id}/{event.message.id}"
    )
    if flags.a:
        if len(flags.a) < 1:
            await event.reply("Sorry, But God haven't given me powers to read your mind and get chat id from there.")
            return
        to_scan_chat = flags.a[0]
        reason = reason.replace(to_scan_chat, "", 1)
        try:
            ts_chat = await System.get_entity(getChatEntity(to_scan_chat))
        except:
            await event.reply("Chat not found.")
            return

        if not ts_chat.megagroup:
            await event.reply("You need to provide me a group's id, not channel's.")
            return
        
        creator, admins = await get_chat_creator_and_admins(event, ts_chat.id, True)

        await event.reply("Connecting to Scythe for a cymatic scan.")

        if flags.f and executer.id in INSPECTORS:
            msg = await System.send_message(
                    Sibyl_logs,
                    group_admin_scan_string.format(
                        ins=executor, t_chat=to_scan_chat, chat=chat, owner_id=creator, reason=reason, admins=admins
                    ),
                    link_preview=False
                )
            async for user in event.client.iter_participants(ts_chat.id, filter=ChannelParticipantsAdmins):
                if user.id in ENFORCERS or user.id in SIBYL:
                    continue
                if not user.bot:
                    await System.gban(executer.id, user.id, reason, msg.id, executer, message="")
                    await asyncio.sleep(10)
        else:
            msg = await System.send_message(
                Sibyl_logs, 
                group_admin_request_string.format(
                    enf=executor, t_chat=to_scan_chat, chat=chat, owner_id=creator, reason=reason, admins=admins
                ),
                link_preview=False
            )
            association_scan_request[msg.id] = {"msg_id": event.id, "chat_id": event.chat_id, "ts_chat":ts_chat.id, "reason":reason, "executer_id":executer.id}
    if not event.is_reply:
        return
    if flags.o:
        if replied.fwd_from:
            reply = replied.fwd_from
            target = reply.from_id.user_id
            if reply.from_id.user_id in ENFORCERS or reply.from_id.user_id in SIBYL:
                return
            if not reply.from_id.user_id:
                await event.reply("Cannot get user ID.")
                return
            if reply.from_name:
                sender = f"[{reply.from_name}](tg://user?id={reply.from_id.user_id})"
            else:
                sender = (
                    f"[{reply.from_id.user_id}](tg://user?id={reply.from_id.user_id})"
                )
    else:
        if replied.sender.id in ENFORCERS:
            return
        sender = f"[{replied.sender.first_name}](tg://user?id={replied.sender.id})"
        target = replied.sender.id
    
    req_proof = req_user = False
    if flags.f and executer.id in INSPECTORS:
        approve = True
    else:
        approve = False
    if replied.media:
        await replied.forward_to(Sibyl_logs)
    
    await event.reply("Connecting to Scythe for a cymatic scan.")
    if req_proof and req_user:
        await replied.forward_to(Sibyl_logs)
        await System.gban(
            executer.id, req_user, reason, msg.id, executer, message=replied.text
        )
    if not approve:
        msg = await System.send_message(
            Sibyl_logs,
            scan_request_string.format(
                enforcer=executor,
                spammer=sender,
                chat=chat,
                message=replied.text,
                reason=reason,
            ),
            link_preview=False
        )
        return
    msg = await System.send_message(
        Sibyl_logs,
        forced_scan_string.format(
            ins=executor, spammer=sender, chat=chat, message=replied.text, reason=reason
        ),
        link_preview=False
    )
    await System.gban(
        executer.id, target, reason, msg.id, executer, message=replied.text
    )

revert_request = {}
@System.on(system_cmd(pattern=r"re(vive|vert|store) ", allow_enforcer=True, allow_inspectors=True))
async def revive(event):
    replied = await event.get_reply_message()
    if replied:
        user_id = replied.sender.id
    else:
        try:
            user_id = event.text.split(" ", 1)[1]
        except IndexError:
            return
    if not user_id.isnumeric():
        await event.reply("Invalid id")
        return
    executor = await event.get_sender()
    if event.sender_id in ENFORCERS:
        chatlink = f"t.me/c/{(str(event.chat_id)).replace('-100', '')}/{event.id}"
        await event.reply("Connecting to Scythe for a cymatic revert.")
        msg = await System.send_message(Sibyl_logs, revert_request_string.format(enforcer=executor.id, spammer=int(user_id), chat=chatlink))
        revert_request[msg.id] = {"user_id":user_id, "chat_id":event.chat_id, "msg_id":event.id}
        return
    a = await event.reply("Reverting bans..")
    if not (
        await System.ungban(int(user_id), f" By //{(await event.get_sender()).id}")
    ):
        await a.edit("User is not gbanned.")
        return
    await a.edit("Revert request sent to Scythe. This might take 10minutes or so.")


@System.on(system_cmd(pattern=r"sibyl logs"))
async def logs(event):
    await System.send_file(event.chat_id, "log.txt")

@System.command(
    e = system_cmd(pattern=r"approve", allow_inspectors=True, force_reply=True),
    group="main",
    help="Approve a scan request.",
    flags=[Flag("-or", "Overwrite reason", nargs="*"), Flag("-silent", "Silently approve a scan", "store_true")]
)
async def approve(event, flags):
    replied = await event.get_reply_message()
    revert = re.match(r"\$REVERT", replied.text)
    assoban = re.match(r"\$ASSOCIATION-BAN", replied.text)
    match = re.match(r"\$SCAN", replied.text)
    auto_match = re.search(r"\$AUTO(SCAN)?", replied.text)
    me = await System.get_me()
    if auto_match:
        if replied.sender.id == me.id:
            id = re.search(
                r"\*\*Scanned.*:\*\* (\[\w+\]\(tg://user\?id=(\d+)\)|(\d+))",
                replied.text,
            ).group(2)
            try:
                message = re.search(
                    "(\*\*)?Message:(\*\*)? (.*)", replied.text, re.DOTALL
                ).group(3)
            except:
                message = None
            try:
                bot = (await System.get_entity(id)).bot
            except:
                bot = False
            reason = re.search("\*\*Reason:\*\* (.*)", replied.text).group(1)
            await System.gban(
                enforcer=me.id,
                target=id,
                reason=reason,
                msg_id=replied.id,
                auto=True,
                bot=bot,
                message=message,
            )
            return
    overwritten = False
    if match:
        reply = replied.sender.id
        sender = await event.get_sender()
        # checks to not gban the Gbanner and find who is who
        if reply == me.id:
            list = re.findall(r"tg://user\?id=(\d+)", replied.text)
            if getattr(flags, "or", None):
                reason = " ".join(getattr(flags, "or"))
                await replied.edit(
                    re.sub(
                        "(\*\*)?(Scan)? ?Reason:(\*\*)? (`([^`]*)`|.*)",
                        f'**Scan Reason:** `{reason}`',
                        replied.text,
                    )
                )
                overwritten = True
            else:
                reason = re.search(
                    r"(\*\*)?(Scan)? ?Reason:(\*\*)? (`([^`]*)`|.*)", replied.text
                )
                reason = reason.group(5) if reason.group(5) else reason.group(4)
            if len(list) > 1:
                id1 = list[0]
                id2 = list[1]
            else:
                id1 = list[0]
                id2 = re.findall(r"(\d+)", replied.text)[1]
            if id1 in ENFORCERS or SIBYL:
                enforcer = id1
                scam = id2
            else:
                enforcer = id2
                scam = id1
            try:
                bot = (await System.get_entity(scam)).bot
            except:
                bot = False
            try:
                message = re.search(
                    "(\*\*)?Target Message:(\*\*)? (.*)", replied.text, re.DOTALL
                ).group(3)
            except:
                message = None
            await System.gban(
                enforcer, scam, reason, replied.id, sender, bot=bot, message=message
            )

            orig = re.search(r"t.me/(\w+)/(\d+)", replied.text.replace("/c/", "/"))
            chat_id_entity = getChatEntity(orig.group(1))
            if not await is_member(event, chat_id_entity, (await System.get_me()).id):
                return
            
            if orig and not getattr(flags, "silent", None) == True:
                try:
                    if overwritten:
                        await System.send_message(
                            chat_id_entity,
                            f"User is a target for enforcement action.\nEnforcement Mode: Lethal Eliminator\nYour reason was overwritten with: `{reason}`",
                            reply_to=int(orig.group(2)),
                        )
                        return
                    await System.send_message(
                        chat_id_entity,
                        "User is a target for enforcement action.\nEnforcement Mode: Lethal Eliminator",
                        reply_to=int(orig.group(2)),
                    )
                except:
                    await event.reply('Failed to notify enforcer about scan being accepted.')
    if revert:
        if not replied.id in revert_request:
            await event.reply("This revert request has been expired!")
            return
        info = revert_request[replied.id]
        a = await event.reply("Revert request accepted!")
        chat_id = info["chat_id"]
        msg_id = info["msg_id"]
        spammer = info["user_id"]
        del revert_request[replied.id]
        if not (await System.ungban(int(spammer), f" By //{(await event.get_sender()).id}")):
            await a.edit("User is not gbanned.")
            return
        await System.send_message(getChatEntity(chat_id), "Revert request has been accepted!", reply_to=int(msg_id))

    if assoban:
        if not replied.id in association_scan_request:
            await event.reply("This scan request has been expired!")
            return
        info = association_scan_request[replied.id]
        # association_scan_request[msg.id] = {"msg_id": event.id, "chat_id": event.chat_id, "ts_chat":ts_chat.id, "reason":reason}
        ts_chat_id = info["ts_chat"]
        chat_id = info["chat_id"]
        msg_id = info["msg_id"]
        executer_id = info["executer_id"]
        if getattr(flags, "or", None):
            reason = " ".join(getattr(flags, "or"))
            overwritten = True
        else:
            reason = info["reason"]

        async for user in event.client.iter_participants(ts_chat_id, filter=ChannelParticipantsAdmins):
            if user.id in ENFORCERS or user.id in SIBYL:
                continue
            if not user.bot:
                await System.gban(executer_id, user.id, reason, replied.id, event.sender_id, message="")
                await asyncio.sleep(10)

        
        chat_id_entity = getChatEntity(chat_id)
        if not await is_member(event, chat_id_entity, (await System.get_me()).id):
            return
        
        try:
            if overwritten:
                await System.send_message(
                    chat_id_entity,
                    f"Chat is a target for enforcement action.\nEnforcement Mode: Lethal Eliminator\nYour reason was overwritten with: `{reason}`",
                    reply_to=int(msg_id),
                )
                return
            await System.send_message(
                chat_id_entity,
                "Chat is a target for enforcement action.\nEnforcement Mode: Lethal Eliminator",
                reply_to=int(msg_id),
            )
        except:
            await event.reply('Failed to notify enforcer about scan being accepted.')



        
@System.on(system_cmd(pattern=r"reject", allow_inspectors=True, force_reply=True))
async def reject(event):
    # print('Trying OmO')
    replied = await event.get_reply_message()
    me = await System.get_me()
    if replied.from_id.user_id == me.id:
        # print('Matching UwU')
        match = re.match(r"\$(SCAN|AUTO(SCAN)?)", replied.text)
        if match:
            # print('Matched OmU')
            id = replied.id
            await System.edit_message(Sibyl_logs, id, reject_string)
    if re.match(r"\$REVERT", replied.text):
        if not replied.id in revert_request:
            await event.reply("This revert request has expired!")
            return
        info = revert_request[replied.id]
        del revert_request[replied.id]
        await System.send_message(
            getChatEntity(info["chat_id"]),
            "Your revert requested is rejected.",
            reply_to=info["msg_id"],
            link_preview=False
        )
        await System.edit_message(Sibyl_logs, replied.id, revert_reject_string)
        return
    orig = re.search(r"t.me/(\w+)/(\d+)", replied.text)
    _orig = re.search(r"t.me/c/(\w+)/(\d+)", replied.text)
    reason = seprate_flags(event.text)
    reason = reason.split(None, 1)
    if orig:
        origchat = orig.group(1)
        origreply = int(orig.group(2))
    elif _orig:
        origchat = int(_orig.group(1))
        origreply = int(_orig.group(2))
    else:
        return
    text = "Crime coefficient less than 100!\nUser is not a target for enforcement action, Trigger of dominator will be locked."
    if re.match(r"\$ASSOCIATION-BAN", replied.text):
        if not replied.id in association_scan_request:
            await event.reply("This revert request has expired!")
            return
        info = association_scan_request[replied.id]
        del association_scan_request[replied.id]
        text = text.replace("User", "Chat")
        origreply = info["msg_id"]
        origchat = info["chat_id"]
        try:
            await System.edit_message(Sibyl_logs, replied.id, reject_string)
        except:
            pass
    
    if len(reason) > 1:
        text += f"\nReason: `{reason[1].strip()}`"

    await System.send_message(
        origchat,
        text,
        reply_to=origreply,
        link_preview=False
    )


help_plus = """
Here is the help for **Main**:

Commands:
    `scan` - Reply to a message WITH reason to send a request to Inspectors/Sibyl for judgement
    `approve` - Approve a scan request (Only works in Sibyl System Base)
    `revert` or `revive` or `restore` - Ungban ID
    `qproof` - Get quick proof from database for given user id
    `proof` - Get message from proof id which is at the end of gban msg
    `reject` - Reject a scan request

Flags:
    scan:
        `-f` - Force approve a scan. Using this with scan will auto approve it (Inspectors+)
        `-u` - Grab message from url. Use this with message link to scan the user the message link redirects to. (Enforcers+)
        `-o` - Original Sender. Using this will gban orignal sender instead of forwarder (Enforcers+)
    approve:
        `-or` - Overwrite reason. Use this to change scan reason.
    reject:
        `-r` - Reply to the scan message with reject reason.

All commands can be used with ! or / or ? or .
"""

__plugin_name__ = "Main"
