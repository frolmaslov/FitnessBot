import logging
import models
import datetime
from database_pgs import SessionLocal

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text

API_TOKEN = 'your API token'

logging.basicConfig(level=logging.INFO)

date = str(datetime.datetime.now().strftime("%Y-%m-%d"))
scheduler = AsyncIOScheduler()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
db = SessionLocal()


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="График"),
            types.KeyboardButton(text="Помощь")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )
    await message.answer("Введите вес", reply_markup=keyboard)


@dp.message_handler(Text("Помощь"))
async def send_welcome(message: types.Message):
    new_user = models.User(telegram_id=message.from_user.id, name=message.from_user.first_name, online=True, date=date)
    db.add(new_user)
    db.commit()
    await message.answer(f'Привет, {message.chat.first_name}! Это фитнес-бот. Введите желаемый вес в формате Цель - число, текущий вес в формате Вес - число.')


@dp.message_handler(Text('График'))
async def send_welcome(message: types.Message):
    new_user = db.query(models.User.weight, models.User.date).filter(models.User.weight != None).all()
    graph = []
    for el in new_user:
        data = (f'Вес: {el[0]} кг. Дата: {el[1]}')
        graph.append(data)
    await message.answer(f'Привет, {message.chat.first_name}! {graph}\n')


async def send_message(dp: Dispatcher):
    users_id = set(db.query(models.User.telegram_id).all())
    text = 'Пришло время взвеситься и ввести данные!'
    for id in users_id:
        online = db.query(models.User.online).filter(models.User.telegram_id==id[0]).all()[-1][0]
        if online:
            try:
                await bot.send_message(id[0], text)
            except Exception as e:
                print('Error:', e)


@dp.message_handler()
async def goal(message: types.Message):
    text = message.text
    if text.lower().startswith('цель'):
        weight = ''
        for char in text:
            if char.isdigit():
                weight += char
        if len(weight) > 0:
            if int(weight) < 120 and int(weight) > 30:
                new_data = models.User(telegram_id=message.from_user.id, name=message.from_user.first_name, online=True,
                                       date=date, weight_wished=weight)
                db.add(new_data)
                db.commit()
                await message.reply(f'Вы хотите весить {weight} кг! Данные записаны!')
            else:
                await message.reply(f'Введите верное число!')
        else:
            await message.reply(f'Вы забыли ввести число!')

    elif text.lower().startswith('вес'):
        weight_current = ''
        weight_wished = db.query(models.User.weight_wished).filter(models.User.weight_wished != None).all()[-1][0]

        for char in text:
            if char.isdigit():
                weight_current += char
        if weight_current > '':
            if int(weight_current) == weight_wished:
                new_data = models.User(telegram_id=message.from_user.id, name=message.from_user.first_name, online=False,
                                       date=date, weight=weight_current, weight_wished=weight_wished)
                db.add(new_data)
                db.commit()
                await message.reply(f'Вы достигли желаемого веса! Уведомления больше примылаться не будут.')
            elif int(weight_current) < 120 and int(weight_current) > 30:
                new_data = models.User(telegram_id=message.from_user.id,
                                      weight=weight_current, name=message.from_user.first_name, online=True,                                   date=date)
                db.add(new_data)
                db.commit()
                await message.reply(f'Ваш вес {weight_current} кг! Данные записаны!')
            else:
                await message.reply(f'Введите верное число!')
        else:
            await message.reply(f'Вы забыли ввести число!')
    else:
        await message.reply(f'Введите верную команду!')


async def verify():
    users_id = db.query(models.User.telegram_id).all()
    for id in set(users_id):
        last_date = db.query(models.User.date).filter(models.User.telegram_id == id[0]).all()
        if last_date[-1][0] != date:
            c_weight = db.query(models.User.weight).filter(models.User.telegram_id == id[0]).all()[-1]
            c_name = db.query(models.User.name).filter(models.User.telegram_id == id[0]).first()
            new_user = models.User(telegram_id=id[0], name=c_name[0], weight=c_weight[0], online=True, date=date)
            db.add(new_user)
            db.commit()
            print(new_user)


scheduler.add_job(verify, 'cron', day_of_week='mon-sun', hour=23, minute=45)
scheduler.add_job(send_message, 'cron', day_of_week='mon-sun', hour=12, minute=00, args=(dp,))


if __name__ == '__main__':
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)
