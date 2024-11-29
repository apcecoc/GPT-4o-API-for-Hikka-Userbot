import json
import aiohttp
from markdown2 import markdown
from telethon.tl.types import Message
from .. import loader, utils

__version__ = (1, 0, 11)

#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2024
#           https://t.me/apcecoc
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://example.com/api_icon.png
# meta banner: https://example.com/api_banner.jpg
# meta developer: @apcecoc
# scope: hikka_only
# scope: hikka_min 1.2.10

@loader.tds
class GPT4oMod(loader.Module):
    """Interact with GPT-4o API"""

    strings = {
        "name": "GPT4oAPI",
        "processing": "🤖 <b>Processing your request...</b>",
        "error": "❌ <b>Error while processing your request.</b>",
        "response": "🤖 <b>GPT-4o Response:</b>\n\n{response}",
    }

    strings_ru = {
        "processing": "🤖 <b>Обрабатываю ваш запрос...</b>",
        "error": "❌ <b>Ошибка при обработке запроса.</b>",
        "response": "🤖 <b>Ответ GPT-4o:</b>\n\n{response}",
        "_cls_doc": "Взаимодействие с API GPT-4о",
    }

    def _convert_markdown_to_html(self, text: str) -> str:
        """
        Converts Markdown to HTML using markdown2 library.
        """
        return markdown(text)

    @loader.command(ru_doc="Отправить запрос к GPT-4o API")
    async def gpt4o(self, message: Message):
        """Send a request to GPT-4o API"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("error"))
            return

        await utils.answer(message, self.strings("processing"))

        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": args,
                }
            ]
        }

        api_url = "https://api.paxsenix.biz.id/ai/gpt4o"
        headers = {"Content-Type": "application/json"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, headers=headers, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        response_message = data.get("message", "No response received.")

                        # Convert the entire response from Markdown to HTML
                        html_response = self._convert_markdown_to_html(response_message)

                        await utils.answer(
                            message,
                            self.strings("response").format(response=html_response),
                        )
                    else:
                        await utils.answer(message, self.strings("error"))
        except Exception as e:
            await utils.answer(message, self.strings("error"))
            raise e
