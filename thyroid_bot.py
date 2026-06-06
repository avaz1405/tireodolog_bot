#!/usr/bin/env python3
"""
Qalqonsimon bez va bosh-bo'yin o'sma kasalliklari bo'yicha maslahat boti
Dr. Avaz Kodirov | +998915281595 | @AvazKodirov
"""

import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)

# ─── Sozlamalar ───────────────────────────────────────────────────────────────
import os
BOT_TOKEN = os.environ.get("BOT_TOKEN")

DOCTOR_PHONE    = "+998915281595"
DOCTOR_TELEGRAM = "@AvazKodirov"

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── Holat konstantalari ──────────────────────────────────────────────────────
LANG, MENU, SYM_CHOICE, THYROID_SYM, TUMOR_SYM, RESULT = range(6)

CONTACT_UZ = (
    f"📞 Telefon: <code>{DOCTOR_PHONE}</code>\n"
    f"💬 Telegram: {DOCTOR_TELEGRAM}\n\n"
    "📱 Agar telefonga javob bera olmasa, Telegramga yozing — tez orada javob beriladi!"
)
CONTACT_RU = (
    f"📞 Телефон: <code>{DOCTOR_PHONE}</code>\n"
    f"💬 Telegram: {DOCTOR_TELEGRAM}\n\n"
    "📱 Если не дозвонились — напишите в Telegram, ответ придёт в ближайшее время!"
)

# ─── Matnlar ──────────────────────────────────────────────────────────────────
TEXTS = {
    "uz": {
        "welcome": (
            "👋 Assalomu alaykum!\n\n"
            "Men qalqonsimon bez va bosh-bo'yin o'sma kasalliklari bo'yicha "
            "maslahat beruvchi botman.\n"
            "Sizga yordam berishdan mamnunman. Boshlaylikmi?"
        ),
        "menu_prompt": "Quyidagilardan birini tanlang:",
        "menu_buttons": ["📋 Belgilarni tekshirish", "📞 Shifokor bilan bog'lanish", "ℹ️ Bot haqida"],

        # ── Belgi tanlash ekrani ──
        "sym_choice_q": "Qaysi soha bo'yicha belgilarni tekshirmoqchisiz?",
        "sym_choice_buttons": [
            "🦋 Qalqonsimon bez kasalliklari",
            "🔬 Bosh-bo'yin o'sma kasalliklari",
            "🔙 Orqaga"
        ],

        # ── Qalqonsimon bez belgilari ──
        "thyroid_q": (
            "Qalqonsimon bez kasalliklari belgilari:\n"
            "Sizda qaysilar bor? Raqam yozing yoki o'zingiz tasvirlab bering.\n\n"
            "<b>Tireotoksikoz belgilari:</b>\n"
            "1️⃣ Yurak tez urishi, qo'l titrashi\n"
            "2️⃣ Vazn kamayishi, ishtaha oshishi\n"
            "3️⃣ Issiqqa chidamsizlik, ko'p terlash\n"
            "4️⃣ Tez asabiylashish, bezovtalik\n"
            "5️⃣ Ko'zlar chaqchayishi\n\n"
            "<b>Gipotireoz belgilari:</b>\n"
            "6️⃣ Charchoq, holsizlik, uyquchanlik\n"
            "7️⃣ Vazn ortishi, ishtaha kamligi\n"
            "8️⃣ Sovuqqa chidamsizlik\n"
            "9️⃣ Soch to'kilishi, teri quruqligi\n"
            "🔟 Tushkunlik, xotira zaiflashi\n\n"
            "<b>Tugunli buqoq belgilari:</b>\n"
            "1️⃣1️⃣ Bo'yinda ko'rinib turuvchi shish yoki tugun\n"
            "1️⃣2️⃣ Tomog'da tiqilish hissi, yutinishda qiyinchilik\n"
            "1️⃣3️⃣ Ovoz o'zgarishi (xirillash)\n\n"
            "0️⃣ Hech qanday belgi yo'q"
        ),
        "thyroid_has": (
            "⚠️ Siz belgilagan alomatlar qalqonsimon bez kasalligi "
            "(tireotoksikoz, gipotireoz yoki tugunli buqoq) bilan bog'liq bo'lishi mumkin.\n\n"
            "✅ Mutaxassis shifokorga murojaat qilish tavsiya etiladi.\n\n"
            "👨‍⚕️ <b>Dr. Avaz Kodirov</b> — Endokrinolog\n"
            "Qalqonsimon bez kasalliklari bo'yicha mutaxassis\n\n"
            "{contact}\n\n"
            "Murojaat qilishdan tortinmang — erta aniqlash davolanishni osonlashtiradi! 🙏"
        ),
        "thyroid_no": (
            "✅ Yaxshi! Hozircha qalqonsimon bez kasalligi belgilari ko'rinmayapti.\n\n"
            "Profilaktika maqsadida yiliga bir marta endokrinologga ko'rinish tavsiya etiladi.\n\n"
            "👨‍⚕️ <b>Dr. Avaz Kodirov</b> — Endokrinolog\n\n"
            "{contact}"
        ),

        # ── Bosh-bo'yin o'sma belgilari ──
        "tumor_q": (
            "Bosh-bo'yin o'sma kasalliklari belgilari:\n"
            "Sizda qaysilar bor? Raqam yozing yoki o'zingiz tasvirlab bering.\n\n"
            "1️⃣ Boshning sochli qismida hosila yoki o'sma\n"
            "2️⃣ Yuzda (yonoq, peshona, burun atrofi) hosila yoki shish\n"
            "3️⃣ Quloq oldi sohasida tugun yoki shish\n"
            "4️⃣ Jag' osti sohasida hosila yoki limfa tugunlari kattalashishi\n"
            "5️⃣ Bo'yin sohasida hosila, shish yoki og'riq\n"
            "6️⃣ Yutinishda qiyinchilik yoki tomog'da tiqilish\n"
            "7️⃣ Ovoz o'zgarishi, xirillash\n"
            "8️⃣ Og'izda, tilning osti, til yoki lunj soxasida yarа yoki hosila\n\n"
            "0️⃣ Hech qanday belgi yo'q"
        ),
        "tumor_has": (
            "⚠️ Siz belgilagan alomatlar bosh-bo'yin sohasidagi o'sma kasalliklari bilan "
            "bog'liq bo'lishi mumkin.\n\n"
            "❗ Diqqat: Bosh, yuz, quloq oldi, jag' osti va bo'yin sohasidagi har qanday hosila "
            "yoki o'sma <b>xavfli yoki xavfsiz</b> bo'lishi mumkin.\n\n"
            "✅ Aniq tashxis uchun mutaxassis shifokorga imkon qadar tezroq murojaat qiling!\n\n"
            "👨‍⚕️ <b>Dr. Avaz Kodirov</b> — Bosh-bo'yin o'smalari mutaxassisi\n\n"
            "{contact}\n\n"
            "Erta murojaat — muvaffaqiyatli davolanish garovidir! 🙏"
        ),
        "tumor_no": (
            "✅ Yaxshi! Hozircha bosh-bo'yin o'sma kasalligi belgilari ko'rinmayapti.\n\n"
            "Shu bilan birga, bo'yin, yuz yoki bosh sohasida biror o'zgarish sezсangиz, "
            "kechiktirmay mutaxassisga murojaat qiling.\n\n"
            "👨‍⚕️ <b>Dr. Avaz Kodirov</b>\n\n"
            "{contact}"
        ),

        # ── Umumiy ──
        "contact": (
            "👨‍⚕️ <b>Dr. Avaz Kodirov</b>\n"
            "Endokrinolog | Bosh-bo'yin o'smalari mutaxassisi\n\n"
            f"📞 Telefon: <code>{DOCTOR_PHONE}</code>\n"
            f"💬 Telegram: {DOCTOR_TELEGRAM}\n\n"
            "📱 Agar telefonga javob bera olmasa, Telegramga yozing — tez orada javob beriladi!\n\n"
            "Qabulga yozilish yoki savol berish uchun murojaat qiling! 🙏"
        ),
        "about": (
            "ℹ️ <b>Bu bot haqida</b>\n\n"
            "Bu bot qalqonsimon bez va bosh-bo'yin o'sma kasalliklari bo'yicha "
            "dastlabki ma'lumot berish uchun yaratilgan.\n\n"
            "⚠️ Diqqat: Bot tibbiy tashxis qo'ymaydi. "
            "Aniq tashxis va davolash uchun mutaxassis shifokorga murojaat qiling.\n\n"
            "👨‍⚕️ <b>Dr. Avaz Kodirov</b>\n"
            f"📞 {DOCTOR_PHONE} | 💬 {DOCTOR_TELEGRAM}"
        ),
        "back": "🔙 Orqaga",
        "again": "🔄 Yana tekshirish",
        "unknown": "Iltimos, quyidagi tugmalardan birini tanlang 👇",
    },

    "ru": {
        "welcome": (
            "👋 Добро пожаловать!\n\n"
            "Я бот-помощник по заболеваниям щитовидной железы и опухолям головы и шеи.\n"
            "Готов помочь вам разобраться. Начнём?"
        ),
        "menu_prompt": "Выберите одно из следующих:",
        "menu_buttons": ["📋 Проверить симптомы", "📞 Связаться с врачом", "ℹ️ О боте"],

        "sym_choice_q": "По какому направлению хотите проверить симптомы?",
        "sym_choice_buttons": [
            "🦋 Заболевания щитовидной железы",
            "🔬 Опухоли головы и шеи",
            "🔙 Назад"
        ],

        # ── Щитовидная железа ──
        "thyroid_q": (
            "Симптомы заболеваний щитовидной железы:\n"
            "Какие из них вас беспокоят? Напишите номер или опишите своими словами.\n\n"
            "<b>Симптомы тиреотоксикоза:</b>\n"
            "1️⃣ Учащённое сердцебиение, дрожь в руках\n"
            "2️⃣ Потеря веса при хорошем аппетите\n"
            "3️⃣ Непереносимость жары, повышенное потоотделение\n"
            "4️⃣ Раздражительность, тревожность\n"
            "5️⃣ Выпученность глаз\n\n"
            "<b>Симптомы гипотиреоза:</b>\n"
            "6️⃣ Усталость, слабость, сонливость\n"
            "7️⃣ Набор веса, снижение аппетита\n"
            "8️⃣ Непереносимость холода\n"
            "9️⃣ Выпадение волос, сухость кожи\n"
            "🔟 Депрессия, ухудшение памяти\n\n"
            "<b>Симптомы узлового зоба:</b>\n"
            "1️⃣1️⃣ Видимый узел или припухлость на шее\n"
            "1️⃣2️⃣ Ощущение кома в горле, затруднение при глотании\n"
            "1️⃣3️⃣ Изменение голоса (охриплость)\n\n"
            "0️⃣ Никаких симптомов нет"
        ),
        "thyroid_has": (
            "⚠️ Отмеченные вами симптомы могут быть связаны с заболеванием щитовидной железы "
            "(тиреотоксикоз, гипотиреоз или узловой зоб).\n\n"
            "✅ Рекомендуется обратиться к специалисту.\n\n"
            "👨‍⚕️ <b>Др. Аваз Кодиров</b> — Эндокринолог\n"
            "Специалист по заболеваниям щитовидной железы\n\n"
            "{contact}\n\n"
            "Не стесняйтесь обращаться — раннее выявление упрощает лечение! 🙏"
        ),
        "thyroid_no": (
            "✅ Хорошо! Серьёзных симптомов заболевания щитовидной железы пока не наблюдается.\n\n"
            "Для профилактики рекомендуется посещать эндокринолога раз в год.\n\n"
            "👨‍⚕️ <b>Др. Аваз Кодиров</b> — Эндокринолог\n\n"
            "{contact}"
        ),

        # ── Опухоли головы и шеи ──
        "tumor_q": (
            "Симптомы опухолей головы и шеи:\n"
            "Какие из них вас беспокоят? Напишите номер или опишите своими словами.\n\n"
            "1️⃣ Образование или опухоль на волосистой части головы\n"
            "2️⃣ Образование или припухлость на лице (щека, лоб, область носа)\n"
            "3️⃣ Узел или припухлость в области уха (околоушная железа)\n"
            "4️⃣ Образование под нижней челюстью или увеличение лимфоузлов\n"
            "5️⃣ Узел, припухлость или боль в области шеи\n"
            "6️⃣ Затруднение при глотании или ощущение кома в горле\n"
            "7️⃣ Изменение голоса, охриплость\n"
            "8️⃣ Язва или образование во рту, под языком или на щеке\n\n"
            "0️⃣ Никаких симптомов нет"
        ),
        "tumor_has": (
            "⚠️ Отмеченные вами симптомы могут быть связаны с опухолями головы и шеи.\n\n"
            "❗ Внимание: Любое образование в области головы, лица, около уха, "
            "под нижней челюстью или на шее <b>может быть доброкачественным или злокачественным</b>.\n\n"
            "✅ Для точного диагноза как можно скорее обратитесь к специалисту!\n\n"
            "👨‍⚕️ <b>Др. Аваз Кодиров</b> — Специалист по опухолям головы и шеи\n\n"
            "{contact}\n\n"
            "Раннее обращение — залог успешного лечения! 🙏"
        ),
        "tumor_no": (
            "✅ Хорошо! Серьёзных симптомов опухолей головы и шеи пока не наблюдается.\n\n"
            "Если заметите какие-либо изменения в области шеи, лица или головы — "
            "не откладывайте визит к специалисту.\n\n"
            "👨‍⚕️ <b>Др. Аваз Кодиров</b>\n\n"
            "{contact}"
        ),

        "contact": (
            "👨‍⚕️ <b>Др. Аваз Кодиров</b>\n"
            "Эндокринолог | Специалист по опухолям головы и шеи\n\n"
            f"📞 Телефон: <code>{DOCTOR_PHONE}</code>\n"
            f"💬 Telegram: {DOCTOR_TELEGRAM}\n\n"
            "📱 Если не дозвонились — напишите в Telegram, ответ придёт в ближайшее время!\n\n"
            "Обращайтесь для записи на приём или задайте вопрос! 🙏"
        ),
        "about": (
            "ℹ️ <b>О боте</b>\n\n"
            "Этот бот создан для первичного информирования о заболеваниях щитовидной железы "
            "и опухолях головы и шеи.\n\n"
            "⚠️ Внимание: Бот не ставит медицинский диагноз. "
            "Для точного диагноза и лечения обратитесь к специалисту.\n\n"
            "👨‍⚕️ <b>Др. Аваз Кодиров</b>\n"
            f"📞 {DOCTOR_PHONE} | 💬 {DOCTOR_TELEGRAM}"
        ),
        "back": "🔙 Назад",
        "again": "🔄 Проверить снова",
        "unknown": "Пожалуйста, выберите один из вариантов ниже 👇",
    }
}

# ─── Kalit so'zlar ────────────────────────────────────────────────────────────
THYROID_KW_UZ = [
    "1","2","3","4","5","6","7","8","9","10","11","12","13",
    "yurak","tez ur","titras","vazn","ishtaha","issiq","terl","asab","bezovta",
    "chaqchay","charchoq","holsiz","uyqu","sovuq","soch","teri","tushkunlik",
    "xotira","bo'yin","tugun","shish","tomoq","tiqil","yutinish","ovoz","xirilla"
]
THYROID_KW_RU = [
    "1","2","3","4","5","6","7","8","9","10","11","12","13",
    "сердц","дрожь","вес","аппетит","жар","пот","раздраж","тревог",
    "выпуч","устал","слаб","сон","холод","волос","кож","депрес",
    "памят","шея","узел","припухл","горл","глотан","голос","охрип"
]
TUMOR_KW_UZ = [
    "1","2","3","4","5","6","7","8",
    "soch","g'o'la","o'sma","hosila","yuz","yonoq","peshona","burun",
    "quloq","jag'","limfa","bo'yin","tugun","shish","og'riq",
    "yutinish","tomoq","ovoz","xirilla","og'iz","til","yara"
]
TUMOR_KW_RU = [
    "1","2","3","4","5","6","7","8",
    "волос","образован","опухол","лиц","щек","лоб","нос",
    "ух","челюст","лимф","шея","узел","припухл","бол",
    "глотан","горл","голос","охрип","рот","язык","язва"
]

# ─── Yordamchi funksiyalar ────────────────────────────────────────────────────
def get_lang(context):
    return context.user_data.get("lang", "uz")

def contact_str(lang):
    return CONTACT_UZ if lang == "uz" else CONTACT_RU

def main_menu(lang):
    t = TEXTS[lang]
    kb = [[KeyboardButton(b)] for b in t["menu_buttons"]]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

def sym_choice_menu(lang):
    t = TEXTS[lang]
    kb = [[KeyboardButton(b)] for b in t["sym_choice_buttons"]]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

def back_menu(lang):
    t = TEXTS[lang]
    return ReplyKeyboardMarkup([[KeyboardButton(t["back"])]], resize_keyboard=True)

def result_menu(lang):
    t = TEXTS[lang]
    return ReplyKeyboardMarkup(
        [[KeyboardButton(t["again"])], [KeyboardButton(t["back"])]],
        resize_keyboard=True
    )

# ─── Handlerlar ───────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton("🇺🇿 O'zbekcha"), KeyboardButton("🇷🇺 Русский")]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await update.message.reply_text("Tilni tanlang / Выберите язык:", reply_markup=kb)
    return LANG

async def choose_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    lang = "ru" if "Русский" in text or "ру" in text.lower() else "uz"
    context.user_data["lang"] = lang
    t = TEXTS[lang]
    await update.message.reply_text(t["welcome"], reply_markup=main_menu(lang))
    return MENU

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    t = TEXTS[lang]
    text = update.message.text

    if t["menu_buttons"][0] in text:       # Belgilarni tekshirish
        await update.message.reply_text(t["sym_choice_q"], reply_markup=sym_choice_menu(lang))
        return SYM_CHOICE
    elif t["menu_buttons"][1] in text:     # Shifokor bilan bog'lanish
        await update.message.reply_text(t["contact"], parse_mode="HTML", reply_markup=main_menu(lang))
        return MENU
    elif t["menu_buttons"][2] in text:     # Bot haqida
        await update.message.reply_text(t["about"], parse_mode="HTML", reply_markup=main_menu(lang))
        return MENU
    else:
        await update.message.reply_text(t["unknown"], reply_markup=main_menu(lang))
        return MENU

async def sym_choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    t = TEXTS[lang]
    text = update.message.text

    if t["sym_choice_buttons"][2] in text or t["back"] in text:  # Orqaga
        await update.message.reply_text(t["menu_prompt"], reply_markup=main_menu(lang))
        return MENU
    elif t["sym_choice_buttons"][0] in text:   # Qalqonsimon bez
        await update.message.reply_text(t["thyroid_q"], parse_mode="HTML", reply_markup=back_menu(lang))
        return THYROID_SYM
    elif t["sym_choice_buttons"][1] in text:   # Bosh-bo'yin o'sma
        await update.message.reply_text(t["tumor_q"], parse_mode="HTML", reply_markup=back_menu(lang))
        return TUMOR_SYM
    else:
        await update.message.reply_text(t["unknown"], reply_markup=sym_choice_menu(lang))
        return SYM_CHOICE

async def thyroid_sym_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    t = TEXTS[lang]
    text = update.message.text.lower()

    if t["back"] in update.message.text:
        await update.message.reply_text(t["sym_choice_q"], reply_markup=sym_choice_menu(lang))
        return SYM_CHOICE

    no_triggers = ["0", "hech", "нет", "никак"]
    kw = THYROID_KW_RU if lang == "ru" else THYROID_KW_UZ

    if any(kw in text for kw in no_triggers) and not any(k in text for k in kw if k not in ["0"]):
        msg = t["thyroid_no"].format(contact=contact_str(lang))
    else:
        msg = t["thyroid_has"].format(contact=contact_str(lang))

    await update.message.reply_text(msg, parse_mode="HTML", reply_markup=result_menu(lang))
    context.user_data["last_section"] = "thyroid"
    return RESULT

async def tumor_sym_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    t = TEXTS[lang]
    text = update.message.text.lower()

    if t["back"] in update.message.text:
        await update.message.reply_text(t["sym_choice_q"], reply_markup=sym_choice_menu(lang))
        return SYM_CHOICE

    no_triggers = ["0", "hech", "нет", "никак"]
    kw = TUMOR_KW_RU if lang == "ru" else TUMOR_KW_UZ

    if any(kw in text for kw in no_triggers) and not any(k in text for k in kw if k not in ["0"]):
        msg = t["tumor_no"].format(contact=contact_str(lang))
    else:
        msg = t["tumor_has"].format(contact=contact_str(lang))

    await update.message.reply_text(msg, parse_mode="HTML", reply_markup=result_menu(lang))
    context.user_data["last_section"] = "tumor"
    return RESULT

async def result_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    t = TEXTS[lang]
    text = update.message.text

    if t["again"] in text:
        # Oxirgi bo'limga qaytarish
        section = context.user_data.get("last_section", "thyroid")
        if section == "tumor":
            await update.message.reply_text(t["tumor_q"], parse_mode="HTML", reply_markup=back_menu(lang))
            return TUMOR_SYM
        else:
            await update.message.reply_text(t["thyroid_q"], parse_mode="HTML", reply_markup=back_menu(lang))
            return THYROID_SYM
    elif t["back"] in text:
        await update.message.reply_text(t["menu_prompt"], reply_markup=main_menu(lang))
        return MENU
    else:
        await update.message.reply_text(t["unknown"], reply_markup=result_menu(lang))
        return RESULT

async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    await update.message.reply_text(TEXTS[lang]["unknown"], reply_markup=main_menu(lang))
    return MENU

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANG:        [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_lang)],
            MENU:        [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler)],
            SYM_CHOICE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, sym_choice_handler)],
            THYROID_SYM: [MessageHandler(filters.TEXT & ~filters.COMMAND, thyroid_sym_handler)],
            TUMOR_SYM:   [MessageHandler(filters.TEXT & ~filters.COMMAND, tumor_sym_handler)],
            RESULT:      [MessageHandler(filters.TEXT & ~filters.COMMAND, result_handler)],
        },
        fallbacks=[
            CommandHandler("start", start),
            MessageHandler(filters.TEXT & ~filters.COMMAND, fallback),
        ],
    )

    app.add_handler(conv)
    logger.info("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
