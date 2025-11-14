"""

Бот разработан командой The Code Factory в 2025 году
https://the-code-factory-team.github.io

"""

import functions.utils as utils
from maxapi.types import MessageCallback, CallbackButton, Command, MessageCreated, BotStarted
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi import F, Router
import sys

sys.path.append('functions')

router = Router()


@router.message_created(Command('start'))
async def hello(event: MessageCreated):
    account_type = await utils.get_user_account_type(event.from_user.user_id)

    if account_type == 'unregistered':
        return await show_registration_menu(event)
    else:
        return await show_main_menu(event, account_type)


async def show_registration_menu(event):
    builder = InlineKeyboardBuilder()
    builder.row(
        CallbackButton(text='🧒 Абитуриент', payload="register_abiturient"),
        CallbackButton(text='👨‍🎓 Студент', payload="register_student")
    )
    builder.row(
        CallbackButton(text='👨‍🏫 Преподаватель', payload="register_teacher"),
        CallbackButton(text='👨‍💻 Администратор', payload="register_director")
    )

    user_info = event.from_user
    welcome_text = (
        f"👋 Добро пожаловать, {user_info.first_name}!\n\n"
        "📝 Для начала работы необходимо пройти регистрацию\n"
        "Пожалуйста, выберите ваш статус:\n\n"
        "• 🧒 Абитуриент - готовитесь к поступлению\n"
        "• 👨‍🎓 Студент - обучаетесь в вузе\n"
        "• 👨‍🏫 Преподаватель - работаете в вузе\n"
        "• 👨‍💻 Администратор - административный персонал"
    )

    if type(event) is not BotStarted:
        return await event.message.answer(
            text=welcome_text,
            attachments=[builder.as_markup()]
        )

    return await event.bot.send_message(
        chat_id=event.chat_id,
        text=welcome_text,
        attachments=[builder.as_markup()]
    )


async def show_main_menu(event, account_type):
    builder = InlineKeyboardBuilder()

    if account_type == 'abiturient':
        builder.row(
            CallbackButton(text='🧒 Абитуриентам', payload="abiturient"),
            CallbackButton(text='👨‍🎓 Студентам', payload="student"))
        menu_text = "🎓 Меню абитуриента"
    elif account_type == 'student':
        builder.row(
            CallbackButton(text='👨‍🎓 Студентам', payload="student"),
            CallbackButton(text='🧒 Абитуриентам', payload="abiturient"))
        menu_text = "📚 Меню студента"
    elif account_type == 'teacher':
        builder.row(
            CallbackButton(text='👨‍🏫 Преподавателям', payload="teacher"),
            CallbackButton(text='👨‍🎓 Студентам', payload="student"))
        menu_text = "🏫 Меню преподавателя"
    elif account_type == 'director':
        builder.row(
            CallbackButton(text='👨‍💻 Администраторам', payload="director"),
            CallbackButton(text='👨‍🏫 Преподавателям', payload="teacher"))
        menu_text = "💼 Меню администратора"
    else:
        builder.row(
            CallbackButton(text='🧒 Абитуриентам', payload="abiturient"),
            CallbackButton(text='👨‍🎓 Студентам', payload="student"))
        builder.row(
            CallbackButton(text='👨‍🏫 Преподавателям', payload="teacher"),
            CallbackButton(text='👨‍💻 Администраторам', payload="director"))
        menu_text = "🏛️ Главное меню"

    builder.row(CallbackButton(
        text='🔄 Сменить роль', payload="change_account"))

    greeting = utils.greetings(event.from_user.first_name)
    full_text = f"{greeting}\n\n{menu_text}\n\nВыберите раздел:"

    if type(event) is not BotStarted:
        return await event.message.answer(
            text=full_text,
            attachments=[builder.as_markup()]
        )

    return await event.bot.send_message(
        chat_id=event.chat_id,
        text=full_text,
        attachments=[builder.as_markup()]
    )


@router.message_created(Command('profile'))
async def show_profile(event: MessageCreated):
    account_type = await utils.get_user_account_type(event.from_user.user_id)

    account_type_names = {
        'unregistered': '❌ Не зарегистрирован',
        'abiturient': '🧒 Абитуриент',
        'student': '👨‍🎓 Студент',
        'teacher': '👨‍🏫 Преподаватель',
        'director': '👨‍💻 Администратор'
    }

    profile_text = (
        f"👤 Ваш профиль\n\n"
        f"Имя: {event.from_user.first_name or 'Не указано'}\n"
        f"Фамилия: {event.from_user.last_name or 'Не указана'}\n"
        f"Роль: {account_type_names.get(account_type, 'Неизвестен')}\n"
        f"ID: {event.from_user.user_id}"
    )

    builder = InlineKeyboardBuilder()
    if account_type != 'unregistered':
        builder.row(CallbackButton(
            text='🔄 Сменить роль', payload="change_account"))
    builder.row(CallbackButton(text='⬅️ Назад', payload="main_menu"))

    await event.message.answer(
        text=profile_text,
        attachments=[builder.as_markup()]
    )


@router.message_callback(F.callback.payload.startswith("register_"))
async def handle_registration(clbck: MessageCallback):
    payload = clbck.callback.payload
    user_info = clbck.from_user

    account_types = {
        "register_abiturient": "abiturient",
        "register_student": "student",
        "register_teacher": "teacher",
        "register_director": "director"
    }

    if payload in account_types:
        account_type = account_types[payload]
        await utils.register_user(user_info, account_type)

        success_messages = {
            "abiturient": "🎉 Вы успешно зарегистрированы как абитуриент!\n\nТеперь вам доступны все функции для подготовки к поступлению.",
            "student": "🎉 Вы успешно зарегистрированы как студент!\n\nТеперь вам доступны все функции для обучения в вузе.",
            "teacher": "🎉 Вы успешно зарегистрированы как преподаватель!\n\nТеперь вам доступны все функции для работы в вузе.",
            "director": "🎉 Вы успешно зарегистрированы как администратор!\n\nТеперь вам доступны все функции для управления вузом."
        }

        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(
            text='🚀 Начать работу', payload="main_menu"))

        await clbck.message.answer(
            text=success_messages[account_type],
            attachments=[builder.as_markup()]
        )


@router.message_callback(F.callback.payload == "change_account")
async def handle_change_account(clbck: MessageCallback):
    await show_registration_menu(clbck)


@router.message_created(Command('menu'))
@router.message_callback(F.callback.payload == "main_menu")
async def handle_main_menu(clbck: MessageCallback):
    account_type = await utils.get_user_account_type(clbck.from_user.user_id)
    await show_main_menu(clbck, account_type)


@router.message_callback(F.callback.payload == "abiturient")
async def message_handler_abiturient(clbck: MessageCallback):
    builder = InlineKeyboardBuilder()
    builder.row(
        CallbackButton(text='🎓Факультеты и специальности',
                       payload="ab_faculties"),
        CallbackButton(text='📅Дни открытых дверей', payload="ab_open_doors"))
    builder.row(
        CallbackButton(text='📝Вступительные испытания', payload="ab_exams"),
        CallbackButton(text='💰Стоимость обучения', payload="ab_prices"))
    builder.row(
        CallbackButton(text='🏛Общежития', payload="ab_dorm"),
        CallbackButton(text='📞Контакты приемной комиссии',
                       payload="ab_contacts")
    )
    builder.row(
        CallbackButton(text='🆘Помощь', payload="help")
    )
    await clbck.message.answer(text='⬇️Вот основное меню⬇️', attachments=[builder.as_markup()])


@router.message_callback(F.callback.payload == "student")
async def message_handler_student(clbck: MessageCallback):
    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(
        text='📅 События и мероприятия', payload="ab_events"))
    builder.row(CallbackButton(
        text='📝 Документооборот', payload="ab_documents"))
    builder.row(CallbackButton(text='📅 Расписание', payload="ab_schedule"))
    builder.row(CallbackButton(
        text='🏛 Навигация по вузу', payload="ab_navigation"))
    builder.row(CallbackButton(text='🆘 Помощь', payload="help"))
    await clbck.message.answer(text='⬇️Вот основное меню⬇️', attachments=[builder.as_markup()])


@router.message_callback(F.callback.payload == "teacher")
async def message_handler_teacher(clbck: MessageCallback):
    builder = InlineKeyboardBuilder()
    builder.row(
        CallbackButton(text='📊Расписание занятий', payload="t_schedule"),
        CallbackButton(text='🏢Инфраструктура вуза', payload="t_infrastructure"))
    builder.row(
        CallbackButton(text='📋Нормативные документы', payload="t_documents"),
        CallbackButton(text='💼Профессиональное развитие', payload="t_development"))
    builder.row(
        CallbackButton(text='📞Экстренные контакты', payload="t_emergency"),
        CallbackButton(text='🛠Техподдержка', payload="t_support")
    )
    builder.row(
        CallbackButton(text='🆘 Помощь', payload="help")
    )
    await clbck.message.answer(text='⬇️Вот основное меню⬇️', attachments=[builder.as_markup()])


@router.message_callback(F.callback.payload == "director")
async def message_handler_director(clbck: MessageCallback):
    builder = InlineKeyboardBuilder()
    builder.row(
        CallbackButton(text='📈Аналитика и отчеты', payload="d_analytics"),
        CallbackButton(text='👥Кадровые вопросы', payload="d_hr"))
    builder.row(
        CallbackButton(text='📊Показатели эффективности', payload="d_kpi"),
        CallbackButton(text='🏫Управление подразделениями', payload="d_departments"))
    builder.row(
        CallbackButton(text='📅Календарь мероприятий', payload="d_calendar"),
        CallbackButton(text='📋Документооборот', payload="d_document_flow")
    )
    builder.row(
        CallbackButton(text='🆘 Помощь', payload="help")
    )
    await clbck.message.answer(text='⬇️Вот основное меню⬇️', attachments=[builder.as_markup()])
