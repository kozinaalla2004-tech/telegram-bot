import sys
import traceback

# Логирование ошибок для Render
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    print(f"❌ CRITICAL ERROR: {exc_type.__name__}: {exc_value}")
    traceback.print_exception(exc_type, exc_value, exc_traceback)

sys.excepthook = handle_exception
import asyncio
import random
import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.session.aiohttp import AiohttpSession
from datetime import datetime, timedelta

# === ЛОГИРОВАНИЕ ===
logging.basicConfig(level=logging.INFO)

# === НАСТРОЙКИ ===
API_TOKEN = "8292643567:AAFIrZdrCgdIVAJhMPorHuRZ24c44RGwO9Q"  # ← Вставь свой токен
ADMIN_ID = 983562369  # ← Твой ID

session = AiohttpSession(timeout=60)
bot = Bot(token=API_TOKEN, session=session)
dp = Dispatcher()

# === FILE_ID ФОТО (мгновенная отправка!) ===
# ↓↓↓ ВСТАВЬ СЮДА file_id ИЗ JSON (самый последний, начинается с BQAC...) ↓↓↓
PHOTO_START_FILE_ID = 'BQACAgIAAxkDAA..._2AMSHKYczs6BA'  # ← ЗАМЕНИ НА СВОЙ ПОЛНЫЙ file_id!

# === БАЗА ПОЛЬЗОВАТЕЛЕЙ ===
users_data = {}

# === ЗАДАНИЯ НА ДЕНЬ (20 штук) ===
daily_tasks = [
    {"text": "📝 Откликнись на 3 вакансии сегодня", "xp": 30},
    {"text": "🎓 Изучи новый навык (30 минут)", "xp": 25},
    {"text": "💼 Обнови своё резюме", "xp": 35},
    {"text": "🤝 Напиши бывшему коллеге или одногруппнику", "xp": 20},
    {"text": "📚 Прочитай статью по своей профессии", "xp": 15},
    {"text": "🎯 Определи 3 карьерные цели на месяц", "xp": 25},
    {"text": "💡 Пройди один профориентационный тест", "xp": 30},
    {"text": "📧 Напиши сопроводительное письмо для мечты", "xp": 40},
    {"text": "🔍 Изучи 5 компаний, где хочешь работать", "xp": 20},
    {"text": "🗣️ Потренируйся отвечать на вопросы на собеседовании", "xp": 25},
    {"text": "✍️ Напиши пост о своём профессиональном пути", "xp": 30},
    {"text": "🎬 Посмотри вебинар по твоей специальности", "xp": 35},
    {"text": "📊 Проанализируй свои сильные и слабые стороны", "xp": 20},
    {"text": "🌐 Найди 3 профессиональных сообщества в соцсетях", "xp": 15},
    {"text": "📞 Позвони ментору или наставнику", "xp": 25},
    {"text": "📋 Составь план развития на ближайший квартал", "xp": 40},
    {"text": "🎨 Создай или обнови портфолио", "xp": 45},
    {"text": "💬 Напиши отзыв о курсе/книге по профессии", "xp": 20},
    {"text": "🔗 Добавь 5 новых контактов в LinkedIn/Telegram", "xp": 30},
    {"text": "🧘 Практикуй самопрезентацию перед зеркалом (2 мин)", "xp": 15},
]

# === ВАКАНСИИ (10 штук) ===
vacancies = [
    {"title": "SMM-менеджер", "company": "Digital Agency", "desc": "Ведение соцсетей, создание контента, работа с блогерами", "link": "https://hh.ru", "salary": "60-90 тыс. ₽"},
    {"title": "Python-разработчик", "company": "TechStart", "desc": "Разработка ботов, парсеров, работа с API", "link": "https://hh.ru", "salary": "80-120 тыс. ₽"},
    {"title": "HR-ассистент", "company": "HR Pro", "desc": "Помощь в подборе персонала, проведение собеседований", "link": "https://hh.ru", "salary": "50-70 тыс. ₽"},
    {"title": "Контент-менеджер", "company": "Media House", "desc": "Наполнение сайта и соцсетей, работа с CMS", "link": "https://hh.ru", "salary": "45-65 тыс. ₽"},
    {"title": "Графический дизайнер", "company": "Creative Studio", "desc": "Дизайн для соцсетей и веба, работа в Figma", "link": "https://hh.ru", "salary": "70-100 тыс. ₽"},
    {"title": "Маркетолог-аналитик", "company": "Growth Lab", "desc": "Анализ рекламных кампаний, работа с метриками", "link": "https://hh.ru", "salary": "75-110 тыс. ₽"},
    {"title": "Технический писатель", "company": "DocuTech", "desc": "Написание документации, инструкций, гайдов", "link": "https://hh.ru", "salary": "55-80 тыс. ₽"},
    {"title": "Project Manager", "company": "Agile Team", "desc": "Управление проектами, координация команды", "link": "https://hh.ru", "salary": "90-140 тыс. ₽"},
    {"title": "UX/UI дизайнер", "company": "Design Hub", "desc": "Проектирование интерфейсов, пользовательские сценарии", "link": "https://hh.ru", "salary": "85-130 тыс. ₽"},
    {"title": "Data Analyst", "company": "DataFlow", "desc": "Анализ данных, визуализация, отчёты", "link": "https://hh.ru", "salary": "95-150 тыс. ₽"},
]

# === ПОЛЕЗНЫЕ СОВЕТЫ (для еженедельной рассылки) ===
weekly_tips = [
    "💡 <b>Лайфхак недели:</b> Откликайся на вакансии до 10 утра — рекрутеры чаще смотрят резюме в начале дня!",
    "💡 <b>Лайфхак недели:</b> Добавляй цифры в резюме — «увеличил охват на 40%» работает лучше, чем «работал с охватом».",
    "💡 <b>Лайфхак недели:</b> Исследуй компанию перед собеседованием — задавай умные вопросы о продукте и команде.",
    "💡 <b>Лайфхак недели:</b> Нетворкинг важнее резюме — 70% вакансий закрываются по рекомендациям.",
    "💡 <b>Лайфхак недели:</b> Делай паузы в поиске работы — выгорание снижает качество откликов.",
    "💡 <b>Лайфхак недели:</b> Сохраняй все отказы — анализируй, что можно улучшить в следующем отклике.",
    "💡 <b>Лайфхак недели:</b> Создай шаблон сопроводительного — адаптируй его под каждую вакансию за 5 минут.",
    "💡 <b>Лайфхак недели:</b> Обновляй резюме каждые 3 месяца — даже если не ищешь работу активно.",
]

# === ДОСТИЖЕНИЯ ===
achievements = {
    "first_start": "🐣 Первый шаг",
    "first_task": "✅ Дело сделано",
    "first_feedback": "💬 Голос услышан",
    "first_match": "🎯 Первый отклик",
    "week_streak": "🔥 Неделя в игре",
    "interview_pass": "🎤 Собеседование пройдено",
    "weekly_reader": "📚 Любитель советов",
}

# === НАВЫКИ (шаблонные) ===
template_skills = [
    "💬 Коммуникация",
    "🤝 Работа в команде",
    "⏰ Тайм-менеджмент",
    "🐍 Python",
    "🇬🇧 Английский",
    "📊 Excel",
    "🎨 Дизайн",
    "📈 Аналитика",
    "🎯 Лидерство",
    "💡 Креативность",
]

# === УРОВНИ НАВЫКОВ ===
skill_levels = {
    1: "🌱 Новичок",
    2: "📚 Изучаю",
    3: "💪 Практикую",
    4: "🎯 Продвинутый",
    5: "🏆 Эксперт"
}

# === ТЕСТ ПРОФОРИЕНТАЦИИ ===
career_test_questions = [
    {
        "question": "Что тебе нравится больше?",
        "options": [
            {"text": "Работать с людьми", "type": "social"},
            {"text": "Работать с данными", "type": "analytical"},
            {"text": "Создавать что-то новое", "type": "creative"},
            {"text": "Управлять процессами", "type": "managerial"},
        ]
    },
    {
        "question": "Как ты предпочитаешь работать?",
        "options": [
            {"text": "В команде", "type": "social"},
            {"text": "Самостоятельно", "type": "analytical"},
            {"text": "В свободном режиме", "type": "creative"},
            {"text": "С чётким планом", "type": "managerial"},
        ]
    },
    {
        "question": "Что для тебя важнее?",
        "options": [
            {"text": "Помогать другим", "type": "social"},
            {"text": "Находить закономерности", "type": "analytical"},
            {"text": "Выражать себя", "type": "creative"},
            {"text": "Достигать целей", "type": "managerial"},
        ]
    },
]

career_test_results = {
    "social": {"title": "🤝 Социальный тип", "desc": "Тебе подходит работа с людьми!", "professions": ["HR-менеджер", "Психолог", "Учитель", "Коуч"]},
    "analytical": {"title": "📊 Аналитический тип", "desc": "Тебе подходит работа с данными!", "professions": ["Аналитик", "Программист", "Финансист", "Data Scientist"]},
    "creative": {"title": "🎨 Креативный тип", "desc": "Тебе подходит творческая работа!", "professions": ["Дизайнер", "Копирайтер", "Маркетолог", "Режиссёр"]},
    "managerial": {"title": "🎯 Управленческий тип", "desc": "Тебе подходит руководящая работа!", "professions": ["Менеджер проектов", "Директор", "Предприниматель", "Team Lead"]},
}

# === ВОПРОСЫ ДЛЯ СОБЕСЕДОВАНИЯ ===
interview_questions = [
    {
        "question": "Расскажите немного о себе",
        "tips": "Говори 2-3 минуты, сосредоточься на профессиональном опыте",
        "keywords": ["опыт", "образование", "работа", "интерес", "цель", "навык"]
    },
    {
        "question": "Почему вы хотите работать именно у нас?",
        "tips": "Покажи, что изучил компанию и разделяешь её ценности",
        "keywords": ["компания", "ценности", "продукт", "культура", "развитие", "интерес"]
    },
    {
        "question": "Назовите ваши сильные стороны",
        "tips": "Приводи конкретные примеры, как эти качества помогали в работе",
        "keywords": ["сильный", "навык", "умение", "опыт", "пример", "результат"]
    },
    {
        "question": "Назовите ваши слабые стороны",
        "tips": "Называй реальную слабость + как работаешь над ней",
        "keywords": ["работаю", "улучшаю", "учусь", "развиваюсь", "практика"]
    },
    {
        "question": "Кем вы видите себя через 5 лет?",
        "tips": "Покажи амбиции, но будь реалистом",
        "keywords": ["развитие", "рост", "цель", "карьера", "профессионал", "эксперт"]
    },
]

# === ГЕНЕРАТОР СОПРОВОДИТЕЛЬНЫХ ПИСЕМ ===
def generate_cover_letter(name, position, company, skills, contact, experience=""):
    letter = f"""<b>Тема:</b> Отклик на вакансию "{position}"

<b>Уважаемая команда {company}!</b>

Меня зовут {name}, и я хочу откликнуться на вакансию <b>"{position}"</b>.

{experience if experience else "Я считаю, что мой опыт и навыки соответствуют требованиям этой позиции."}

<b>Мои ключевые навыки:</b>
{chr(10).join([f"• {skill}" for skill in skills])}

<b>Почему я хочу работать у вас:</b>
Меня привлекает возможность развиваться в {company} и применять свои навыки для решения интересных задач.

<b>Что я могу предложить:</b>
• Готовность к обучению и развитию
• Ответственный подход к работе
• Умение работать в команде
• {skills[0] if skills else "Профессионализм"}

<b>Контакты для связи:</b>
{contact}

С уважением и готовностью к сотрудничеству,
{name}

---
<i>Письмо сгенерировано ботом Ворон Кар 🖤</i>"""
    return letter

# === КЛАВИАТУРЫ ===
def get_main_keyboard():
    kb = [
        [KeyboardButton(text="💼 Вакансии"), KeyboardButton(text="📋 Задание дня")],
        [KeyboardButton(text="🧪 Тесты"), KeyboardButton(text="🏆 Мой прогресс")],
        [KeyboardButton(text="📄 Резюме"), KeyboardButton(text="🛠️ Навыки")],
        [KeyboardButton(text="🎤 Собеседование"), KeyboardButton(text="✉️ Сопроводительное")],
        [KeyboardButton(text="📬 Полезное"), KeyboardButton(text="💬 Обратная связь")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_vacancy_keyboard(vac_id):
    kb = [
        [InlineKeyboardButton(text="❌ Не подходит", callback_data=f"vac_dislike_{vac_id}")],
        [InlineKeyboardButton(text="✅ Подходит", callback_data=f"vac_like_{vac_id}")],
        [InlineKeyboardButton(text="⏭️ Далее", callback_data="vac_next")],
        [InlineKeyboardButton(text="🛑 Стоп", callback_data="vac_stop")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_task_keyboard(task_id):
    kb = [
        [InlineKeyboardButton(text="✅ Выполнил!", callback_data=f"task_complete_{task_id}")],
        [InlineKeyboardButton(text="🔄 Другое", callback_data="task_new")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_feedback_keyboard():
    kb = [
        [InlineKeyboardButton(text="📝 Написать отзыв", callback_data="feedback_text")],
        [InlineKeyboardButton(text="📩 Написать в ЛС", url="https://t.me/cheerryplum")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_test_keyboard():
    kb = [
        [InlineKeyboardButton(text="🧪 Пройти тест", callback_data="test_start")],
        [InlineKeyboardButton(text="📊 Мои результаты", callback_data="test_results")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_resume_keyboard():
    kb = [
        [InlineKeyboardButton(text="📋 Чек-лист", callback_data="resume_checklist")],
        [InlineKeyboardButton(text="✅ Отметить пункт", callback_data="resume_mark")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_skills_main_keyboard():
    kb = [
        [InlineKeyboardButton(text="📊 Мои навыки", callback_data="skills_list")],
        [InlineKeyboardButton(text="➕ Добавить шаблонный", callback_data="skills_add_template")],
        [InlineKeyboardButton(text="✨ Добавить свой", callback_data="skills_add_custom")],
        [InlineKeyboardButton(text="⬆️ Прокачать навык", callback_data="skills_level_up")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_interview_keyboard():
    kb = [
        [InlineKeyboardButton(text="🎤 Начать практику", callback_data="interview_start")],
        [InlineKeyboardButton(text="💡 Советы", callback_data="interview_tips_list")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_cover_letter_keyboard():
    kb = [
        [InlineKeyboardButton(text="✏️ Создать письмо", callback_data="cover_create")],
        [InlineKeyboardButton(text="📋 Шаблоны", callback_data="cover_templates")],
        [InlineKeyboardButton(text="💡 Как заполнить", callback_data="cover_help")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

# === ФУНКЦИИ ===
def get_user_data(user_id):
    if user_id not in users_data:
        users_data[user_id] = {
            "xp": 0, "level": 1, "tasks_completed": 0,
            "achievements": [], "streak": 0, "last_visit": None,
            "current_vacancy": 0, "matched_vacancies": [],
            "completed_tasks": [], "waiting_feedback": False, "username": None,
            "test_result": None, "resume_checklist": [False]*8,
            "skills": {},
            "custom_skills": [],
            "interview_completed": 0,
            "last_streak_check": None,
            "cover_letter_data": {},
            "last_weekly_tip": None  # Для еженедельной рассылки
        }
    return users_data[user_id]

def add_xp(user_id, amount):
    user = get_user_data(user_id)
    user["xp"] += amount
    new_level = (user["xp"] // 100) + 1
    if new_level > user["level"]:
        user["level"] = new_level
        return True
    return False

def check_streak(user_id):
    user = get_user_data(user_id)
    today = datetime.now().date()
    
    if user["last_streak_check"] is None:
        user["streak"] = 1
        user["last_streak_check"] = today
        return 1
    
    last_check = user["last_streak_check"]
    days_diff = (today - last_check).days
    
    if days_diff == 0:
        return user["streak"]
    elif days_diff == 1:
        user["streak"] += 1
        user["last_streak_check"] = today
        if user["streak"] == 7 and "week_streak" not in user["achievements"]:
            user["achievements"].append("week_streak")
            add_xp(user_id, 100)
        return user["streak"]
    else:
        user["streak"] = 1
        user["last_streak_check"] = today
        return 1

async def send_to_admin(text):
    try:
        await bot.send_message(ADMIN_ID, text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Ошибка: {e}")

async def send_weekly_tip(user_id):
    """Отправляет еженедельный полезный совет"""
    user = get_user_data(user_id)
    today = datetime.now().date()
    
    # Проверяем, прошло ли 7 дней с последнего совета
    if user["last_weekly_tip"] is None or (today - user["last_weekly_tip"]).days >= 7:
        tip = random.choice(weekly_tips)
        
        try:
            await bot.send_message(user_id, tip, parse_mode="HTML")
            user["last_weekly_tip"] = today
            add_xp(user_id, 10)  # +10 XP за прочтение совета
            
            if "weekly_reader" not in user["achievements"]:
                user["achievements"].append("weekly_reader")
                add_xp(user_id, 25)
            
            logging.info(f"✅ Еженедельный совет отправлен пользователю {user_id}")
        except Exception as e:
            logging.warning(f"⚠️ Не удалось отправить совет: {e}")

# === ОБРАБОТЧИКИ ===

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user = get_user_data(user_id)
    name = message.from_user.first_name
    
    streak = check_streak(user_id)
    streak_bonus = f"\n\n🔥 <b>Твой стрик:</b> {streak} дней подряд!" if streak > 1 else ""
    
    if user["last_visit"] is None:
        user["achievements"].append("first_start")
        add_xp(user_id, 50)
        user["username"] = name
        await send_to_admin(f"🆕 Новый пользователь: {name} (ID: {user_id})")
    
    user["last_visit"] = message.date
    user["current_vacancy"] = 0
    user["cover_letter_data"] = {}
    user["interview_mode"] = False
    
    # === СООБЩЕНИЕ 1: Приветствие + ФОТО ===
    text1 = (
        f"Привет, {name}! 🖤\n\n"
        f"<b>Я Ворон Кар</b> — твой карьерный наставник!"
    )
    
    try:
        await message.answer_photo(
            photo=PHOTO_START_FILE_ID,
            caption=text1,
            parse_mode="HTML"
        )
        logging.info("✅ Фото отправлено")
    except Exception as e:
        logging.warning(f"⚠️ Фото не отправлено: {e}")
        await message.answer(text1, parse_mode="HTML")
    
    await asyncio.sleep(0.5)  # Ждём 0.5 секунды
    
    # === СООБЩЕНИЕ 2: История Ворона ===
    text2 = (
        f"Я — ворон, и я знаю, каково это: быть запутанным...\n\n"
        f"Но я прошёл этот путь и теперь стал экспертом! 🎯\n\n"
        f"Теперь я помогаю таким же, как ты.{streak_bonus}"
    )
    await message.answer(text2, parse_mode="HTML")
    
    await asyncio.sleep(0.5)  # Ждём 0.5 секунды
    
    # === СООБЩЕНИЕ 3: Что есть в боте + КНОПКИ ===
    text3 = (
        f"<b>В этом боте ты можешь:</b>\n\n"
        f"💼 <b>Найти вакансии</b>\n"
        f"📋 <b>Получать задания</b>\n"
        f"🧪 <b>Пройти тесты</b>\n"
        f"🏆 <b>Отслеживать прогресс</b>\n"
        f"📄 <b>Создать резюме</b>\n"
        f"🛠️ <b>Трекер навыков</b>\n"
        f"🎤 <b>Симулятор собеседования</b>\n"
        f"✉️ <b>Сопроводительное письмо</b>\n"
        f"📬 <b>Полезное</b>\n"
        f"💬 <b>Обратная связь</b>\n\n"
        f"Выбирай раздел в меню 👇"
    )
    
    await message.answer(text3, reply_markup=get_main_keyboard(), parse_mode="HTML")
    
    # Проверяем, нужно ли отправить еженедельный совет
    await send_weekly_tip(user_id)
    
    logging.info(f"✅ Start от {name} (3 сообщения отправлены)")

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    total = len(users_data)
    active = sum(1 for u in users_data.values() if u["last_visit"])
    total_xp = sum(u["xp"] for u in users_data.values())
    
    text = (
        f"🖤 <b>Админ-панель</b>\n\n"
        f"👥 Пользователей: {total}\n"
        f"🔥 Активных: {active}\n"
        f"⚡ XP выдано: {total_xp}\n"
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text == "💼 Вакансии")
async def btn_vacancies(message: types.Message):
    user = get_user_data(message.from_user.id)
    
    if user["current_vacancy"] >= len(vacancies):
        await message.answer("🎉 <b>Все вакансии просмотрены!</b>", parse_mode="HTML")
        return
    
    vac = vacancies[user["current_vacancy"]]
    text = (
        f"💼 <b>{vac['title']}</b>\n"
        f"🏢 {vac['company']}\n"
        f"💰 {vac['salary']}\n\n"
        f"📝 {vac['desc']}"
    )
    
    await message.answer(text, reply_markup=get_vacancy_keyboard(user["current_vacancy"]), parse_mode="HTML")

@dp.callback_query(F.data.startswith("vac_like_"))
async def cb_vac_like(callback: types.CallbackQuery):
    user = get_user_data(callback.from_user.id)
    vac_id = int(callback.data.split("_")[2])
    vac = vacancies[vac_id]
    
    if vac_id not in user["matched_vacancies"]:
        user["matched_vacancies"].append(vac_id)
        if "first_match" not in user["achievements"]:
            user["achievements"].append("first_match")
            add_xp(callback.from_user.id, 50)
    
    add_xp(callback.from_user.id, 20)
    
    await callback.message.edit_text(
        f"✅ <b>Отлично!</b>\n\n"
        f"{vac['title']} в {vac['company']}\n\n"
        f"🔗 <a href='{vac['link']}'>Открыть на hh.ru</a>\n\n"
        f"⚡ +20 XP",
        parse_mode="HTML"
    )
    await callback.answer()
    
    await asyncio.sleep(2)
    user["current_vacancy"] += 1
    await btn_vacancies(callback.message)

@dp.callback_query(F.data.startswith("vac_dislike_"))
async def cb_vac_dislike(callback: types.CallbackQuery):
    user = get_user_data(callback.from_user.id)
    add_xp(callback.from_user.id, 5)
    await callback.message.edit_text("👎 Пропущено...", parse_mode="HTML")
    await callback.answer()
    await asyncio.sleep(1)
    user["current_vacancy"] += 1
    await btn_vacancies(callback.message)

@dp.callback_query(F.data == "vac_next")
async def cb_vac_next(callback: types.CallbackQuery):
    user = get_user_data(callback.from_user.id)
    user["current_vacancy"] += 1
    await callback.message.delete()
    await btn_vacancies(callback.message)
    await callback.answer()

@dp.callback_query(F.data == "vac_stop")
async def cb_vac_stop(callback: types.CallbackQuery):
    user = get_user_data(callback.from_user.id)
    await callback.message.edit_text(
        f"🛑 <b>Остановлено!</b>\n\n"
        f"💕 В избранном: {len(user['matched_vacancies'])}\n"
        f"👀 Посмотрено: {user['current_vacancy'] + 1}",
        parse_mode="HTML"
    )
    await callback.answer("Остановлено! 🖤")

@dp.message(F.text == "📋 Задание дня")
async def btn_tasks(message: types.Message):
    user = get_user_data(message.from_user.id)
    available = [i for i in range(len(daily_tasks)) if i not in user["completed_tasks"]]
    
    if not available:
        await message.answer("🎉 <b>Все задания выполнены!</b>\n\nЗаходи завтра за новыми!", parse_mode="HTML")
        return
    
    task_id = random.choice(available)
    task = daily_tasks[task_id]
    text = f"📋 <b>Задание:</b>\n\n{task['text']}\n\n⚡ +{task['xp']} XP"
    
    await message.answer(text, reply_markup=get_task_keyboard(task_id), parse_mode="HTML")

@dp.callback_query(F.data.startswith("task_complete_"))
async def cb_task_complete(callback: types.CallbackQuery):
    user = get_user_data(callback.from_user.id)
    task_id = int(callback.data.split("_")[2])
    task = daily_tasks[task_id]
    
    if task_id in user["completed_tasks"]:
        await callback.answer("Уже выполнено!", show_alert=True)
        return
    
    user["completed_tasks"].append(task_id)
    user["tasks_completed"] += 1
    add_xp(callback.from_user.id, task["xp"])
    
    if "first_task" not in user["achievements"]:
        user["achievements"].append("first_task")
        add_xp(callback.from_user.id, 50)
    
    await callback.message.edit_text(
        f"✅ <b>Выполнено!</b>\n\n"
        f"+{task['xp']} XP",
        parse_mode="HTML"
    )
    await callback.answer(f"+{task['xp']} XP!")

@dp.callback_query(F.data == "task_new")
async def cb_task_new(callback: types.CallbackQuery):
    await callback.message.delete()
    await btn_tasks(callback.message)
    await callback.answer()

@dp.message(F.text == "🧪 Тесты")
async def btn_tests(message: types.Message):
    user = get_user_data(message.from_user.id)
    
    if user.get("test_result"):
        result = career_test_results.get(user["test_result"], {})
        text = (
            f"🧪 <b>Твой результат:</b>\n\n"
            f"<b>{result.get('title', '')}</b>\n"
            f"{result.get('desc', '')}\n\n"
            f"<b>Подходящие профессии:</b>\n" +
            "\n".join([f"• {p}" for p in result.get('professions', [])]) +
            "\n\n🔁 Пройти заново?"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔄 Пройти ещё раз", callback_data="test_start")]])
    else:
        text = (
            "🧪 <b>Тест профориентации</b>\n\n"
            "Ответь на 3 вопроса и узнай, какая профессия тебе подходит!\n\n"
            "⏱️ Время: 2 минуты\n"
            "⚡ Награда: 100 XP"
        )
        kb = get_test_keyboard()
    
    await message.answer(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data == "test_start")
async def cb_test_start(callback: types.CallbackQuery):
    user = get_user_data(callback.from_user.id)
    user["test_answers"] = []
    user["test_current"] = 0
    
    question = career_test_questions[0]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=opt["text"], callback_data=f"test_ans_{opt['type']}")]
        for opt in question["options"]
    ])
    
    await callback.message.edit_text(
        f"🧪 <b>Вопрос 1/3</b>\n\n"
        f"{question['question']}",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("test_ans_"))
async def cb_test_answer(callback: types.CallbackQuery):
    user = get_user_data(callback.from_user.id)
    answer_type = callback.data.split("_")[2]
    
    user["test_answers"].append(answer_type)
    user["test_current"] += 1
    
    if user["test_current"] >= len(career_test_questions):
        counts = {}
        for ans in user["test_answers"]:
            counts[ans] = counts.get(ans, 0) + 1
        result_type = max(counts, key=counts.get)
        user["test_result"] = result_type
        add_xp(callback.from_user.id, 100)
        
        result = career_test_results[result_type]
        text = (
            f"🎉 <b>Тест завершён!</b>\n\n"
            f"<b>{result['title']}</b>\n"
            f"{result['desc']}\n\n"
            f"<b>Подходящие профессии:</b>\n" +
            "\n".join([f"• {p}" for p in result['professions']]) +
            f"\n\n⚡ +100 XP"
        )
        await callback.message.edit_text(text, parse_mode="HTML")
    else:
        question = career_test_questions[user["test_current"]]
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=opt["text"], callback_data=f"test_ans_{opt['type']}")]
            for opt in question["options"]
        ])
        await callback.message.edit_text(
            f"🧪 <b>Вопрос {user['test_current']+1}/3</b>\n\n"
            f"{question['question']}",
            reply_markup=kb,
            parse_mode="HTML"
        )
    
    await callback.answer()

@dp.callback_query(F.data == "test_results")
async def cb_test_results(callback: types.CallbackQuery):
    await btn_tests(callback.message)
    await callback.answer()

@dp.message(F.text == "🏆 Мой прогресс")
async def btn_progress(message: types.Message):
    user = get_user_data(message.from_user.id)
    
    achievements_list = "\n".join([achievements[a] for a in user["achievements"]]) if user["achievements"] else "Пока нет"
    
    text = (
        f"🏆 <b>Твой прогресс:</b>\n\n"
        f"📊 <b>Уровень:</b> {user['level']}\n"
        f"⚡ <b>XP:</b> {user['xp']} / {user['level'] * 100}\n"
        f"🔥 <b>Стрик:</b> {user['streak']} дней\n"
        f"✅ <b>Заданий:</b> {user['tasks_completed']}\n"
        f"💕 <b>Вакансий:</b> {len(user['matched_vacancies'])}\n\n"
        f"🏅 <b>Достижения:</b>\n{achievements_list}"
    )
    
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text == "📄 Резюме")
async def btn_resume(message: types.Message):
    user = get_user_data(message.from_user.id)
    
    checklist_items = [
        "📸 Фотография добавлена",
        "📞 Контакты указаны",
        "💼 Опыт работы описан",
        "🎓 Образование указано",
        "🛠️ Навыки перечислены",
        "🏆 Достижения с цифрами",
        "📄 Формат PDF",
        "✅ Нет ошибок"
    ]
    
    done = sum(1 for item in user["resume_checklist"] if item)
    total = len(checklist_items)
    percent = int(done / total * 100)
    
    text = f"📄 <b>Чек-лист резюме</b>\n\n"
    text += f"📊 <b>Прогресс:</b> {done}/{total} ({percent}%)\n\n"
    
    for i, item in enumerate(checklist_items):
        status = "✅" if user["resume_checklist"][i] else "⬜"
        text += f"{status} {item}\n"
    
    if percent == 100 and "resume_complete" not in user["achievements"]:
        user["achievements"].append("resume_complete")
        add_xp(message.from_user.id, 200)
        text += "\n\n🎉 <b>Поздравляю! Резюме готово! +200 XP</b>"
    
    await message.answer(text, reply_markup=get_resume_keyboard(), parse_mode="HTML")

@dp.callback_query(F.data == "resume_checklist")
async def cb_resume_checklist(callback: types.CallbackQuery):
    await btn_resume(callback.message)
    await callback.answer()

@dp.callback_query(F.data == "resume_mark")
async def cb_resume_mark(callback: types.CallbackQuery):
    user = get_user_data(callback.from_user.id)
    
    checklist_items = [
        "📸 Фотография",
        "📞 Контакты",
        "💼 Опыт работы",
        "🎓 Образование",
        "🛠️ Навыки",
        "🏆 Достижения",
        "📄 Формат PDF",
        "✅ Нет ошибок"
    ]
    
    kb = []
    for i, item in enumerate(checklist_items):
        if not user["resume_checklist"][i]:
            kb.append([InlineKeyboardButton(text=item, callback_data=f"resume_mark_{i}")])
    
    if not kb:
        await callback.answer("Все пункты отмечены! 🎉", show_alert=True)
        return
    
    await callback.message.edit_text(
        "✅ <b>Отметь выполненный пункт:</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("resume_mark_"))
async def cb_resume_mark_done(callback: types.CallbackQuery):
    user = get_user_data(callback.from_user.id)
    idx = int(callback.data.split("_")[2])
    
    user["resume_checklist"][idx] = True
    add_xp(callback.from_user.id, 25)
    
    await callback.answer(f"+25 XP! ✅")
    await btn_resume(callback.message)

@dp.message(F.text == "🛠️ Навыки")
async def btn_skills(message: types.Message):
    user = get_user_data(message.from_user.id)
    
    text = "🛠️ <b>Твои навыки</b>\n\n"
    
    if user["skills"]:
        for skill_name, level in user["skills"].items():
            level_name = skill_levels.get(level, "🌱 Новичок")
            text += f"{level_name} — {skill_name} (уровень {level}/5)\n"
    else:
        text += "Пока нет навыков. Добавь первый! 👇"
    
    text += f"\n⚡ +10 XP за новый навык\n⚡ +15 XP за прокачку"
    
    await message.answer(text, reply_markup=get_skills_main_keyboard(), parse_mode="HTML")

@dp.callback_query(F.data == "skills_list")
async def cb_skills_list(callback: types.CallbackQuery):
    await btn_skills(callback.message)
    await callback.answer()

@dp.callback_query(F.data == "skills_add_template")
async def cb_skills_add_template(callback: types.CallbackQuery):
    kb = []
    for skill in template_skills:
        kb.append([InlineKeyboardButton(text=skill, callback_data=f"skill_add_tpl_{skill}")])
    
    await callback.message.edit_text(
        "📚 <b>Выбери навык из списка:</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("skill_add_tpl_"))
async def cb_skills_add_tpl_confirm(callback: types.CallbackQuery):
    user = get_user_data(callback.from_user.id)
    skill_name = callback.data.replace("skill_add_tpl_", "")
    
    if skill_name not in user["skills"]:
        user["skills"][skill_name] = 1
        add_xp(callback.from_user.id, 10)
        await callback.answer(f"+10 XP! {skill_name} добавлен ✅")
    else:
        await callback.answer("Уже есть!", show_alert=True)
    
    await btn_skills(callback.message)

@dp.callback_query(F.data == "skills_add_custom")
async def cb_skills_add_custom(callback: types.CallbackQuery):
    await callback.message.answer(
        "✨ <b>Добавь свой навык</b>\n\n"
        "Напиши название навыка в следующем сообщении:\n"
        "Например: 'Figma', 'Копирайтинг', 'Продажи'\n\n"
        "Или нажми /start чтобы отменить"
    )
    user = get_user_data(callback.from_user.id)
    user["waiting_custom_skill"] = True
    await callback.answer()

@dp.callback_query(F.data == "skills_level_up")
async def cb_skills_level_up(callback: types.CallbackQuery):
    user = get_user_data(callback.from_user.id)
    
    if not user["skills"]:
        await callback.answer("Сначала добавь навыки!", show_alert=True)
        return
    
    kb = []
    for skill_name, level in user["skills"].items():
        if level < 5:
            kb.append([InlineKeyboardButton(text=f"⬆️ {skill_name} ({level}/5)", callback_data=f"skill_up_{skill_name}")])
    
    if not kb:
        await callback.answer("Все навыки на максимуме! 🏆", show_alert=True)
        return
    
    await callback.message.edit_text(
        "⬆️ <b>Выбери навык для прокачки:</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("skill_up_"))
async def cb_skills_level_up_confirm(callback: types.CallbackQuery):
    user = get_user_data(callback.from_user.id)
    skill_name = callback.data.replace("skill_up_", "")
    
    if skill_name in user["skills"] and user["skills"][skill_name] < 5:
        user["skills"][skill_name] += 1
        add_xp(callback.from_user.id, 15)
        new_level = user["skills"][skill_name]
        await callback.answer(f"+15 XP! {skill_name} → уровень {new_level} 🎉")
    else:
        await callback.answer("Нельзя прокачать!", show_alert=True)
    
    await btn_skills(callback.message)

@dp.message(F.text == "🎤 Собеседование")
async def btn_interview(message: types.Message):
    user = get_user_data(message.from_user.id)
    
    text = (
        "🎤 <b>Симулятор собеседования</b>\n\n"
        f"Пройдено вопросов: {user.get('interview_completed', 0)}\n\n"
        "Я задам вопрос, ты ответишь текстом.\n"
        "Я проанализирую ответ и дам обратную связь!\n\n"
        "⚡ +20 XP за каждый вопрос"
    )
    
    await message.answer(text, reply_markup=get_interview_keyboard(), parse_mode="HTML")

@dp.callback_query(F.data == "interview_tips_list")
async def cb_interview_tips_list(callback: types.CallbackQuery):
    text = "💡 <b>Советы для собеседования:</b>\n\n"
    for q_data in interview_questions:
        text += f"<b>❓ {q_data['question']}</b>\n"
        text += f"💡 {q_data['tips']}\n\n"
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "interview_start")
async def cb_interview_start(callback: types.CallbackQuery):
    user = get_user_data(callback.from_user.id)
    user["interview_mode"] = True
    user["interview_question_idx"] = 0
    
    q_data = interview_questions[user["interview_question_idx"]]
    
    await callback.message.edit_text(
        f"🎤 <b>Вопрос 1/{len(interview_questions)}</b>\n\n"
        f"<b>{q_data['question']}</b>\n\n"
        f"💡 Подсказка: {q_data['tips']}\n\n"
        f"Напиши свой ответ сообщением 👇",
        parse_mode="HTML"
    )
    await callback.answer()

@dp.message(F.text == "✉️ Сопроводительное")
async def btn_cover_letter(message: types.Message):
    text = (
        "✉️ <b>Генератор сопроводительного письма</b>\n\n"
        "Я помогу составить профессиональное письмо за 2 минуты!\n\n"
        "<b>Что нужно подготовить:</b>\n"
        "• Твоё имя\n"
        "• Позиция (название вакансии)\n"
        "• Компания\n"
        "• 3-5 навыков\n"
        "• Контакты (телефон/email/Telegram)\n"
        "• Опыт работы (необязательно)\n\n"
        "Выбери действие 👇"
    )
    await message.answer(text, reply_markup=get_cover_letter_keyboard(), parse_mode="HTML")

@dp.callback_query(F.data == "cover_create")
async def cb_cover_create(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "✏️ <b>Создание сопроводительного письма</b>\n\n"
        "Сейчас я задам тебе несколько вопросов.\n"
        "Отвечай по очереди 👇\n\n"
        "<b>Вопрос 1/6:</b>\n"
        "Как тебя зовут?",
        parse_mode="HTML"
    )
    user = get_user_data(callback.from_user.id)
    user["cover_letter_data"] = {"step": 1}
    await callback.answer()

@dp.callback_query(F.data == "cover_templates")
async def cb_cover_templates(callback: types.CallbackQuery):
    text = (
        "📋 <b>Шаблоны писем:</b>\n\n"
        "<b>1. Для начинающего специалиста:</b>\n"
        "Акцент на мотивацию и готовность учиться\n\n"
        "<b>2. Для опытного специалиста:</b>\n"
        "Акцент на достижения и опыт\n\n"
        "<b>3. Для смены профессии:</b>\n"
        "Акцент на transferable skills\n\n"
        "💡 Используй мастер создания выше!"
    )
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "cover_help")
async def cb_cover_help(callback: types.CallbackQuery):
    text = (
        "💡 <b>Как заполнить:</b>\n\n"
        "<b>Имя:</b> Как к тебе обращаться\n\n"
        "<b>Позиция:</b> Точное название вакансии\n"
        "Например: 'SMM-менеджер', 'HR-специалист'\n\n"
        "<b>Компания:</b> Название компании\n"
        "Например: 'Яндекс', 'Сбер', 'Digital Agency'\n\n"
        "<b>Навыки:</b> 3-5 главных навыков\n"
        "Через запятую: 'коммуникация, аналитика, Excel'\n\n"
        "<b>Контакты:</b> Как с тобой связаться\n"
        "Телефон, email или Telegram\n\n"
        "<b>Опыт:</b> Кратко о опыте (необязательно)\n"
        "Например: '2 года в маркетинге'"
    )
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()

@dp.message(F.text == "📬 Полезное")
async def btn_useful(message: types.Message):
    tip = random.choice(weekly_tips)
    await message.answer(tip, parse_mode="HTML")

@dp.message(F.text == "💬 Обратная связь")
async def btn_feedback(message: types.Message):
    text = (
        "💬 <b>Твоё мнение важно!</b>\n\n"
        "Я хочу сделать бота ещё лучше, поэтому буду рад любой обратной связи.\n\n"
        "Напиши:\n"
        "• Что тебе понравилось\n"
        "• Что можно улучшить\n"
        "• Какие функции добавить\n\n"
        "Или напиши мне напрямую 👇"
    )
    await message.answer(text, reply_markup=get_feedback_keyboard(), parse_mode="HTML")

@dp.callback_query(F.data == "feedback_text")
async def cb_feedback_text(callback: types.CallbackQuery):
    user = get_user_data(callback.from_user.id)
    user["waiting_feedback"] = True
    
    await callback.message.answer(
        "📝 <b>Напиши свой отзыв</b>\n\n"
        "Я (Ворон Кар) обязательно всё прочитаю! 🖤\n\n"
        "Или нажми /start чтобы вернуться в меню",
        parse_mode="HTML"
    )
    await callback.answer()

@dp.message()
async def msg_other(message: types.Message):
    user = get_user_data(message.from_user.id)
    
    # Обработка добавления кастомного навыка
    if user.get("waiting_custom_skill", False):
        user["waiting_custom_skill"] = False
        skill_name = message.text.strip()
        
        if len(skill_name) < 3:
            await message.answer("⚠️ Слишком короткое название. Попробуй ещё раз!")
            return
        
        if skill_name not in user["skills"]:
            user["skills"][skill_name] = 1
            user["custom_skills"].append(skill_name)
            add_xp(message.from_user.id, 10)
            await message.answer(
                f"✅ <b>Навык добавлен!</b>\n\n"
                f"🛠️ {skill_name} — уровень 1\n\n"
                f"⚡ +10 XP",
                reply_markup=get_main_keyboard(),
                parse_mode="HTML"
            )
        else:
            await message.answer("⚠️ Такой навык уже есть!")
        return
    
    # Обработка создания сопроводительного письма (пошагово)
    if user.get("cover_letter_data", {}).get("step", 0) > 0:
        step = user["cover_letter_data"]["step"]
        data = user["cover_letter_data"]
        
        if step == 1:  # Имя
            data["name"] = message.text.strip()
            data["step"] = 2
            await message.answer(
                f"✅ <b>Имя:</b> {data['name']}\n\n"
                f"<b>Вопрос 2/6:</b>\n"
                "На какую позицию откликаешься?\n"
                "<i>Напиши точное название вакансии</i>",
                parse_mode="HTML"
            )
            return
        
        elif step == 2:  # Позиция
            data["position"] = message.text.strip()
            data["step"] = 3
            await message.answer(
                f"✅ <b>Позиция:</b> {data['position']}\n\n"
                f"<b>Вопрос 3/6:</b>\n"
                "В какую компанию?\n"
                "<i>Напиши название компании</i>",
                parse_mode="HTML"
            )
            return
        
        elif step == 3:  # Компания
            data["company"] = message.text.strip()
            data["step"] = 4
            await message.answer(
                f"✅ <b>Компания:</b> {data['company']}\n\n"
                f"<b>Вопрос 4/6:</b>\n"
                "Твои навыки (3-5 штук)\n"
                "<i>Напиши через запятую:</i>\n"
                "<i>например: коммуникация, аналитика, Excel</i>",
                parse_mode="HTML"
            )
            return
        
        elif step == 4:  # Навыки
            skills = [s.strip() for s in message.text.split(",")]
            data["skills"] = skills
            data["step"] = 5
            await message.answer(
                f"✅ <b>Навыки:</b> {len(skills)} шт.\n\n"
                f"<b>Вопрос 5/6:</b>\n"
                "Твои контакты\n"
                "<i>Телефон, email или Telegram</i>",
                parse_mode="HTML"
            )
            return
        
        elif step == 5:  # Контакты
            data["contact"] = message.text.strip()
            data["step"] = 6
            await message.answer(
                f"✅ <b>Контакты:</b> {data['contact']}\n\n"
                f"<b>Вопрос 6/6 (необязательно):</b>\n"
                "Кратко о опыте работы\n"
                "<i>Или напиши 'нет', если не хочешь указывать</i>",
                parse_mode="HTML"
            )
            return
        
        elif step == 6:  # Опыт (последний)
            experience = message.text.strip()
            if experience.lower() in ["нет", "-", ""]:
                experience = ""
            
            letter = generate_cover_letter(
                name=data["name"],
                position=data["position"],
                company=data["company"],
                skills=data["skills"],
                contact=data["contact"],
                experience=experience
            )
            
            user["cover_letter_data"] = {}
            add_xp(message.from_user.id, 30)
            
            await message.answer(
                f"📬 <b>Твоё сопроводительное письмо:</b>\n\n"
                f"{letter}\n\n"
                f"<i>📋 Скопируй и отправь работодателю!</i>\n\n"
                f"⚡ +30 XP",
                parse_mode="HTML"
            )
            return
    
    # Обработка режима собеседования
    if user.get("interview_mode", False):
        q_idx = user.get("interview_question_idx", 0)
        q_data = interview_questions[q_idx]
        
        user_answer = message.text.lower()
        
        found_keywords = [kw for kw in q_data["keywords"] if kw in user_answer]
        keyword_count = len(found_keywords)
        
        if keyword_count >= 2:
            feedback = "✅ <b>Отличный ответ!</b>\n\n"
            feedback += f"Ты упомянул: {', '.join(found_keywords)}\n"
            feedback += "Это хорошие признаки!\n"
            xp_gain = 25
        elif keyword_count == 1:
            feedback = "👍 <b>Неплохо!</b>\n\n"
            feedback += f"Ты упомянул: {found_keywords[0]}\n"
            feedback += "Попробуй добавить больше конкретики.\n"
            xp_gain = 15
        else:
            feedback = "💡 <b>Можно лучше!</b>\n\n"
            feedback += "Попробуй добавить:\n"
            feedback += f"• {q_data['tips']}\n"
            feedback += "Будь конкретнее, приводи примеры.\n"
            xp_gain = 10
        
        user["interview_completed"] = user.get("interview_completed", 0) + 1
        add_xp(message.from_user.id, xp_gain)
        
        if q_idx + 1 < len(interview_questions):
            user["interview_question_idx"] += 1
            next_q = interview_questions[q_idx + 1]
            
            await message.answer(
                f"{feedback}\n"
                f"⚡ +{xp_gain} XP\n\n"
                f"🎤 <b>Вопрос {q_idx + 2}/{len(interview_questions)}</b>\n\n"
                f"<b>{next_q['question']}</b>\n\n"
                f"💡 Подсказка: {next_q['tips']}\n\n"
                f"Напиши ответ 👇",
                parse_mode="HTML"
            )
        else:
            user["interview_mode"] = False
            if user["interview_completed"] >= 3 and "interview_pass" not in user["achievements"]:
                user["achievements"].append("interview_pass")
                add_xp(message.from_user.id, 50)
                bonus = "\n\n🎉 <b>+50 XP за прохождение всех вопросов!</b>"
            else:
                bonus = ""
            
            await message.answer(
                f"{feedback}\n"
                f"⚡ +{xp_gain} XP\n\n"
                f"🎉 <b>Собеседование завершено!</b>\n\n"
                f"Всего пройдено: {user['interview_completed']} вопросов\n"
                f"{bonus}",
                reply_markup=get_main_keyboard(),
                parse_mode="HTML"
            )
        return
    
    # Обработка отзыва
    if user.get("waiting_feedback", False):
        add_xp(message.from_user.id, 20)
        user["waiting_feedback"] = False
        await send_to_admin(f"💬 Отзыв от {message.from_user.first_name}:\n\n{message.text}")
        await message.answer(
            "Спасибо! Твой отзыв сохранён 🖤\n\n"
            "⚡ +20 XP",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Обычное сообщение
    await message.answer(
        "Используй кнопки внизу или /start",
        reply_markup=get_main_keyboard()
    )

@dp.callback_query(F.data == "feedback_text")
async def cb_feedback_text(callback: types.CallbackQuery):
    user = get_user_data(callback.from_user.id)
    user["waiting_feedback"] = True
    
    await callback.message.answer(
        "📝 <b>Напиши свой отзыв</b>\n\n"
        "Я (Ворон Кар) обязательно всё прочитаю! 🖤\n\n"
        "Или нажми /start чтобы вернуться в меню",
        parse_mode="HTML"
    )
    await callback.answer()

# === ЗАПУСК ===
async def main():
    print("\n" + "="*50)
    print("🖤 Ворон Кар запущен...")
    print(f"📸 Используем file_id для мгновенной отправки фото")
    print("="*50 + "\n")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
