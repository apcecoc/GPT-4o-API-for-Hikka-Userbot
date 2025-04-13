import json
import aiohttp
import re
from telethon.tl.types import Message
from .. import loader, utils

__version__ = (1, 0, 13)

#        █████  ██████   ██████ ███████  ██████  ██████   ██████ 
#       ██   ██ ██   ██ ██      ██      ██      ██    ██ ██      
#       ███████ ██████  ██      █████   ██      ██    ██ ██      
#       ██   ██ ██      ██      ██      ██      ██    ██ ██      
#       ██   ██ ██       ██████ ███████  ██████  ██████   ██████

#              © Copyright 2025
#           https://t.me/apcecoc
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @apcecoc
# scope: hikka_only
# scope: hikka_min 1.2.10

@loader.tds
class GPT4oMod(loader.Module):
    """Interact with GPT-4o API"""

    strings = {
        "name": "GPT4oAPI",
        "processing": "🤖 <b>Processing your request...</b>",
        "error": "❌ <b>Error while processing your request: {error}</b>",
        "response": "🤖 <b>GPT-4o Response:</b>\n\n{response}",
    }

    strings_ru = {
        "processing": "🤖 <b>Обрабатываю ваш запрос...</b>",
        "error": "❌ <b>Ошибка при обработке запроса: {error}</b>",
        "response": "🤖 <b>Ответ GPT-4o:</b>\n\n{response}",
        "_cls_doc": "Взаимодействие с API GPT-4о",
    }

    def _markdown_to_html(self, text: str) -> str:
        """
        Convert Markdown to HTML manually.
        """
        text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
        text = re.sub(r"_(.+?)_", r"<i>\1</i>", text)
        text = re.sub(r"^# (.+)", r"<h1>\1</h1>", text, flags=re.MULTILINE)
        text = re.sub(r"^## (.+)", r"<h2>\1</h2>", text, flags=re.MULTILINE)
        text = re.sub(r"^### (.+)", r"<h3>\1</h3>", text, flags=re.MULTILINE)
        text = re.sub(
            r"```(\w+)?\n([\s\S]*?)```",
            lambda m: f"<pre><code class='{m.group(1) or 'plaintext'}'>{utils.escape_html(m.group(2))}</code></pre>",
            text,
        )
        text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
        return text

    @loader.command(ru_doc="Отправить запрос к GPT-4o API")
    async def gpt4o(self, message: Message):
        """Send a request to GPT-4o API"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("error").format(error="No input provided"))
            return

        await utils.answer(message, self.strings("processing"))

        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": args,
                }
            ]
        }

        api_url = "https://api.paxsenix.biz.id/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer YOUR_API_KEY",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, headers=headers, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if not data.get("ok", False):
                            await utils.answer(
                                message,
                                self.strings("error").format(error=data.get("message", "Unknown error")),
                            )
                            return

                        response_message = data["choices"][0]["message"]["content"]

                        html_response = self._markdown_to_html(response_message)

                        await utils.answer(
                            message,
                            self.strings("response").format(response=html_response),
                        )
                    elif resp.status == 400:
                        data = await resp.json()
                        await utils.answer(
                            message,
                            self.strings("error").format(error=data.get("message", "Bad request")),
                        )
                    elif resp.status == 500:
                        data = await resp.json()
                        await utils.answer(
                            message,
                            self.strings("error").format(error=data.get("message", "Server error")),
                        )
                    else:
                        await utils.answer(
                            message,
                            self.strings("error").format(error=f"HTTP {resp.status}"),
                        )
        except Exception as e:
            await utils.answer(
                message,
                self.strings("error").format(error=str(e)),
            )