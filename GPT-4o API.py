import json
import aiohttp
import re
from markdown2 import markdown
from telethon.tl.types import Message
from .. import loader, utils

__version__ = (1, 1, 0)

#       █████  ██████   ██████ ███████  ██████  ██████   ██████ 
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

    def _format_code_block(self, text: str) -> str:
        """
        Formats code blocks, replacing triple backticks with <pre> tags and extracting the programming language.
        """
        code_block_pattern = re.compile(r"```(\w+)?\n([\s\S]*?)```")
        matches = code_block_pattern.findall(text)

        for lang, code in matches:
            formatted_code = f"<pre><code class='{lang}'>{utils.escape_html(code)}</code></pre>"
            text = text.replace(f"```{lang}\n{code}```", formatted_code)

        return text

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

        api_url = "https://paxsenix.koyeb.app/ai/gpt4o"
        headers = {"Content-Type": "application/json"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, headers=headers, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        response_message = data.get("message", "No response received.")

                        # Convert Markdown to HTML
                        html_response = self._convert_markdown_to_html(response_message)

                        # Format code blocks
                        formatted_response = self._format_code_block(html_response)

                        await utils.answer(
                            message,
                            self.strings("response").format(response=formatted_response),
                        )
                    else:
                        await utils.answer(message, self.strings("error"))
        except Exception as e:
            await utils.answer(message, self.strings("error"))
            raise e
