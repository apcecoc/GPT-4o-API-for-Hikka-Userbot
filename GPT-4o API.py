__version__ = (1, 1, 1)

#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2024
#           https://t.me/apcecoc
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta banner: https://i.ibb.co/qnmP7nX/file-21.jpg
# meta developer: @apcecoc
# scope: hikka_only
# scope: hikka_min 1.2.10

import json
import aiohttp
import re
from telethon.tl.types import Message
from .. import loader, utils


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

    def _format_code_block(self, text: str) -> str:
        """
        Форматирует текст, заменяя тройные кавычки на теги <pre> и извлекая язык программирования.
        """
        code_block_pattern = re.compile(r"```(\w+)?\n([\s\S]*?)```")
        matches = code_block_pattern.findall(text)

        # Если найдены блоки кода, заменяем их на <pre> с указанием языка
        for lang, code in matches:
            formatted_code = f"<pre><code class='{lang}'>{utils.escape_html(code)}</code></pre>"
            text = text.replace(f"```{lang}\n{code}```", formatted_code)

        return text

    @loader.command(ru_doc="<ваш запрос> Отправить запрос к GPT-4o API")
    async def gpt4o(self, message: Message):
        """<your query> Send a request to GPT-4o API"""
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

                        # Обрабатываем кодовые блоки в ответе
                        formatted_response = self._format_code_block(response_message)

                        await utils.answer(
                            message,
                            self.strings("response").format(response=formatted_response),
                        )
                    else:
                        await utils.answer(message, self.strings("error"))
        except Exception as e:
            await utils.answer(message, self.strings("error"))
            raise e
