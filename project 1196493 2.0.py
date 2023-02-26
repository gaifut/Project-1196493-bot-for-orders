from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from private_infomration_1196494 import API_KEY
from private_infomration_1196494 import Google_sheets_API_details
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# connect to Google Sheets

sa = gspread.service_account(filename = Google_sheets_API_details)
sheet_connect = sa.open('Project 1196493')
# wks stands for worksheet
wks = sheet_connect.worksheet("1196493_inquiry_DB")

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name(Google_sheets_API_details, scope)
gc = gspread.authorize(credentials)


# making a class for a state to move from one state to another later and tie commands to a current state
class reg_state (StatesGroup):
    activity = State()
    full_name = State()
    phone = State()

# button names content
button1_text = 'Активность 1' 
button2_text = 'Активность 2'
button3_text = 'Активность 3' 
button4_text = 'Активность 4'
button5_text = 'Активность 5'
# buttons
button1 = InlineKeyboardButton (text = button1_text, callback_data='активность1')
button2 = InlineKeyboardButton (text = button2_text, callback_data='активность2')
button3 = InlineKeyboardButton (text = button3_text, callback_data='активность3')
button4 = InlineKeyboardButton (text = button4_text, callback_data='активность4')
button5 = InlineKeyboardButton (text = button5_text, callback_data='активность5')


#keyboard
keyboard_inline = InlineKeyboardMarkup().add(button1).add(button2).add(button3).add(button4).add(button5)

# answers
enter_your_name_details = 'Введите ваше ФИО'
enter_your_phone = "Введите ваш номер телефона без плюса"
user_greeting = "какой вид деятельности хотите заказать?"

bot = Bot(API_KEY)
storage = MemoryStorage()
dp = Dispatcher(bot, storage = storage)

async def startcommand_on_startup(dp):
    await bot.set_my_commands(types.BotCommand("start", "Start the bot"))

# job initiated, asking to choose activity
@dp.message_handler(commands=['start'])
async def activity_reg (message: types.Message):
    user_name_greeting = message.from_user.first_name
    await message.answer (text = f"{user_name_greeting}, {user_greeting}", reply_markup=keyboard_inline)

@dp.callback_query_handler(lambda call: call.data in ['активность1', 'активность2','активность3', 'активность4', 'активность5'])
async def inline_buttons_handler(call: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query_id=call.id)
    await state.update_data(activity=call.data)
    await call.message.answer (enter_your_name_details)
    await reg_state.full_name.set()



# grabbing the info about the user's name and asking for phone
@dp.message_handler(state=reg_state.full_name)
async def grab_full_name (message: types.Message, state: FSMContext):
    await state.update_data(full_name = message.text)
    await message.answer (enter_your_phone)
    await reg_state.phone.set()

# grabbing user's phone info and wrapping it up
@dp.message_handler (state = reg_state.phone)
async def grab_phone (message: types.Message, state: FSMContext):
    await state.update_data (phone = message.text)
    data_full = await state.get_data()
    await message.answer("Спасибо, заявка принята. Сохранены данные:\n"
                         f"Активность: {data_full['activity']}'\n"
                         f"ФИО: {data_full['full_name']}\n"
                         f"Номер телефона: {data_full['phone']}")
    await state.finish()

    print (data_full)
    wks.append_row([data_full['activity'], data_full['full_name'], data_full['phone']])

if __name__ == '__main__':
    executor.start_polling(dp)