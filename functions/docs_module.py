"""

Бот разработан командой The Code Factory в 2025 году
https://the-code-factory-team.github.io

"""

from functions.utils import db
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types import MessageCallback, CallbackButton, MessageCreated
from maxapi import F, Router
import sys
import json
from utils import application_sessions

sys.path.append('functions')


docs_router = Router()


@docs_router.message_callback(F.callback.payload == "ab_documents")
async def message_handler_abiturient_docs(clbck: MessageCallback):
    builder = InlineKeyboardBuilder()
    builder.row(
        CallbackButton(text='📋 Справки',
                       payload="request_certificate"),
        CallbackButton(text='📊 Статус заявок', payload="request_status")
    )
    builder.row(
        CallbackButton(text='📝 Заявления',
                       payload="application_templates"),
        CallbackButton(text='⬅️ Назад', payload="student")
    )

    await clbck.message.answer(
        text='Документооборот\n\nВыберите нужный раздел:',
        attachments=[builder.as_markup()]
    )


@docs_router.message_callback(F.callback.payload == "request_certificate")
async def request_certificate_menu(clbck: MessageCallback):
    builder = InlineKeyboardBuilder()
    builder.row(
        CallbackButton(text='🎓 Справка об обучении', payload="cert_study"),
        CallbackButton(text='🎖️ Справка в военкомат', payload="cert_military")
    )
    builder.row(
        CallbackButton(text='💰 Справка о стипендии',
                       payload="cert_scholarship"),
        CallbackButton(text='⬅️ Назад', payload="ab_documents")
    )

    await clbck.message.answer(
        text='Заказ справок\n\nВыберите тип справки:',
        attachments=[builder.as_markup()]
    )


@docs_router.message_callback(F.callback.payload.startswith("cert_"))
async def handle_certificate_request(clbck: MessageCallback):
    cert_type = clbck.callback.payload
    user_id = clbck.from_user.user_id

    cert_types = {
        "cert_study": "study_cert",
        "cert_military": "military_cert",
        "cert_scholarship": "scholarship_cert"
    }

    if cert_type in cert_types:

        db.request(
            "INSERT INTO document_requests (user_id, document_type) VALUES (?, ?)",
            [user_id, cert_types[cert_type]],
            commit=True
        )

        cert_names = {
            "cert_study": "об обучении",
            "cert_military": "в военкомат",
            "cert_scholarship": "о стипендии"
        }

        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(
            text='📊 Статус заявок', payload="request_status"))
        builder.row(CallbackButton(
            text='⬅️ В меню документов', payload="ab_documents"))

        await clbck.message.answer(
            text=f'Заявка на справку {cert_names[cert_type]} создана!\n\n'
                 f'Номер заявки: №{db.cur.lastrowid}\n'
                 f'Статус: ⏳ запрос отправлен\n\n'
                 f'Вы можете отслеживать статус в разделе "Статус заявок"',
            attachments=[builder.as_markup()]
        )


@docs_router.message_callback(F.callback.payload == "request_status")
async def show_request_status(clbck: MessageCallback):
    user_id = clbck.from_user.user_id

    cert_requests = db.request(
        "SELECT id, document_type, status, created_at FROM document_requests WHERE user_id = ? ORDER BY created_at DESC LIMIT 5",
        [user_id]
    )

    app_requests = db.request(
        "SELECT id, application_type, status, created_at, media_files FROM application_requests WHERE user_id = ? ORDER BY created_at DESC LIMIT 5",
        [user_id]
    )

    status_emojis = {
        'запрос отправлен': '⏳',
        'в работе': '🔄',
        'готов(-а)': '✅',
        'отменен(-а)': '❌',
        'принят(-а)': '✅',
        'отклонен(-а)': '❌'
    }

    doc_type_names = {
        'study_cert': 'Справка об обучении',
        'military_cert': 'Справка в военкомат',
        'scholarship_cert': 'Справка о стипендии'
    }

    app_type_names = {
        'academic_leave': 'Академотпуск',
        'transfer': 'Перевод',
        'financial_aid': 'Материальная помощь'
    }

    response_text = "Статус ваших заявок\n\n"

    if cert_requests or app_requests:
        if cert_requests:
            response_text += "Справки:\n"
            for req in cert_requests:
                req_id, doc_type, status, created_at = req
                response_text += f"№{req_id} {doc_type_names.get(doc_type, doc_type)} - {status_emojis.get(status, '')} {status}\n"

        if app_requests:
            response_text += "\nЗаявления:\n"
            for req in app_requests:
                req_id, app_type, status, created_at, media_files = req
                has_files = "📎" if media_files and media_files != "[]" else ""
                response_text += f"№{req_id} {app_type_names.get(app_type, app_type)} - {status_emojis.get(status, '')} {status} {has_files}\n"
    else:
        response_text += "У вас нет активных заявок."

    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(text='🔄 Обновить', payload="request_status"))
    builder.row(CallbackButton(
        text='⬅️ В меню документов', payload="ab_documents"))

    await clbck.message.answer(
        text=response_text,
        attachments=[builder.as_markup()]
    )


@docs_router.message_callback(F.callback.payload == "application_templates")
async def application_templates_menu(clbck: MessageCallback):
    builder = InlineKeyboardBuilder()
    builder.row(
        CallbackButton(text='📚 Академотпуск', payload="template_academic"),
        CallbackButton(text='🔄 Перевод', payload="template_transfer")
    )
    builder.row(
        CallbackButton(text='💵 Мат. помощь', payload="template_financial"),
        CallbackButton(text='⬅️ Назад', payload="ab_documents")
    )

    await clbck.message.answer(
        text='Заявления\n\nВыберите тип заявления:',
        attachments=[builder.as_markup()]
    )


@docs_router.message_callback(F.callback.payload.startswith("template_"))
async def handle_application_template(clbck: MessageCallback):
    template_type = clbck.callback.payload
    user_id = clbck.from_user.user_id

    template_types = {
        "template_academic": "academic_leave",
        "template_transfer": "transfer",
        "template_financial": "financial_aid"
    }

    template_names = {
        "template_academic": "академотпуск",
        "template_transfer": "перевод",
        "template_financial": "материальная помощь"
    }

    if template_type in template_types:
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text='✅ Подать заявление',
                    payload=f"submit_{template_types[template_type]}"))
        builder.row(CallbackButton(text='📝 Посмотреть шаблон',
                    payload=f"view_{template_types[template_type]}"))
        builder.row(CallbackButton(text='⬅️ Назад',
                    payload="application_templates"))

        await clbck.message.answer(
            text=f'Заявление на {template_names[template_type]}\n\n'
                 f'Вы можете:\n'
                 f'• Подать заявление (будет создана заявка)\n'
                 f'• Посмотреть шаблон заявления',
            attachments=[builder.as_markup()]
        )


@docs_router.message_callback(F.callback.payload.startswith("view_"))
async def view_application_template(clbck: MessageCallback):
    template_type = clbck.callback.payload.replace("view_", "")

    templates = {
        "academic_leave": "Шаблон заявления на академотпуск:\n\nПрошу предоставить мне академический отпуск с [дата] по [дата] в связи с [причина].\n\nСтудент: [ФИО]\nГруппа: [номер группы]",
        "transfer": "Шаблон заявления на перевод:\n\nПрошу перевести меня с [специальность] на [специальность] с [дата].\n\nСтудент: [ФИО]\nГруппа: [номер группы]",
        "financial_aid": "Шаблон заявления на материальную помощь:\n\nПрошу предоставить мне материальную помощь в связи с [причина].\n\nСтудент: [ФИО]\nГруппа: [номер группы]"
    }

    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(text='✅ Подать заявление',
                payload=f"submit_{template_type}"))
    builder.row(CallbackButton(text='⬅️ Назад',
                payload="application_templates"))

    await clbck.message.answer(
        text=templates.get(template_type, "Шаблон не найден."),
        attachments=[builder.as_markup()]
    )


@docs_router.message_callback(F.callback.payload.startswith("submit_"))
async def submit_application(clbck: MessageCallback):
    app_type = clbck.callback.payload.replace("submit_", "")
    user_id = clbck.from_user.user_id

    application_sessions[user_id] = {
        'type': app_type,
        'media_files': []
    }

    app_type_names = {
        "academic_leave": "академотпуск",
        "transfer": "перевод",
        "financial_aid": "материальную помощь"
    }

    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(text='📎 Прикрепить файлы',
                payload=f"attach_files_{app_type}"))
    builder.row(CallbackButton(text='❌ Отменить',
                payload="application_templates"))

    await clbck.message.answer(
        text=f'Подача заявления на {app_type_names.get(app_type, app_type)}\n\n'
             f'Для подачи заявления необходимо прикрепить файл:\n'
             f'• 📸 Фотография заполненного заявления\n'
             f'• 📄 Скан документа\n'
             f'• 🖼️ Изображение с подписью\n\n'
             f'Инструкция:\n'
             f'1. Нажмите "Прикрепить файлы"\n'
             f'2. Отправьте фото или скан заявления\n'
             f'3. Нажмите "✅ Отправить заявление"',
        attachments=[builder.as_markup()]
    )


@docs_router.message_callback(F.callback.payload.startswith("attach_files_"))
async def start_file_attachment(clbck: MessageCallback):
    app_type = clbck.callback.payload.replace("attach_files_", "")
    user_id = clbck.from_user.user_id

    if user_id not in application_sessions:
        application_sessions[user_id] = {
            'type': app_type,
            'media_files': []
        }

    builder = InlineKeyboardBuilder()

    if application_sessions[user_id]['media_files']:
        builder.row(CallbackButton(text='✅ Отправить заявление',
                    payload=f"finish_{app_type}"))

    builder.row(CallbackButton(text='❌ Отменить',
                payload="application_templates"))

    file_count = len(application_sessions[user_id]["media_files"])

    await clbck.message.answer(
        text='Прикрепление файлов\n\n'
             'Отправьте фото или скан вашего заявления.\n'
             'Это обязательное требование для подачи заявления.\n\n'
             f'Прикреплено файлов: {file_count}',
        attachments=[builder.as_markup()]
    )


@docs_router.message_created(F.message.body.attachments)
async def handle_media_message(event: MessageCreated):
    user_id = event.from_user.user_id

    if user_id not in application_sessions:
        return

    media_files = []
    for attachment in event.message.body.attachments:
        if hasattr(attachment, 'payload') and hasattr(attachment.payload, 'token'):
            file_info = {
                'media_id': attachment.payload.token,
                'type': attachment.type,
                'url': getattr(attachment.payload, 'url', ''),
            }

            if attachment.type == 'file' and hasattr(attachment, 'filename'):
                file_info['filename'] = attachment.filename
                file_info['size'] = getattr(attachment, 'size', 0)
            elif attachment.type == 'image' and hasattr(attachment.payload, 'photo_id'):
                file_info['photo_id'] = attachment.payload.photo_id

            media_files.append(file_info)

    if not media_files:
        return

    application_sessions[user_id]['media_files'].extend(media_files)

    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(text='✅ Отправить заявление',
                payload=f"finish_{application_sessions[user_id]['type']}"))
    builder.row(CallbackButton(text='📎 Добавить ещё файлов',
                payload=f"attach_files_{application_sessions[user_id]['type']}"))
    builder.row(CallbackButton(text='❌ Отменить',
                payload="application_templates"))

    file_count = len(application_sessions[user_id]["media_files"])

    file_info_text = ""
    for i, file_data in enumerate(application_sessions[user_id]["media_files"][-5:], 1):
        file_type_emoji = "📄" if file_data['type'] == 'file' else "🖼️"
        file_name = file_data.get('filename', f'файл_{i}')
        file_info_text += f"{file_type_emoji} {file_name}\n"

    if file_count > 5:
        file_info_text += f"... и еще {file_count - 5} файлов\n"

    await event.message.answer(
        text=f'Файл успешно прикреплен!\n\n'
             f'Прикреплено файлов: {file_count}\n\n'
             f'Последние файлы:\n{file_info_text}\n'
             f'Теперь вы можете отправить заявление.',
        attachments=[builder.as_markup()]
    )


@docs_router.message_created()
async def handle_message_in_session(event: MessageCreated):
    user_id = event.from_user.user_id

    if user_id not in application_sessions:
        return

    if (not event.message.body.attachments or len(event.message.body.attachments) == 0) and not event.message.body.text.startswith('/'):
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text='📎 Прикрепить файлы',
                    payload=f"attach_files_{application_sessions[user_id]['type']}"))
        builder.row(CallbackButton(text='❌ Отменить',
                    payload="application_templates"))

        await event.message.answer(
            text='Пожалуйста, прикрепите файл с заявлением.\n\n'
                 'Отправьте фото или скан вашего заявления.\n'
                 'Поддерживаемые форматы:\n'
                 '• 📸 Фотографии (JPG, PNG)\n'
                 '• 📄 Документы (PDF, Word)\n'
                 '• 📊 Другие файлы',
            attachments=[builder.as_markup()]
        )


@docs_router.message_callback(F.callback.payload.startswith("finish_"))
async def finish_application(clbck: MessageCallback):
    app_type = clbck.callback.payload.replace("finish_", "")
    user_id = clbck.from_user.user_id

    if user_id not in application_sessions or not application_sessions[user_id]['media_files']:
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text='📎 Прикрепить файлы',
                    payload=f"attach_files_{app_type}"))
        builder.row(CallbackButton(text='❌ Отменить',
                    payload="application_templates"))

        await clbck.message.answer(
            text='Нельзя отправить заявление без файла!\n\n'
                 'Пожалуйста, прикрепите фото или скан вашего заявления.',
            attachments=[builder.as_markup()]
        )
        return

    media_files = application_sessions[user_id]['media_files']
    del application_sessions[user_id]

    media_files_json = json.dumps(media_files)

    db.request(
        "INSERT INTO application_requests (user_id, application_type, media_files) VALUES (?, ?, ?)",
        [user_id, app_type, media_files_json],
        commit=True
    )

    app_type_names = {
        "academic_leave": "академотпуск",
        "transfer": "перевод",
        "financial_aid": "материальную помощь"
    }

    request_id = db.cur.lastrowid

    file_types = {}
    for file_data in media_files:
        file_type = file_data['type']
        file_types[file_type] = file_types.get(file_type, 0) + 1

    file_info = ""
    for file_type, count in file_types.items():
        if file_type == 'image':
            file_info += f"📸 Фото: {count}\n"
        elif file_type == 'file':
            file_info += f"📄 Документы: {count}\n"
        else:
            file_info += f"📁 Файлы ({file_type}): {count}\n"

    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(
        text='📊 Статус заявок', payload="request_status"))
    builder.row(CallbackButton(text='📝 Новое заявление',
                payload="application_templates"))

    await clbck.message.answer(
        text=f'Заявление на {app_type_names.get(app_type, app_type)} подано!\n\n'
             f'Номер заявки: №{request_id}\n'
             f'Прикреплено файлов: {len(media_files)}\n'
             f'{file_info}'
             f'Статус: ⏳ запрос отправлен\n\n'
             f'Вы можете отслеживать статус в разделе "Статус заявок"',
        attachments=[builder.as_markup()]
    )
