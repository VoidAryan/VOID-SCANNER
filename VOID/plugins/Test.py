from telethon.tl.functions.users import GetFullUserRequest
from VOID import System, system_cmd


@System.on(system_cmd(pattern=r"whois"))
async def whois(event):
    try:
        to_get = event.pattern_match.group(1)
    except Exception:
        if event.reply:
            replied = await event.get_reply_message()
            to_get = int(replied.sender.id)
            to_get = int(to_get)
        else:
            return

    try:
        data = await System(GetFullUserRequest(to_get))
    await System.send_message(
        event.chat_id,
        f"Perma Link: [{data.user.first_name}](tg://user?id={data.user.id})\nUser ID: `{data.user.id}`\nAbout: {data.about}",
    )


help_plus = """ [۞](https://telegra.ph/file/5403e3fb7685bcf8bf7b2.jpg) Here is Help for **Whois** -\n
`whois` - get data of the user\n
**Notes:**
`/` `?` `.` `!` are supported prefixes.\n
**Example:** `/addenf` or `?addenf` or `.addenf`
"""
__plugin_name__ = "Test"
