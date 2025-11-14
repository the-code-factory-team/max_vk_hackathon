"""

Бот разработан командой The Code Factory в 2025 году
https://the-code-factory-team.github.io

"""

import sqlite3
import sys
from maxapi import F, Router
from maxapi.types import MessageCallback, CallbackButton, Command, MessageCreated, BotStarted
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder

help_router = Router()

conn = sqlite3.connect('functions/faq_database.db')
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS questions_answers')
conn.commit()
cursor.execute('''
CREATE TABLE IF NOT EXISTS questions_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL
)
''')

questions_answers = [
    ("Как посмотреть расписание",  "Выбрать раздел Студентам -> Расписание -> Сегодня / Завтра, готово"),
    ("Как подать заявление на мат. помощь", "Выбрать раздел Студентам -> Документооборот -> Заявления -> Мат. помощь -> Подать заявление -> Прикрепить файл заявления ")
]

cursor.executemany('INSERT INTO questions_answers (question, answer) VALUES (?, ?)', questions_answers)

conn.commit()

cursor.execute('SELECT * FROM questions_answers')
rows = cursor.fetchall()

@help_router.message_callback(F.callback.payload == "help")
async def handle_message_help(clbck: MessageCallback):
    builder = InlineKeyboardBuilder()

    builder.row(CallbackButton(text='🆘 Связаться с поддержкой', payload="helpers"))
    builder.row(CallbackButton(text='⁉ FAQ', payload="faq"))
    builder.row(CallbackButton(text='⬅️ Назад', payload="student"))

    
    await clbck.message.answer(
        text='Помощь🆘\n\nВыберите нужный раздел:',
        attachments=[builder.as_markup()]
    )


@help_router.message_callback(F.callback.payload == "faq")
async def handle_message_faq(clblk: MessageCallback):
    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(text='⬅️ Назад', payload="help"))

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
