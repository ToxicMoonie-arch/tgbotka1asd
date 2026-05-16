from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
import asyncio
from aiogram.types import CallbackQuery
from aiogram import F
import random

TOKEN = "8094622496:AAG6UnfKNMxx39MpLhw7yqCJOtcq75lZNrU"
ADMIN_ID = 8586842368

bot = Bot(token=TOKEN)
dp = Dispatcher()

cities = {
    "Белгород": {"🧂Соли PVP 1г": 5600, "🧂Соли PVP 0.5г": 2950, "💠Мяу(Кристалл/Мука) 1г": 3025, "💠Мяу(Кристалл/Мука) 0.5г": 1675,
                 "🌿Бошки 2г": 8100, "🌿Бошки 5г": 17450, "🪴Гаш 1г": 4575, "🪴Гаш 2г": 8450},
    "Москва":   {"🧂Соли PVP 1г": 5450, "🧂Соли PVP 0.5г": 3075, "💠Мяу(Кристалл/Мука) 1г": 2900, "💠Мяу(Кристалл/Мука) 0.5г": 1700,
                 "🌿Бошки 2г": 7950, "🌿Бошки 5г": 17600, "🪴Гаш 1г": 4450, "🪴Гаш 2г": 8575},
    "Лобня":    {"🧂Соли PVP 1г": 5575, "🧂Соли PVP 0.5г": 3000, "💠Мяу(Кристалл/Мука) 1г": 3050, "💠Мяу(Кристалл/Мука) 0.5г": 1550,
                 "🌿Бошки 2г": 8175, "🌿Бошки 5г": 17575, "🪴Гаш 1г": 4600, "🪴Гаш 2г": 8500},
    "СПБ":      {"🧂Соли PVP 1г": 5500, "🧂Соли PVP 0.5г": 2950, "💠Мяу(Кристалл/Мука) 1г": 2975, "💠Мяу(Кристалл/Мука) 0.5г": 1650,
                 "🌿Бошки 2г": 8050, "🌿Бошки 5г": 17425, "🪴Гаш 1г": 4525, "🪴Гаш 2г": 8425},
    "Екб":      {"🧂Соли PVP 1г": 5650, "🧂Соли PVP 0.5г": 3050, "💠Мяу(Кристалл/Мука) 1г": 2875, "💠Мяу(Кристалл/Мука) 0.5г": 1575,
                 "🌿Бошки 2г": 7925, "🌿Бошки 5г": 17650, "🪴Гаш 1г": 4475, "🪴Гаш 2г": 8600},
    "ДНР":      {"🧂Соли PVP 1г": 5425, "🧂Соли PVP 0.5г": 2900, "💠Мяу(Кристалл/Мука) 1г": 3000, "💠Мяу(Кристалл/Мука) 0.5г": 1675,
                 "🌿Бошки 2г": 8125, "🌿Бошки 5г": 17375, "🪴Гаш 1г": 4550, "🪴Гаш 2г": 8475},
    "Краснодар":{"🧂Соли PVP 1г": 5525, "🧂Соли PVP 0.5г": 3025, "💠Мяу(Кристалл/Мука) 1г": 2925, "💠Мяу(Кристалл/Мука) 0.5г": 1625,
                 "🌿Бошки 2г": 8000, "🌿Бошки 5г": 17550, "🪴Гаш 1г": 4625, "🪴Гаш 2г": 8550},
    "Мурманск":   {"🧂Соли PVP 1г": 5475, "🧂Соли PVP 0.5г": 2975, "💠Мяу(Кристалл/Мука) 1г": 3075, "💠Мяу(Кристалл/Мука) 0.5г": 1725,
                 "🌿Бошки 2г": 8075, "🌿Бошки 5г": 17475, "🪴Гаш 1г": 4500, "🪴Гаш 2г": 8525},
}

# Индексы городов и товаров для коротких callback_data
city_index = {i: city for i, city in enumerate(cities)}
city_reverse = {city: i for i, city in enumerate(cities)}

pending_orders = {}
user_to_admin_message = {}
admin_message_to_user = {}
active_chats = set()
used_order_numbers = set()


def generate_order_number():
    while True:
        number = random.randint(100000, 999999)
        if number not in used_order_numbers:
            used_order_numbers.add(number)
            return number


def cities_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=city, callback_data=f"c_{i}")]
            for i, city in city_index.items()
        ]
    )


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
            [InlineKeyboardButton(text="◀️ Назад к товарам", callback_data=f"back_products_{city_i}")]
        ]
    )


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Выберите город, в котором хотите приобрести товар. 🌿🐈🧂",
        reply_markup=cities_keyboard()
    )


@dp.callback_query(F.data == "back_cities")
async def back_to_cities(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите город, в котором хотите приобрести товар. 🌿🐈🧂",
        reply_markup=cities_keyboard()
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("back_products_"))
async def back_to_products(callback: CallbackQuery):
    city_i = int(callback.data.removeprefix("back_products_"))
    city = city_index[city_i]
    await callback.message.edit_text(
        f"Вы выбрали: {city}\n\nТеперь выберите товар:",
        reply_markup=products_keyboard(city_i)
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("c_"))
async def city_handler(callback: CallbackQuery):
    city_i = int(callback.data.removeprefix("c_"))
    city = city_index.get(city_i)

    if not city:
        await callback.answer("Город не найден.", show_alert=True)
        return

    await callback.message.edit_text(
        f"Вы выбрали: {city}\n\nТеперь выберите товар:",
        reply_markup=products_keyboard(city_i)
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("p_"))
async def product_handler(callback: CallbackQuery):
    _, city_i_str, product_i_str = callback.data.split("_")
    city_i = int(city_i_str)
    product_i = int(product_i_str)

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
    }

    await callback.message.edit_text(
        f"Заказ номер: #{order_number}\n\n"
        f"🛒 {product}\n"
        f"📍 Город: {city}\n"
        f"💰 Сумма к оплате: {price} ₽\n\n"
        f"Переведите {price} ₽ на карту:\n"
        f"2200701356924784 Т-Банк\n\n"
        f"После оплаты пришлите скриншот или PDF чека сюда 👇",
        reply_markup=payment_keyboard(city_i)
    )
    await callback.answer()


@dp.message(F.photo & (F.chat.id != ADMIN_ID))
async def photo_handler(message: Message):
    user_id = message.from_user.id

    if user_id in pending_orders:
        order = pending_orders.pop(user_id)
        active_chats.add(user_id)

        caption = (
            f"🔔 Новый заказ!\n"
            f"Заказ номер: #{order['order_number']}\n\n"
            f"👤 Покупатель: {order['full_name']} (@{order['username']})\n"
            f"🆔 ID: {user_id}\n"
            f"📍 Город: {order['city']}\n"
            f"🛒 Товар: {order['product']}\n"
            f"💰 Сумма: {order['price']} ₽\n\n"
            f"💬 Отвечайте reply на любое сообщение покупателя"
        )

        sent = await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=message.photo[-1].file_id,
            caption=caption,
        )

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
            caption=f"📸 Фото от {message.from_user.full_name} (ID: {user_id})"
        )
        user_to_admin_message[user_id] = sent.message_id
        admin_message_to_user[sent.message_id] = user_id

    else:
        await message.answer("Сначала выберите товар через /start")


@dp.message(F.document & (F.chat.id != ADMIN_ID))
async def document_handler(message: Message):
    user_id = message.from_user.id

    if user_id in pending_orders:
        order = pending_orders.pop(user_id)
        active_chats.add(user_id)

        caption = (
            f"🔔 Новый заказ!\n"
            f"Заказ номер: #{order['order_number']}\n\n"
            f"👤 Покупатель: {order['full_name']} (@{order['username']})\n"
            f"🆔 ID: {user_id}\n"
            f"📍 Город: {order['city']}\n"
            f"🛒 Товар: {order['product']}\n"
            f"💰 Сумма: {order['price']} ₽\n\n"
            f"💬 Отвечайте reply на любое сообщение покупателя"
        )

        sent = await bot.send_document(
            chat_id=ADMIN_ID,
            document=message.document.file_id,
            caption=caption,
        )

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
            caption=f"📄 Документ от {message.from_user.full_name} (ID: {user_id})"
        )
        user_to_admin_message[user_id] = sent.message_id
        admin_message_to_user[sent.message_id] = user_id

    else:
        await message.answer("Сначала выберите товар через /start")


@dp.message(F.chat.id != ADMIN_ID)
async def user_message_handler(message: Message):
    user_id = message.from_user.id

    if user_id not in active_chats:
        return

    text = message.text or message.caption or ""

    forwarded = await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"💬 {message.from_user.full_name} (@{message.from_user.username or 'без username'}, ID: {user_id}):\n\n{text}"
    )

    user_to_admin_message[user_id] = forwarded.message_id
    admin_message_to_user[forwarded.message_id] = user_id


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
                text=f"💬 Продавец:\n\n{message.text}"
            )
        await message.answer("✅ Отправлено")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())