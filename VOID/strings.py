on_string = """
⚜【V๏ɪ፝֟𝔡】• SᴄᴀɴɴᴇƦ ⚜
•──────✗───────•
۞ ʀᴀɴᴋ : {Enforcer}
۞ ɴᴀᴍᴇ : {name}
•──────✗───────•
「 ʏᴏᴜ ᴀʀᴇ ᴀɴ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀ ! 」
"""

# Make sure not to change these too much
# If you still wanna change it change the regex too
scan_request_string = """
$SCAN @voidaryan 
Cymatic Scan Request!
**Enforcer:** {enforcer}
**User scanned:** {spammer}
**Reason:** `{reason}`
**Scan Source:** {chat}
**Target Message:** `{message}`
"""
proof_string = """
**Case file for** - {proof_id} :
┣━**Reason**: {reason}
┗━**Message**
         ┣━[Nekobin]({paste})
         ┗━[DelDog]({url})"""


forced_scan_string = """
$FORCED @voidaryan
**Inspector:** {ins}
**Target:** {spammer}
**Reason:** `{reason}`
**Scan Source:** {chat}
**Target Message:** `{message}`
"""

group_admin_scan_string = """
$FORCED ASSOCIATION-BAN
**Inspector**: {ins}
**Target Chat**: {t_chat}
**Reason**: `{reason}`
**Scan Source**: {chat}
**Chat Owner**: 
`{owner_id}`
**Admins**: `{admins}`
"""

group_admin_request_string = """
$ASSOCIATION-BAN
Cymatic Ban Request!
**Enforcer**: {enf}
**Target Chat**: {t_chat}
**Reason**: `{reason}`
**Scan Source**: {chat}
**Chat Owner**: 
`{owner_id}`
**Admins**: `{admins}`
"""

revert_request_string = """
$REVERT
Cymatic Revert Request!
**Enforcer:** `{enforcer}`
**User to revert:** `{spammer}`
**Revert Source:** {chat}
"""

reject_string = """
$REJECTED
**Crime Coefficient:** `Under 100`
Not a target for enforcement action.
The trigger of Dominator will be locked.
"""

revert_reject_string = """
$REJECTED
**Crime Coefficient:** `Over 100`
Not a target for revert action.
The trigger of Dominator will be unlocked.
"""

check_ban_string = """
**Case file for** - `{user_id}`:
┣━**Date**: `{date}`
┣━**Timestamp**: `{timestamp}`
┗━**Reason**: `{reason}`"""


scan_approved_string = """
#LethalEliminator
**Target User:** {scam}
**Crime Coefficient:** `Over 300`
**Reason:** `{reason}`
**Enforcer:** `{enforcer}`
**Case Number:** `{proof_id}`
"""

bot_gban_string = """
#DestroyDecomposer
**Enforcer:** `{enforcer}`
**Target User:** {scam}
**Reason:** `{reason}`
"""

# https://psychopass.fandom.com/wiki/Crime_Coefficient_(Index)
# https://psychopass.fandom.com/wiki/The_Dominator
