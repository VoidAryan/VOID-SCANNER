from VOID import System, system_cmd
import os
import sys
import subprocess


@System.on(system_cmd(pattern=r"v gitpull"))
async def gitpull(event):
    subprocess.Popen("git pull", stdout=subprocess.PIPE, shell=True)
    await event.reply("Git pulled probably.")
    os.system("restart.bat")
    os.execv("start.bat", sys.argv)


@System.on(system_cmd(pattern=r"Iɴꜰɪɴɪᴛᴇ • SᴄᴀɴɴᴇƦ restart...."))
async def reboot(event):
    if event.fwd_from:
        return
    await event.reply("Restarting Iɴꜰɪɴɪᴛᴇ • SᴄᴀɴɴᴇƦ.....")
    await System.disconnect()
    os.execl(sys.executable, sys.executable, *sys.argv)
    sys.exit()


@System.on(system_cmd(pattern=r"v shutdown"))
async def shutdown(event):
    if event.fwd_from:
        return
    await event.reply("Shutting Down 【V๏ɪ፝֟𝔡】•  SᴄᴀɴɴᴇƦ... ")
    await System.disconnect()
