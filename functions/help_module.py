"""

Бот разработан командой The Code Factory в 2025 году
https://the-code-factory-team.github.io

"""

import sqlite3
from maxapi import F, Router
from maxapi.types import MessageCallback, CallbackButton, Command, MessageCreated, BotStarted
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from utils import db

help_router = Router()

if len(db.request('SELECT * FROM questions_answers')) == 0:
    questions_answers = [
        ("Как посмотреть расписание",  "Выбрать раздел Студентам -> Расписание -> Сегодня / Завтра, готово"),
        ("Как подать заявление на мат. помощь", "Выбрать раздел Студентам -> Документооборот -> Заявления -> Мат. помощь -> Подать заявление -> Прикрепить файл заявления ")
    ]

    db.cur.executemany('INSERT INTO questions_answers (question, answer) VALUES (?, ?)', questions_answers)
    db.con.commit()

@help_router.message_created(Command("help"))
@help_router.message_callback(F.callback.payload == "help")
async def handle_message_help(clbck: MessageCallback):
    builder = InlineKeyboardBuilder()

    builder.row(CallbackButton(text='🆘 Связаться с поддержкой', payload="helpers"))
    builder.row(CallbackButton(text='⁉ FAQ', payload="faq"))
    builder.row(CallbackButton(text='⬅️ Назад', payload="main_menu"))

    
    await clbck.message.answer(
        text='Помощь🆘\n\nВыберите нужный раздел:',
        attachments=[builder.as_markup()]
    )


@help_router.message_callback(F.callback.payload == "faq")
async def handle_message_faq(clblk: MessageCallback):
    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(text='⬅️ Назад', payload="help"))

    rows = db.request('SELECT * FROM questions_answers')

    qa_txt = ""
    for row in rows:
        qa_txt += f"{row[0]}. Вопрос: {row[1]}\n\n   Ответ: {row[2]}\n\n"
    

    await clblk.message.answer(
        text=qa_txt,
        attachments=[builder.as_markup()]
    )

@help_router.message_callback(F.callback.payload == "helpers")
async def handle_message_faq(clblk: MessageCallback):
    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(text='⬅️ Назад', payload="help"))
    await clblk.message.answer(
        text="Здесь можно связаться с поддержкой вуза(В разработке)",
        attachments=[builder.as_markup()]
    )