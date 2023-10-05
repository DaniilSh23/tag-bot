from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from tgbot.keyboards.bot_buttons import BUTTONS_DCT

CANCEL_SEND_COMMENT_KBRD = InlineKeyboardMarkup([
    [
        BUTTONS_DCT['COME_BACK_LATER'],
    ],
])


async def form_webapp_kbrd(buttons_data):
    """
    Формирование клавиатуры с одной WebApp кнопкой
    :param buttons_data: tuple - Данные для клавиатуры ((название кнопки, ссылка на страницу), ...).
    """
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text=name,
                web_app=WebAppInfo(url=link)
            )
        ]
        for name, link in buttons_data
    ])

