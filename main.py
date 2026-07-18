from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
import asyncio
from aiogram.types import CallbackQuery
from aiogram import F
import random

TOKEN = "8846875551:AAHzTm4I1lyDqZVAOOffV9ubpXarIvvRPjw"
ADMIN_ID = 8091903185

bot = Bot(token=TOKEN)
dp = Dispatcher()

cities = {
    "Белгород": {"🧂Соли PVP 1г": 5600, "🧂Соли PVP 0.5г": 2950, "💠Мяу(Кристалл/Мука) 1г": 3025, "💠Мяу(Кристалл/Мука) 0.5г": 1675,
                 "🪴Гаш 2г": 8100, "🪴Гаш 5г": 17450, "🌿Бошки 1г": 4575, "🌿Бошки 2г": 8450},
    "Москва":   {"🧂Соли PVP 1г": 5450, "🧂Соли PVP 0.5г": 3075, "💠Мяу(Кристалл/Мука) 1г": 2900, "💠Мяу(Кристалл/Мука) 0.5г": 1700,
                 "🪴Гаш 2г": 7950, "🪴Гаш 5г": 17600, "🌿Бошки 1г": 4450, "🌿Бошки 2г": 8575},
    "Лобня":    {"🧂Соли PVP 1г": 5575, "🧂Соли PVP 0.5г": 3000, "💠Мяу(Кристалл/Мука) 1г": 3050, "💠Мяу(Кристалл/Мука) 0.5г": 1550,
                 "🪴Гаш 2г": 8175, "🪴Гаш 5г": 17575, "🌿Бошки 1г": 4600, "🌿Бошки 2г": 8500},
    "СПБ":      {"🧂Соли PVP 1г": 5500, "🧂Соли PVP 0.5г": 2950, "💠Мяу(Кристалл/Мука) 1г": 2975, "💠Мяу(Кристалл/Мука) 0.5г": 1650,
                 "🪴Гаш 2г": 8050, "🪴Гаш 5г": 17425, "🌿Бошки 1г": 4525, "🌿Бошки 2г": 8425},
    "Екб":      {"🧂Соли PVP 1г": 5650, "🧂Соли PVP 0.5г": 3050, "💠Мяу(Кристалл/Мука) 1г": 2875, "💠Мяу(Кристалл/Мука) 0.5г": 1575,
                 "🪴Гаш 2г": 7925, "🪴Гаш 5г": 17650, "🌿Бошки 1г": 4475, "🌿Бошки 2г": 8600},
    "ДНР/ЛНР":      {"🧂Соли PVP 1г": 5425, "🧂Соли PVP 0.5г": 2900, "💠Мяу(Кристалл/Мука) 1г": 3000, "💠Мяу(Кристалл/Мука) 0.5г": 1675,
                 "🪴Гаш 2г": 8125, "🪴Гаш 5г": 17375, "🌿Бошки 1г": 4550, "🌿Бошки 2г": 8475},
    "Курск":{"🧂Соли PVP 1г": 5525, "🧂Соли PVP 0.5г": 3025, "💠Мяу(Кристалл/Мука) 1г": 2925, "💠Мяу(Кристалл/Мука) 0.5г": 1625,
                 "🪴Гаш 2г": 8000, "🪴Гаш 5г": 17550, "🌿Бошки 1г": 4625, "🌿Бошки 2г": 8550},
    "Мурманск": {"🧂Соли PVP 1г": 5475, "🧂Соли PVP 0.5г": 2975, "💠Мяу(Кристалл/Мука) 1г": 3075, "💠Мяу(Кристалл/Мука) 0.5г": 1725,
                 "🪴Гаш 2г": 8075, "🪴Гаш 5г": 17475, "🌿Бошки 1г": 4500, "🌿Бошки 2г": 8525},
}

wholesale_types = {
    "🧂Соли PVP": 5500,
    "💠Мяу(Кристалл/Мука)": 3000,
    "🪴Гаш": round((8050/2 + 17500/5) / 2),
    "🌿Бошки": round((4550/1 + 8500/2) / 2),
}

wholesale_index = {i: name for i, name in enumerate(wholesale_types)}
city_index = {i: city for i, city in enumerate(cities)}

pending_orders = {}
user_to_admin_message = {}
admin_message_to_user = {}
active_chats = set()
used_order_numbers = set()
wholesale_state = {}


def generate_order_number():
    while True:
        number = random.randint(100000, 999999)
        if number not in used_order_numbers:
            used_order_numbers.add(number)
            return number


def clear_user_state(user_id: int):
    """Сбрасывает pending_orders и wholesale_state пользователя."""
    pending_orders.pop(user_id, None)
    wholesale_state.pop(user_id, None)


# ─── Клавиатуры ────────────────────────────────────────────────────────────────

def main_keyboard():
    buttons = [
        [InlineKeyboardButton(text=f"📍 {city}", callback_data=f"c_{i}")]
        for i, city in city_index.items()
    ]
    buttons.append([InlineKeyboardButton(text="📦 Оптовая покупка", callback_data="wholesale")])
    buttons.append([InlineKeyboardButton(text="💬 Поддержка (лайв-чат)", callback_data="support")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def products_keyboard(city_i: int):
    city = city_index[city_i]
    products = list(cities[city].items())
    return InlineKeyboardMarkup(
        inline_keyboard=[
            *[
                [InlineKeyboardButton(text=f"{product} — {price} ₽",
                                      callback_data=f"p_{city_i}_{j}")]
                for j, (product, price) in enumerate(products)
            ],
            [InlineKeyboardButton(text="◀️ Назад к городам", callback_data="back_cities")]
        ]
    )


def payment_keyboard(city_i: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Написать в поддержку", callback_data="support_from_order")],
            [InlineKeyboardButton(text="◀️ Назад к товарам", callback_data=f"back_products_{city_i}")]
        ]
    )


def wholesale_region_keyboard():
    buttons = [
        [InlineKeyboardButton(text=f"📍 {city}", callback_data=f"ws_city_{i}")]
        for i, city in city_index.items()
    ]
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_cities")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def wholesale_products_keyboard(city_i: int):
    buttons = [
        [InlineKeyboardButton(
            text=f"{name} — {ppg} ₽/г",
            callback_data=f"ws_p_{city_i}_{i}"
        )]
        for i, (name, ppg) in enumerate(wholesale_types.items())
    ]
    buttons.append([InlineKeyboardButton(text="◀️ Назад к регионам", callback_data="wholesale")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def wholesale_amounts_keyboard(city_i: int, product_i: int):
    options = list(range(1, 11))
    rows = []
    row = []
    for opt in options:
        row.append(InlineKeyboardButton(
            text=f"{opt}г",
            callback_data=f"ws_g_{city_i}_{product_i}_{opt}"
        ))
        if len(row) == 5:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(
        text="✏️ Ввести своё количество",
        callback_data=f"ws_custom_{city_i}_{product_i}"
    )])
    rows.append([InlineKeyboardButton(
        text="◀️ Назад к товарам",
        callback_data=f"ws_city_{city_i}"
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def wholesale_payment_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Написать в поддержку", callback_data="support_from_order")],
            [InlineKeyboardButton(text="◀️ Назад к опту", callback_data="wholesale")]
        ]
    )


def support_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад в главное меню", callback_data="back_cities")]
        ]
    )


# ─── Команды ───────────────────────────────────────────────────────────────────

@dp.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    clear_user_state(user_id)
    active_chats.discard(user_id)
    await message.answer(
        "Выберите город, в котором хотите приобрести товар. 🌿🐈🧂",
        reply_markup=main_keyboard()
    )


# ─── Навигация ─────────────────────────────────────────────────────────────────

@dp.callback_query(F.data == "back_cities")
async def back_to_cities(callback: CallbackQuery):
    user_id = callback.from_user.id
    clear_user_state(user_id)
    active_chats.discard(user_id)
    await callback.answer()
    await callback.message.answer(
        "Выберите город, в котором хотите приобрести товар. 🌿🐈🧂",
        reply_markup=main_keyboard()
    )


@dp.callback_query(F.data.startswith("back_products_"))
async def back_to_products(callback: CallbackQuery):
    clear_user_state(callback.from_user.id)
    city_i = int(callback.data.removeprefix("back_products_"))
    city = city_index.get(city_i)
    if not city:
        await callback.answer("Город не найден.", show_alert=True)
        return
    await callback.message.edit_text(
        f"Вы выбрали: 📍 {city}\n\nТеперь выберите товар:",
        reply_markup=products_keyboard(city_i)
    )
    await callback.answer()


# ─── Розничные города и товары ─────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("c_"))
async def city_handler(callback: CallbackQuery):
    city_i = int(callback.data.removeprefix("c_"))
    city = city_index.get(city_i)
    if not city:
        await callback.answer("Город не найден.", show_alert=True)
        return
    await callback.message.edit_text(
        f"Вы выбрали: 📍 {city}\n\nТеперь выберите товар:",
        reply_markup=products_keyboard(city_i)
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("p_"))
async def product_handler(callback: CallbackQuery):
    # split с maxsplit=2 чтобы правильно парсить при любых индексах
    parts = callback.data.split("_", 2)
    city_i = int(parts[1])
    product_i = int(parts[2])

    city = city_index.get(city_i)
    if not city:
        await callback.answer("Город не найден.", show_alert=True)
        return

    products = list(cities[city].items())
    if product_i >= len(products):
        await callback.answer("Товар не найден.", show_alert=True)
        return

    product, price = products[product_i]
    order_number = generate_order_number()

    pending_orders[callback.from_user.id] = {
        "city": city,
        "city_i": city_i,
        "product": product,
        "price": price,
        "username": callback.from_user.username or "без username",
        "full_name": callback.from_user.full_name,
        "order_number": order_number,
        "type": "retail",
    }

    await callback.message.edit_text(
        f"Заказ номер: #{order_number}\n\n"
        f"🛒 {product}\n"
        f"📍 Город: {city}\n"
        f"💰 Сумма к оплате: {price} ₽\n\n"
        f"Переведите {price} ₽ на карту:\n"
        f"2202202533173096 Сбер\n\n"
        f"После оплаты пришлите скриншот или PDF чека сюда 👇",
        reply_markup=payment_keyboard(city_i)
    )
    await callback.answer()


# ─── Поддержка ─────────────────────────────────────────────────────────────────

@dp.callback_query(F.data == "support")
async def support_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    active_chats.add(user_id)
    await callback.answer()
    await callback.message.answer(
        "💬 Вы подключились к чату поддержки.\n\n"
        "Напишите ваш вопрос, и наш оператор ответит вам в ближайшее время.\n\n"
        "Мы работаем ежедневно и стараемся отвечать как можно быстрее 🕐",
        reply_markup=support_keyboard()
    )
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"🆕 Новый запрос в поддержку!\n"
            f"👤 {callback.from_user.full_name} (@{callback.from_user.username or 'без username'})\n"
            f"🆔 ID: {user_id}\n\n"
            f"Пользователь ожидает ответа. Отвечайте reply на его сообщения."
        )
    )


# ─── Поддержка прямо со страницы оплаты ───────────────────────────────────────

@dp.callback_query(F.data == "support_from_order")
async def support_from_order_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    pending_orders.pop(user_id, None)
    active_chats.add(user_id)
    # answer вместо edit_text — после получения чека старое сообщение уже не inline
    await callback.message.answer(
        "💬 Вы подключились к чату поддержки.\n\n"
        "Опишите вашу проблему, и наш оператор поможет вам.\n\n"
        "Мы работаем ежедневно и стараемся отвечать как можно быстрее 🕐",
        reply_markup=support_keyboard()
    )
    await callback.answer()
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"🆕 Запрос в поддержку со страницы оплаты!\n"
            f"👤 {callback.from_user.full_name} (@{callback.from_user.username or 'без username'})\n"
            f"🆔 ID: {user_id}\n\n"
            f"У пользователя проблема с оплатой. Отвечайте reply на его сообщения."
        )
    )
    await callback.answer()


# ─── Опт: шаг 1 — регион ──────────────────────────────────────────────────────

@dp.callback_query(F.data == "wholesale")
async def wholesale_handler(callback: CallbackQuery):
    wholesale_state.pop(callback.from_user.id, None)
    await callback.message.edit_text(
        "📦 Оптовая покупка\n\n"
        "Выберите ваш регион:",
        reply_markup=wholesale_region_keyboard()
    )
    await callback.answer()


# ─── Опт: шаг 2 — товар ───────────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("ws_city_"))
async def wholesale_city_handler(callback: CallbackQuery):
    wholesale_state.pop(callback.from_user.id, None)
    city_i = int(callback.data.removeprefix("ws_city_"))
    city = city_index.get(city_i)
    if not city:
        await callback.answer("Регион не найден.", show_alert=True)
        return
    await callback.message.edit_text(
        f"📦 Оптовая покупка\n"
        f"📍 Регион: {city}\n\n"
        f"Выберите товар (цена за 1 грамм):",
        reply_markup=wholesale_products_keyboard(city_i)
    )
    await callback.answer()


# ─── Опт: шаг 3 — количество граммов ─────────────────────────────────────────

@dp.callback_query(F.data.startswith("ws_p_"))
async def wholesale_product_handler(callback: CallbackQuery):
    parts = callback.data.split("_")
    city_i = int(parts[2])
    product_i = int(parts[3])

    city = city_index.get(city_i)
    product = wholesale_index.get(product_i)
    if not city or not product:
        await callback.answer("Не найдено.", show_alert=True)
        return

    ppg = wholesale_types[product]

    await callback.message.edit_text(
        f"📦 Оптовая покупка\n"
        f"📍 Регион: {city}\n"
        f"🛒 {product}\n"
        f"💰 Цена: {ppg} ₽/г\n\n"
        f"Выберите количество граммов:",
        reply_markup=wholesale_amounts_keyboard(city_i, product_i)
    )
    await callback.answer()


# ─── Опт: шаг 4 — оформление (кнопка) ────────────────────────────────────────

@dp.callback_query(F.data.startswith("ws_g_"))
async def wholesale_grams_handler(callback: CallbackQuery):
    parts = callback.data.split("_")
    city_i = int(parts[2])
    product_i = int(parts[3])
    grams = int(parts[4])

    city = city_index.get(city_i)
    product = wholesale_index.get(product_i)
    if not city or not product:
        await callback.answer("Не найдено.", show_alert=True)
        return

    ppg = wholesale_types[product]
    total = ppg * grams
    order_number = generate_order_number()

    pending_orders[callback.from_user.id] = {
        "city": city,
        "product": product,
        "grams": grams,
        "price_per_gram": ppg,
        "price": total,
        "username": callback.from_user.username or "без username",
        "full_name": callback.from_user.full_name,
        "order_number": order_number,
        "type": "wholesale",
    }

    await callback.message.edit_text(
        f"📦 Оптовый заказ номер: #{order_number}\n\n"
        f"🛒 {product}\n"
        f"📍 Регион: {city}\n"
        f"⚖️ Количество: {grams} г\n"
        f"💰 Цена за грамм: {ppg} ₽\n"
        f"💵 Итого к оплате: {total} ₽\n\n"
        f"Переведите {total} ₽ на карту:\n"
        f"2200701356924784 Т-Банк\n\n"
        f"После оплаты пришлите скриншот или PDF чека сюда 👇",
        reply_markup=wholesale_payment_keyboard()
    )
    await callback.answer()


# ─── Опт: своё количество ─────────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("ws_custom_"))
async def wholesale_custom_handler(callback: CallbackQuery):
    parts = callback.data.split("_")
    city_i = int(parts[2])
    product_i = int(parts[3])

    city = city_index.get(city_i)
    product = wholesale_index.get(product_i)
    if not city or not product:
        await callback.answer("Не найдено.", show_alert=True)
        return

    ppg = wholesale_types[product]
    wholesale_state[callback.from_user.id] = {
        "city": city,
        "city_i": city_i,
        "product": product,
        "product_i": product_i,
        "price_per_gram": ppg,
    }

    await callback.message.edit_text(
        f"📦 {product} — {ppg} ₽/г\n"
        f"📍 Регион: {city}\n\n"
        f"✏️ Введите желаемое количество граммов (целое число, минимум 1):"
    )
    await callback.answer()


# ─── Текстовые сообщения пользователей ────────────────────────────────────────

@dp.message(F.text & (F.chat.id != ADMIN_ID))
async def user_message_handler(message: Message):
    user_id = message.from_user.id

    # 1. Ввод граммов для опта
    if user_id in wholesale_state:
        state = wholesale_state[user_id]
        try:
            grams = int(message.text.strip())
            if grams < 1:
                await message.answer("❌ Минимум 1 грамм. Введите снова:")
                return

            ppg = state["price_per_gram"]
            total = ppg * grams
            order_number = generate_order_number()
            del wholesale_state[user_id]

            pending_orders[user_id] = {
                "city": state["city"],
                "product": state["product"],
                "grams": grams,
                "price_per_gram": ppg,
                "price": total,
                "username": message.from_user.username or "без username",
                "full_name": message.from_user.full_name,
                "order_number": order_number,
                "type": "wholesale",
            }

            await message.answer(
                f"📦 Оптовый заказ номер: #{order_number}\n\n"
                f"🛒 {state['product']}\n"
                f"📍 Регион: {state['city']}\n"
                f"⚖️ Количество: {grams} г\n"
                f"💰 Цена за грамм: {ppg} ₽\n"
                f"💵 Итого к оплате: {total} ₽\n\n"
                f"Переведите {total} ₽ на карту:\n"
                f"2200701356924784 Т-Банк\n\n"
                f"После оплаты пришлите скриншот или PDF чека сюда 👇",
                reply_markup=wholesale_payment_keyboard()
            )
        except ValueError:
            await message.answer("❌ Введите целое число (например: 15):")
        return

    # 2. Ожидаем чек — не пересылаем в поддержку
    if user_id in pending_orders:
        await message.answer(
            "📎 Пожалуйста, пришлите скриншот или PDF чека для подтверждения оплаты."
        )
        return

    # 3. Чат поддержки
    if user_id not in active_chats:
        return

    text = message.text or ""
    forwarded = await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"💬 {message.from_user.full_name} (@{message.from_user.username or 'без username'}, ID: {user_id}):\n\n{text}"
    )
    user_to_admin_message[user_id] = forwarded.message_id
    admin_message_to_user[forwarded.message_id] = user_id


# ─── Фото от пользователя ──────────────────────────────────────────────────────

@dp.message(F.photo & (F.chat.id != ADMIN_ID))
async def photo_handler(message: Message):
    user_id = message.from_user.id

    if user_id in pending_orders:
        order = pending_orders.pop(user_id)
        active_chats.add(user_id)

        if order["type"] == "wholesale":
            caption = (
                f"🔔 Новый ОПТОВЫЙ заказ!\n"
                f"Заказ номер: #{order['order_number']}\n\n"
                f"👤 {order['full_name']} (@{order['username']})\n"
                f"🆔 ID: {user_id}\n"
                f"📍 Регион: {order['city']}\n"
                f"🛒 Товар: {order['product']}\n"
                f"⚖️ Количество: {order['grams']} г\n"
                f"💰 Цена за грамм: {order['price_per_gram']} ₽\n"
                f"💵 Итого: {order['price']} ₽\n\n"
                f"💬 Отвечайте reply на сообщения покупателя"
            )
        else:
            caption = (
                f"🔔 Новый заказ!\n"
                f"Заказ номер: #{order['order_number']}\n\n"
                f"👤 {order['full_name']} (@{order['username']})\n"
                f"🆔 ID: {user_id}\n"
                f"📍 Город: {order['city']}\n"
                f"🛒 Товар: {order['product']}\n"
                f"💰 Сумма: {order['price']} ₽\n\n"
                f"💬 Отвечайте reply на сообщения покупателя"
            )

        sent = await bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, caption=caption)
        user_to_admin_message[user_id] = sent.message_id
        admin_message_to_user[sent.message_id] = user_id

        await message.answer(
            f"✅ Скриншот получен!\n"
            f"Заказ номер: #{order['order_number']}\n\n"
            f"Ваш заказ обрабатывается. Можете написать нам если есть вопросы 👇"
        )

    elif user_id in active_chats:
        sent = await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=message.photo[-1].file_id,
            caption=f"📸 Фото от {message.from_user.full_name} (@{message.from_user.username or 'без username'}, ID: {user_id})"
        )
        user_to_admin_message[user_id] = sent.message_id
        admin_message_to_user[sent.message_id] = user_id
        await message.answer("📨 Фото отправлено оператору.")

    else:
        await message.answer("Сначала выберите товар через /start")


# ─── Документы от пользователя ─────────────────────────────────────────────────

@dp.message(F.document & (F.chat.id != ADMIN_ID))
async def document_handler(message: Message):
    user_id = message.from_user.id

    if user_id in pending_orders:
        order = pending_orders.pop(user_id)
        active_chats.add(user_id)

        if order["type"] == "wholesale":
            caption = (
                f"🔔 Новый ОПТОВЫЙ заказ!\n"
                f"Заказ номер: #{order['order_number']}\n\n"
                f"👤 {order['full_name']} (@{order['username']})\n"
                f"🆔 ID: {user_id}\n"
                f"📍 Регион: {order['city']}\n"
                f"🛒 Товар: {order['product']}\n"
                f"⚖️ Количество: {order['grams']} г\n"
                f"💰 Цена за грамм: {order['price_per_gram']} ₽\n"
                f"💵 Итого: {order['price']} ₽\n\n"
                f"💬 Отвечайте reply на сообщения покупателя"
            )
        else:
            caption = (
                f"🔔 Новый заказ!\n"
                f"Заказ номер: #{order['order_number']}\n\n"
                f"👤 {order['full_name']} (@{order['username']})\n"
                f"🆔 ID: {user_id}\n"
                f"📍 Город: {order['city']}\n"
                f"🛒 Товар: {order['product']}\n"
                f"💰 Сумма: {order['price']} ₽\n\n"
                f"💬 Отвечайте reply на сообщения покупателя"
            )

        sent = await bot.send_document(chat_id=ADMIN_ID, document=message.document.file_id, caption=caption)
        user_to_admin_message[user_id] = sent.message_id
        admin_message_to_user[sent.message_id] = user_id

        await message.answer(
            f"✅ Чек получен!\n"
            f"Заказ номер: #{order['order_number']}\n\n"
            f"Ваш заказ обрабатывается. Можете написать нам если есть вопросы 👇"
        )

    elif user_id in active_chats:
        sent = await bot.send_document(
            chat_id=ADMIN_ID,
            document=message.document.file_id,
            caption=f"📄 Документ от {message.from_user.full_name} (@{message.from_user.username or 'без username'}, ID: {user_id})"
        )
        user_to_admin_message[user_id] = sent.message_id
        admin_message_to_user[sent.message_id] = user_id
        await message.answer("📨 Документ отправлен оператору.")

    else:
        await message.answer("Сначала выберите товар через /start")


# ─── Ответы администратора ─────────────────────────────────────────────────────

@dp.message(F.chat.id == ADMIN_ID)
async def admin_reply_handler(message: Message):
    if not message.reply_to_message:
        return

    replied_msg_id = message.reply_to_message.message_id
    user_id = admin_message_to_user.get(replied_msg_id)

    if not user_id:
        await message.answer("Не могу найти покупателя. Убедитесь что отвечаете reply на его сообщение.")
        return

    try:
        if message.photo:
            await bot.send_photo(
                chat_id=user_id,
                photo=message.photo[-1].file_id,
                caption=f"💬 Продавец:\n\n{message.caption or ''}"
            )
        elif message.document:
            await bot.send_document(
                chat_id=user_id,
                document=message.document.file_id,
                caption=f"💬 Продавец:\n\n{message.caption or ''}"
            )
        else:
            await bot.send_message(
                chat_id=user_id,
                text=f"💬 Продавец:\n\n{message.text or ''}"
            )
        await message.answer("✅ Отправлено")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())