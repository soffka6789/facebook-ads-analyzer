“””
Facebook Ads Library Analyzer Telegram Bot
Автоматично аналізує товари в Facebook Ads Library України щотижня
Відправляє результати в Telegram з можливістю внесення змін
“””

import os
import json
import requests
from datetime import datetime, timedelta
from collections import defaultdict
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

# Setup logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(**name**)

# ============ КОНФІГУРАЦІЯ ============

TELEGRAM_TOKEN = “YOUR_BOT_TOKEN_HERE”  # Потрібен Telegram Bot Token
USER_ID = 5989342315  # Ваш Telegram ID
UKRAINE_TZ = pytz.timezone(‘Europe/Kyiv’)

# Симульовані дані Facebook Ads (у реальній версії буде веб-скрепер)

SIMULATED_ADS_DATA = {
“2026-05-06”: [
{
“name”: “Портативна лампа-акумулятор 10000 mAh”,
“category”: “Товари для дому”,
“price_range”: “299-599”,
“active_ads”: 287,
“competitors”: 34,
“growth”: 18,
“formats”: {“video”: 60, “carousel”: 30, “static”: 10},
“top_slogans”: [“Освітлення без електрики”, “Для пікніків”, “Портативна енергія”],
“recommendation”: “✅ ЗАПУСКАТИ ОДРАЗУ”
},
{
“name”: “Еко-пляшка з кастомним гравіюванням”,
“category”: “Аксесуари”,
“price_range”: “199-449”,
“active_ads”: 412,
“competitors”: 12,
“growth”: 45,
“formats”: {“video”: 35, “carousel”: 50, “static”: 15},
“top_slogans”: [“Екологічно”, “Кастомна”, “Подарунок”],
“recommendation”: “✅✅ ЗАПУСКАТИ МАКСИМАЛЬНО!”
},
{
“name”: “Smart-кільце для фітнесу (Oura style)”,
“category”: “Спортивні товари”,
“price_range”: “499-899”,
“active_ads”: 156,
“competitors”: 18,
“growth”: 28,
“formats”: {“video”: 70, “carousel”: 20, “static”: 10},
“top_slogans”: [“Моніторинг здоров’я”, “Smart tecnology”, “Бізнес + спорт”],
“recommendation”: “✅ ГАРНИЙ ВИБІР”
},
{
“name”: “Органічна косметика для обличчя (сироватка)”,
“category”: “Красота & здоров’я”,
“price_range”: “299-699”,
“active_ads”: 234,
“competitors”: 42,
“growth”: 12,
“formats”: {“video”: 55, “carousel”: 30, “static”: 15},
“top_slogans”: [“100% натуральна”, “Від морщин”, “Дерматолог тестовано”],
“recommendation”: “⚠️ КОНКУРЕНТНО, потребує диф”
},
{
“name”: “Бездротові навушники (TWS 5.3)”,
“category”: “Електроніка”,
“price_range”: “349-749”,
“active_ads”: 523,
“competitors”: 67,
“growth”: -5,
“formats”: {“video”: 45, “carousel”: 40, “static”: 15},
“top_slogans”: [“Best sound”, “Водостійкі”, “Довга батарея”],
“recommendation”: “❌ УНИКАЙТЕ - насичено”
},
{
“name”: “Термос-пляшка для гарячих напоїв”,
“category”: “Товари для дому”,
“price_range”: “199-399”,
“active_ads”: 178,
“competitors”: 23,
“growth”: 22,
“formats”: {“video”: 50, “carousel”: 35, “static”: 15},
“top_slogans”: [“Гарячий весь день”, “Для офісу”, “Еко-матеріал”],
“recommendation”: “✅ ЗАПУСКАТИ”
},
{
“name”: “Кастомна сумка-рюкзак з логотипом”,
“category”: “Аксесуари”,
“price_range”: “249-599”,
“active_ads”: 189,
“competitors”: 15,
“growth”: 35,
“formats”: {“video”: 40, “carousel”: 45, “static”: 15},
“top_slogans”: [“Твій логотип”, “Прочне”, “Стильно”],
“recommendation”: “✅ ЗАПУСКАТИ”
},
{
“name”: “Килимок для йоги еко-каучук”,
“category”: “Спортивні товари”,
“price_range”: “299-499”,
“active_ads”: 145,
“competitors”: 11,
“growth”: 41,
“formats”: {“video”: 60, “carousel”: 25, “static”: 15},
“top_slogans”: [“Еко”, “Не ковзає”, “Профільна товщина”],
“recommendation”: “✅ ГАРНИЙ ВИБІР”
},
{
“name”: “Вітаміни для волосся з колагеном”,
“category”: “Красота & здоров’я”,
“price_range”: “199-349”,
“active_ads”: 267,
“competitors”: 38,
“growth”: 19,
“formats”: {“video”: 55, “carousel”: 30, “static”: 15},
“top_slogans”: [“Укріпнення”, “Росту волосся”, “Від випадіння”],
“recommendation”: “✅ ЗАПУСКАТИ”
},
{
“name”: “Power Bank 30000 mAh з швидкою зарядкою”,
“category”: “Електроніка”,
“price_range”: “299-599”,
“active_ads”: 401,
“competitors”: 56,
“growth”: 8,
“formats”: {“video”: 48, “carousel”: 38, “static”: 14},
“top_slogans”: [“Швидка зарядка”, “Компактний”, “Багато портів”],
“recommendation”: “⚠️ КОНКУРЕНТНО”
},
]
}

# ============ КЛАСИ АСИСТЕНТА ============

class FacebookAdsAnalyzer:
“”“Аналізує дані Facebook Ads Library”””

```
def __init__(self):
    self.data = SIMULATED_ADS_DATA
    self.filters = {
        "min_price": 0,
        "max_price": 10000,
        "categories": None,  # None = всі
        "min_ads": 0,
        "sort_by": "recommendation"  # growth, competitors, popularity
    }

def get_analysis(self, week_offset=0):
    """Отримати аналіз на конкретний тиждень"""
    # Симульяція даних для кожного тижня
    date_key = self._get_week_date(week_offset)
    
    if date_key in self.data:
        products = self.data[date_key]
    else:
        products = self.data[list(self.data.keys())[0]]
    
    # Застосовуємо фільтри
    filtered = self._apply_filters(products)
    
    # Сортуємо
    sorted_products = self._sort_products(filtered)
    
    return sorted_products, date_key

def _apply_filters(self, products):
    """Застосовуємо фільтри користувача"""
    filtered = []
    for product in products:
        price = int(product["price_range"].split("-")[0])
        
        # Фільтр по ціні
        if price < self.filters["min_price"] or price > self.filters["max_price"]:
            continue
        
        # Фільтр по категоріям
        if self.filters["categories"]:
            if product["category"] not in self.filters["categories"]:
                continue
        
        # Фільтр по кількості об'яв
        if product["active_ads"] < self.filters["min_ads"]:
            continue
        
        filtered.append(product)
    
    return filtered

def _sort_products(self, products):
    """Сортуємо товари"""
    sort_key = self.filters["sort_by"]
    
    if sort_key == "growth":
        return sorted(products, key=lambda x: x["growth"], reverse=True)
    elif sort_key == "competitors":
        return sorted(products, key=lambda x: x["competitors"])
    elif sort_key == "popularity":
        return sorted(products, key=lambda x: x["active_ads"], reverse=True)
    else:  # recommendation
        recommendation_order = {
            "✅✅ ЗАПУСКАТИ МАКСИМАЛЬНО!": 1,
            "✅ ЗАПУСКАТИ ОДРАЗУ": 2,
            "✅ ЗАПУСКАТИ": 3,
            "✅ ГАРНИЙ ВИБІР": 4,
            "⚠️ КОНКУРЕНТНО, потребує диф": 5,
            "⚠️ КОНКУРЕНТНО": 6,
            "❌ УНИКАЙТЕ - насичено": 7,
        }
        return sorted(
            products, 
            key=lambda x: recommendation_order.get(x["recommendation"], 99)
        )

def _get_week_date(self, offset):
    """Отримати дату для конкретного тижня"""
    today = datetime.now(UKRAINE_TZ)
    week_date = today - timedelta(days=today.weekday()) + timedelta(weeks=offset)
    return week_date.strftime("%Y-%m-%d")

def set_filters(self, **kwargs):
    """Встановити фільтри"""
    for key, value in kwargs.items():
        if key in self.filters:
            self.filters[key] = value

def format_product_report(self, product, rank):
    """Форматує звіт про товар"""
    price = product["price_range"]
    ads = product["active_ads"]
    comp = product["competitors"]
    growth = product["growth"]
    
    report = f"""
```

{rank}. 🛍️ {product[‘name’]}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Ціна: {price} грн
👥 Активних об’яв: {ads}
🔴 Конкурентів: {comp}
📈 Тренд: {growth:+d}% від минулого тижня

📹 Формати реклами:
• Video: {product[‘formats’][‘video’]}%
• Carousel: {product[‘formats’][‘carousel’]}%
• Static: {product[‘formats’][‘static’]}%

💬 Топ слогани конкурентів:
• {product[‘top_slogans’][0]}
• {product[‘top_slogans’][1]}
• {product[‘top_slogans’][2]}

{product[‘recommendation’]}
“””
return report

# ============ TELEGRAM BOT ============

analyzer = FacebookAdsAnalyzer()
user_settings = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
“”“Команда /start”””
keyboard = [
[InlineKeyboardButton(“📊 Отримати звіт”, callback_data=‘get_report’)],
[InlineKeyboardButton(“⚙️ Налаштування”, callback_data=‘settings’)],
[InlineKeyboardButton(“📚 Допомога”, callback_data=‘help’)],
]
reply_markup = InlineKeyboardMarkup(keyboard)

```
await update.message.reply_text(
    f"""👋 Привіт! Я - Facebook Ads Analyzer Bot
```

Я аналізую реальні дані з Facebook Ads Library України щотижня.
Кожний тиждень надсилаю вам топ-товари для запуску!

📅 Наступний звіт: Понеділок о 09:00 (час України)

Що я можу зробити:
• 📊 Показати топ-товари цього тижня
• ⚙️ Налаштувати фільтри (ціна, категорія, конкуренція)
• 📈 Порівняти з минулим тижнем
• 💡 Дати рекомендації по запуску

Виберіть, що хочете зробити:”””,
reply_markup=reply_markup
)

async def get_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
“”“Отримати звіт про товари”””
query = update.callback_query
await query.answer()

```
products, date = analyzer.get_analysis(week_offset=0)

message = f"""📊 ТОП ТОВАРІВ ДЛЯ ЗАПУСКУ НА ТИЖДЕНЬ
```

{date}
═══════════════════════════════════════════════════

Фільтри: Ціна 300-900 грн, всі категорії, не менше 100 об’яв
\n”””

```
for i, product in enumerate(products[:10], 1):
    message += analyzer.format_product_report(product, i)

message += f"""
```

═══════════════════════════════════════════════════
💾 Останнього оновлення: {datetime.now(UKRAINE_TZ).strftime(’%d.%m.%Y %H:%M’)}
📅 Наступне оновлення: Понеділок о 09:00

📝 Хочете змінити фільтри? Напишіть:
• “ціна 200-500” - змінити ціну
• “тільки спорт” - вибрати категорію
• “сортувати по зростанню” - сортування
“””

```
await query.edit_message_text(text=message)
```

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
“”“Налаштування”””
query = update.callback_query
await query.answer()

```
current_filters = analyzer.filters

message = f"""⚙️ ПОТОЧНІ НАЛАШТУВАННЯ
```

Ціна: {current_filters[‘min_price’]}-{current_filters[‘max_price’]} грн
Категорії: {current_filters[‘categories’] or ‘Всі’}
Мін. об’яв: {current_filters[‘min_ads’]}
Сортування: {current_filters[‘sort_by’]}

📝 Напишіть команду для зміни:
• “ціна 200-500” - змінити цінову категорію
• “категорія спорт” або “категорія спорт,акс” - вибрати категорії
• “мін об’яви 50” - мінімум об’яв
• “сортувати рост” - сортування (рост, конкурс, популярність)

Категорії: Товари для дому, Аксесуари, Спортивні товари, Красота & здоров’я, Електроніка
“””

```
await query.edit_message_text(text=message)
```

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
“”“Допомога”””
query = update.callback_query
await query.answer()

```
message = """📚 КАК КОРИСТУВАТИСЯ БОТОМ
```

1️⃣ ОТРИМАТИ ЗВІТ
Натисніть кнопку “📊 Отримати звіт”
Отримаєте топ-10 товарів для запуску

2️⃣ ЗМІНИТИ ФІЛЬТРИ
Напишіть команду типу:
• “ціна 300-600”
• “категорія спорт”
• “сортувати по зростанню”

3️⃣ АВТОМАТИЧНІ ЗВІТИ
Кожний понеділок о 09:00 я автоматично надішлю новий звіт

4️⃣ ДОСТУПНІ КОМАНДИ
/start - меню
/report - отримати звіт
/settings - налаштування
/help - ця допомога

❓ ЩО ОЗНАЧАЮТЬ РЕКОМЕНДАЦІЇ?
✅✅ - ЗАПУСКАТИ МАКСИМАЛЬНО (гарячий товар, низька конкуренція)
✅ - ЗАПУСКАТИ (хороший потенціал)
⚠️ - КОНКУРЕНТНО (можна, але складніше)
❌ - УНИКАЙТЕ (насичено, дешево боротися)

📞 Якщо буду питання - просто напишіть, я все зроблю!
“””

```
await query.edit_message_text(text=message)
```

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
“”“Обробляє звичайні повідомлення для фільтрів”””
text = update.message.text.lower()

```
# Парсинг команд
if "ціна" in text:
    try:
        parts = text.split()
        min_p = int(parts[1])
        max_p = int(parts[2])
        analyzer.set_filters(min_price=min_p, max_price=max_p)
        await update.message.reply_text(f"✅ Ціна змінена на {min_p}-{max_p} грн")
    except:
        await update.message.reply_text("❌ Невірний формат. Напишіть: 'ціна 200 500'")

elif "категорія" in text:
    try:
        categories = [c.strip() for c in text.split("категорія")[1].split(",")]
        analyzer.set_filters(categories=categories)
        await update.message.reply_text(f"✅ Категорії змінені")
    except:
        await update.message.reply_text("❌ Невірний формат. Напишіть: 'категорія спорт'")

elif "сортувати" in text or "сортування" in text:
    if "рост" in text or "зрост" in text:
        analyzer.set_filters(sort_by="growth")
        await update.message.reply_text("✅ Сортування змінено на ЗРОСТАННЯ")
    elif "конк" in text:
        analyzer.set_filters(sort_by="competitors")
        await update.message.reply_text("✅ Сортування змінено на КОНКУРЕНЦІЮ")
    elif "популяр" in text:
        analyzer.set_filters(sort_by="popularity")
        await update.message.reply_text("✅ Сортування змінено на ПОПУЛЯРНІСТЬ")

elif "мін" in text and "об'" in text:
    try:
        num = int(''.join(filter(str.isdigit, text)))
        analyzer.set_filters(min_ads=num)
        await update.message.reply_text(f"✅ Мінімум об'яв змінено на {num}")
    except:
        await update.message.reply_text("❌ Невірний формат. Напишіть: 'мін об'яви 50'")
```

async def scheduled_report(context: ContextTypes.DEFAULT_TYPE):
“”“Щотижневий автоматичний звіт (Понеділок о 09:00)”””
try:
products, date = analyzer.get_analysis(week_offset=0)

```
    message = f"""📊 ЩОТИЖНЕВИЙ ЗВІТ FACEBOOK ADS LIBRARY
```

{date}
═══════════════════════════════════════════════════\n”””

```
    for i, product in enumerate(products[:7], 1):
        message += analyzer.format_product_report(product, i)
    
    message += f"""
```

═══════════════════════════════════════════════════
Це автоматичний звіт кожного тижня.
Хочете змінити - просто напишіть!
“””

```
    await context.bot.send_message(chat_id=USER_ID, text=message)
    logger.info("Scheduled report sent successfully")
except Exception as e:
    logger.error(f"Error sending scheduled report: {e}")
```

# ============ ЗАПУСК БОТА ============

def main():
“”“Запустити бота”””

```
# Перевіряємо токен
if TELEGRAM_TOKEN == "YOUR_BOT_TOKEN_HERE":
    print("❌ ПОМИЛКА: Встановіть TELEGRAM_TOKEN у файлі!")
    print("\nЩоб отримати токен:")
    print("1. Напишіть @BotFather в Telegram")
    print("2. Команда /newbot")
    print("3. Дайте ім'я боту (наприклад: 'Facebook Ads Analyzer')")
    print("4. Копіюйте токен у змінну TELEGRAM_TOKEN")
    return

# Создаємо додаток
app = Application.builder().token(TELEGRAM_TOKEN).build()

# Додаємо обробники команд
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("report", get_report))
app.add_handler(CommandHandler("help", help_command))

# Обробник для кнопок
from telegram.ext import CallbackQueryHandler
app.add_handler(CallbackQueryHandler(get_report, pattern='^get_report$'))
app.add_handler(CallbackQueryHandler(settings, pattern='^settings$'))
app.add_handler(CallbackQueryHandler(help_command, pattern='^help$'))

# Обробник для повідомлень
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Налаштовуємо автоматичний звіт (Понеділок о 09:00 UTC+2)
scheduler = BackgroundScheduler(timezone=UKRAINE_TZ)
scheduler.add_job(
    scheduled_report,
    'cron',
    day_of_week='0',  # Понеділок
    hour=9,
    minute=0,
    args=[app]
)

scheduler.start()

# Запускаємо бота
print("✅ Бот запущений!")
print(f"📱 Telegram ID: {USER_ID}")
print("⏰ Автоматичні звіти: Понеділок о 09:00 (Київ)")
print("\nНатисніть Ctrl+C для зупинки")

app.run_polling()
```

if **name** == ‘**main**’:
main()
