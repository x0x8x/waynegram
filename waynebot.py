import traceback, sys, io, os, html, textwrap, asyncio

from asyncio import sleep
from contextlib import redirect_stdout
from io import StringIO

from utils import meval

from telethon import TelegramClient, events
from telethon.events import NewMessage, MessageEdited
from telethon.errors import MessageTooLongError

APP_ID = 12345
APP_HASH = "abcd123"


client = TelegramClient('bot', api_id=APP_ID, api_hash=APP_HASH)

@client.on(events.NewMessage(outgoing=True, pattern=r"(\,x\s).+"))
@client.on(events.MessageEdited(outgoing=True, pattern=r"(\,x\s).+"))
async def eval(event):
    client = event.client
    message = event.message
    cmd = event.pattern_match.group(1)
    code: str = event.raw_text
    code = code.replace(cmd, "", 1)

    caption = "<b>Evaluated expression:</b>\n<code>{}</code>\n\n<b>Result:</b>\n".format(
        code
    )
    preserve_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        res = str(await meval(code, locals()))
    except Exception:
        caption = "<b>Evaluation failed:</b>\n<code>{}</code>\n\n<b>Result:</b>\n".format(
            code
        )
        etype, value, tb = sys.exc_info()
        res = "".join(traceback.format_exception(etype, value, None, 0))
        sys.stdout = preserve_stdout
    try:
        val = sys.stdout.getvalue()
    except AttributeError:
        val = None

        sys.stdout = preserve_stdout
    try:
        await event.edit(
            caption + f"<code>{html.escape(res)}</code>", parse_mode="html"
        )

    except MessageTooLongError:
        res = textwrap.wrap(res, 4096 - len(caption))
        await event.reply(caption + f"<code>{res[0]}</code>", parse_mode="html")
        for part in res[1::]:
            await asyncio.sleep(3)
            await event.reply(f"<code>{part}</code>", parse_mode="html")

        else:
            await event.reply(caption, parse_mode="html")
            
client.start()
client.run_until_disconnected()
