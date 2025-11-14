"""

Бот разработан командой The Code Factory в 2025 году
https://the-code-factory-team.github.io

"""

import datetime
import sqlite3
import sys
import traceback
from pprint import pprint

months = {1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля', 5: 'мая', 6: 'июня',
          7: 'июля', 8: 'августа', 9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'}
cur_day, cur_month, cur_year = datetime.datetime.now().day, datetime.datetime.now(
).month, datetime.datetime.now().year  # текущий день, месяц и год


application_sessions = {}


class DataBase:
    def __init__(self):
        try:
            self.con = sqlite3.connect(
                'functions/database.db', check_same_thread=False)
            self.cur = self.con.cursor()
        except sqlite3.Error as er:
            print('SQLite error: %s' % (' '.join(er.args)))
            print("Exception class is: ", er.__class__)
            print('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            pprint(traceback.format_exception(exc_type, exc_value, exc_tb))
            sys.stdout.flush()
            sys.exit()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            first_name TEXT,
            last_name TEXT,
            username TEXT,
            account_type TEXT DEFAULT 'unregistered',
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS document_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            document_type TEXT NOT NULL,
            status TEXT DEFAULT 'запрос отправлен',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS application_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            application_type TEXT NOT NULL,
            status TEXT DEFAULT 'запрос отправлен',
            media_files TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""")

    def request(self, text, params=[], commit=False):
        try:
            request = self.cur.execute(f"""{text}""", params)
        except Exception as er:
            print('SQLite error: %s' % (' '.join(er.args)))
            print("Exception class is: ", er.__class__)
            print('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            pprint(traceback.format_exception(exc_type, exc_value, exc_tb))
            return False

        if not commit:
            return request.fetchall()
        else:
            self.con.commit()
            if "INSERT" in text:
                return request.lastrowid
            return request


db = DataBase()


def greetings(name):  # приветствие, в соответствии со временем суток
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 6:
        return f"Доброй ночи, {name}! 🌚"
    elif 6 <= hour < 12:
        return f"Доброе утро, {name}! 🌞"
    elif 12 <= hour < 18:
        return f"Добрый день, {name}! 🌥️"
    return f"Добрый вечер, {name}! 🌅"


async def get_user_account_type(user_id):
    """Получить тип аккаунта пользователя"""
    result = db.request(
        "SELECT account_type FROM users WHERE user_id = ?",
        [user_id]
    )
    return result[0][0] if result else 'unregistered'


async def register_user(user_info, account_type):
    """Зарегистрировать пользователя или обновить тип аккаунта"""
    db.request(
        """INSERT OR REPLACE INTO users 
        (user_id, first_name, last_name, username, account_type) 
        VALUES (?, ?, ?, ?, ?)""",
        [user_info.user_id, user_info.first_name, user_info.last_name,
         user_info.username, account_type],
        commit=True
    )
