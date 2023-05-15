import logging

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from config import TOKEN
from utils import TestStates
from messages import MESSAGES


logging.basicConfig(format=u'%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.DEBUG)


bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage()) #хранилище состояний оперативвной памяти

dp.middleware.setup(LoggingMiddleware()) #подключаем логгирование


@dp.message_handler(commands=['start'])#создаем базовые хендлеры
async def process_start_command(message: types.Message):
    await message.reply(MESSAGES['start'])


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(MESSAGES['help'])


@dp.message_handler(state='*', commands=['setstate'])
#запрашиваем текущее состояние пользователя
async def process_setstate_command(message: types.Message):
    argument = message.get_args()
    state = dp.current_state(user=message.from_user.id)
    if not argument:
        await state.reset_state() #если не задан № - сбрасываем состояние
        return await message.reply(MESSAGES['state_reset'])

    if (not argument.isdigit()) or (not int(argument) < len(TestStates.all())):
        return await message.reply(MESSAGES['invalid_key'].format(key=argument))

    await state.set_state(TestStates.all()[int(argument)])
    await message.reply(MESSAGES['state_change'], reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_1)#обработка хенддлера с первым состоянием  
async def first_test_state_case_met(message: types.Message):
    await message.reply('Первый!', reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_2[0])#обработка хендлера со вторым состоянием
async def second_test_state_case_met(message: types.Message):
    await message.reply('Второй!', reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_3 | TestStates.TEST_STATE_4)#обработка 3/4
async def third_or_fourth_test_state_case_met(message: types.Message):
    await message.reply('Третий или четвертый!', reply=False)


@dp.message_handler(state=TestStates.all())#обработка хенддлера, который принимает все состояния
async def some_test_state_case_met(message: types.Message):
    with dp.current_state(user=message.from_user.id) as state:
        text = MESSAGES['current_state'].format(
            current_state=await state.get_state(),
            states=TestStates.all()
        )
    await message.reply(text, reply=False)


@dp.message_handler()
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, msg.text)

#закрываем соединение с хранилещем
async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=shutdown)
