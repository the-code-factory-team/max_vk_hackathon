"""

Бот разработан командой The Code Factory в 2025 году
https://the-code-factory-team.github.io

"""

from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types import MessageCallback, CallbackButton, MessageCreated
from maxapi import F, Router
import sys
from datetime import datetime, timedelta

sys.path.append('functions')

schedule_router = Router()


SCHEDULE = {
    'Понедельник': [
        {'time': '13:25-15:00', 'subject': 'Программирование',
            'teacher': 'Воронина И.Е.', 'audience': '227'},
        {'time': '15:10-16:45', 'subject': 'Программирование',
            'teacher': 'Воронина И.Е.', 'audience': '227'}
    ],
    'Вторник': [
        {'time': '11:30-13:05', 'subject': 'Линейная алгебра',
            'teacher': 'Лазарев К.П.', 'audience': '435'},
        {'time': '13:25-15:00', 'subject': 'Линейная алгебра',
            'teacher': 'Лазарев К.П.', 'audience': '227'},
        {'time': '15:10-16:45', 'subject': 'Математический анализ',
            'teacher': 'Сумина Р.С.', 'audience': '437'},
        {'time': '16:55-18:30', 'subject': 'Математический анализ',
            'teacher': 'Сумина Р.С.', 'audience': '437'}
    ],
    'Среда': [
        {'time': '9:45-11:20', 'subject': 'ИИТОН',
            'teacher': 'Шуйкова И.А.', 'audience': '216'},
        {'time': '11:30-13:05', 'subject': 'Программирование',
            'teacher': 'Пастревич М.К.', 'audience': '9'},
        {'time': '13:25-15:00', 'subject': 'ИИТОН',
            'teacher': 'Шуйкова И.А.', 'audience': '227'},
        {'time': '15:10-16:45', 'subject': 'Физкультура',
            'teacher': 'Кобелёв В.И.', 'audience': 'Спортзал'},
    ],
    'Четверг': [
        {'time': '8:00-9:35', 'subject': 'Дискретная математика',
            'teacher': 'Бондаренко Ю.В.', 'audience': '329'},
        {'time': '9:45-11:20', 'subject': 'Английский язык',
            'teacher': 'Кривенко Л.А.', 'audience': '315'},
        {'time': '11:30-13:05', 'subject': 'Математический анализ',
            'teacher': 'Шашкин А.И.', 'audience': '409П'},
    ],
    'Пятница': [
        {'time': '8:00-9:35', 'subject': 'Дискретная математика',
            'teacher': 'Недикова Т.Н.', 'audience': '410П'},
        {'time': '9:45-11:20', 'subject': 'Основы российской государственности',
            'teacher': 'Погорельчик А.В.', 'audience': '430'},
        {'time': '13:25-15:00', 'subject': 'Физкультура',
            'teacher': 'Кобелёв В.И.', 'audience': 'Спортзал'},
    ],
    'Суббота': [
        {'time': '8:00-9:35', 'subject': 'Информационные системы и технологии',
            'teacher': 'Экерт Н.А.', 'audience': '226'},
        {'time': '12:15-13:50', 'subject': 'Основы российской государственности',
            'teacher': 'Шурыгина М.А.', 'audience': '410П'},
    ]
}

WEEK_DAYS = {
    0: 'Понедельник',
    1: 'Вторник',
    2: 'Среда',
    3: 'Четверг',
    4: 'Пятница',
    5: 'Суббота',
    6: 'Воскресенье'
}


def get_day_schedule(offset=0):
    target_date = datetime.now() + timedelta(days=offset)
    day_name = WEEK_DAYS[target_date.weekday()]
    lessons = SCHEDULE.get(day_name, [])
    return {
        'date': target_date.strftime("%d.%m.%Y"),
        'day_name': day_name,
        'lessons': lessons,
        'is_weekend': len(lessons) == 0
    }


def format_schedule(data):
    if data['is_weekend']:
        return f"📅{data['day_name']} ({data['date']})\n🎉 Выходной! Пар нет."

    result = f"📅{data['day_name']} ({data['date']})\n\n"
    for lesson_number, lesson in enumerate(data['lessons'], 1):
        result += f"{lesson_number}. 🕐 {lesson['time']}\n"
        result += f"    📚 {lesson['subject']}\n"
        result += f"    👨‍🏫 {lesson['teacher']}\n"
        result += f"    🏫 Ауд. {lesson['audience']}\n\n"

    return result


def get_upcoming_lessons():
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_day = WEEK_DAYS[now.weekday()]

    upcoming_lessons = []
    for lesson in SCHEDULE.get(current_day, []):
        start_time = lesson["time"].split("-")[0]

        lesson_time = datetime.strptime(start_time, "%H:%M")
        current_time_obj = datetime.strptime(current_time, "%H:%M")
        time_diff = (lesson_time - current_time_obj).total_seconds() / 3600

        if 0 <= time_diff <= 2:
            upcoming_lessons.append({
                "day": current_day,
                "lesson": lesson,
                "hours_until": time_diff
            })

    return upcoming_lessons


@schedule_router.message_callback(F.callback.payload == "ab_schedule")
async def schedule_handler(clbck: MessageCallback):
    builder = InlineKeyboardBuilder()
    builder.row(
        CallbackButton(text='📅 Сегодня', payload="schedule_today"),
        CallbackButton(text='📅 Завтра', payload="schedule_tomorrow")
    )
    builder.row(
        CallbackButton(text='⬅️ Назад', payload="student")
    )
    await clbck.message.answer(
        text='🗓️ Выберите день для просмотра расписания:',
        attachments=[builder.as_markup()]
    )


@schedule_router.message_callback(F.callback.payload == "schedule_today")
async def schedule_today_handler(clbck: MessageCallback):
    schedule_data = get_day_schedule(0)
    schedule_text = format_schedule(schedule_data)
    await clbck.message.answer(text=schedule_text)


@schedule_router.message_callback(F.callback.payload == "schedule_tomorrow")
async def schedule_tomorrow_handler(clbck: MessageCallback):
    schedule_data = get_day_schedule(1)
    schedule_text = format_schedule(schedule_data)
    await clbck.message.answer(text=schedule_text)
