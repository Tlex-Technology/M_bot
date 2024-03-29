from telebot import TeleBot
from telebot.types import *
from config import group_id, token
from Keyboards import Keyboard
from Ahsql import SQL_Enter

bot = TeleBot(token)
sd = {"count":0,"pass":"0000"}

@bot.message_handler(commands=["start", "help", "go_main"])
def welcome(message: Message):
    if SQL_Enter.check_ban(message.chat.id):
        bot.send_message(message.chat.id, "You banned")
    else: 
        bot.send_message(message.chat.id, "Привет! Выбери следующие команды:", reply_markup = Keyboard.welcome_keyboard())


@bot.callback_query_handler(func=lambda call: call.data == "question") # Handler on button 'question'
def write(call: CallbackQuery):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    ans = bot.send_message(chat_id=call.message.chat.id, text= "Готов принять ваш вопрос)\nНапишите его")
    bot.register_next_step_handler(ans, post)


def post(message: Message):#
    if message.text is None or message.text.startswith('/'):
        bot.send_message(message.chat.id, "Спам и ложные сообщения не записываются в базу.", reply_markup = Keyboard.main_menu())
    else:
        bot.send_message(message.chat.id, "Спасибо за обращение)\nНажмите /go_main для перехода в главное меню", reply_markup = Keyboard.main_menu())
        SQL_Enter.post(message.chat.id, message.chat.username, message.text, message.date)



#admin_part
@bot.message_handler(commands=['admin'])
def admin_enter(message: Message):
    if SQL_Enter.exam_admin(message.chat.id):
        bot.send_message(message.chat.id, "Pass\nYou are in the admin panel\nYou can click on buttons in menu", reply_markup = Keyboard.admin_keyboard())
    else:
        ans = bot.send_message(message.chat.id, "Enter admin password", reply_markup = Keyboard.main_menu())
        bot.register_next_step_handler(ans, enter_pass)
            
            
def enter_pass(message: Message):# ok
    if SQL_Enter.enter_pass(message.chat.id, message.text):
        bot.send_message(message.chat.id, "Pass\nYou are in the admin panel\nYou can click on buttons in menu", reply_markup = Keyboard.admin_keyboard())
    else:
        bot.send_message(message.chat.id, "You enter incorrect password", reply_markup = Keyboard.main_menu())  

@bot.message_handler(commands=["all_commands"])
def read_messages(message: Message):
    if SQL_Enter.exam_admin(message.chat.id):
        bot.delete_message(chat_id=message.chat.id, message_id=message.id - 1)
        bot.delete_message(chat_id=message.chat.id, message_id=message.id - 2)
        bot.send_message(message.chat.id, "All admin commands:", reply_markup = Keyboard.admin_keyboard())
    else:
        bot.send_message(message.chat.id, "sorry, you are not the admin.", reply_markup = Keyboard.main_menu())


@bot.message_handler(commands=["settings", "back"])
def read_messages(message: Message):
    if SQL_Enter.exam_admin(message.chat.id):
        bot.send_message(message.chat.id, text = "To go to other admin commands click /all_commands\nOr click /go_main to go to main menu", reply_markup = Keyboard.all_commands()) 
        bot.send_message(message.chat.id, "Setting commands:", reply_markup = Keyboard.new_pass_settings_keyboard())
    else:
        bot.send_message(message.chat.id, "sorry, you are not the admin.", reply_markup = Keyboard.main_menu())

@bot.callback_query_handler(func=lambda call: call.data == "apass")
def passwd_button(call: CallbackQuery): #ok
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    ans = bot.send_message(chat_id=call.message.chat.id, text= f"Admin password = {SQL_Enter.passwd_button()}\nClick '/back' to go to settings\nClick '/go_main' to go to main menu", reply_markup = Keyboard.after_passwd_keyboard()) 

@bot.callback_query_handler(func=lambda call: call.data == "passwd")
def passwd_button(call: CallbackQuery): #ok
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    ans = bot.send_message(chat_id=call.message.chat.id, text= f"Real Password =  {SQL_Enter.passwd_button()}\nEnter new password", reply_markup = Keyboard.delete())
    bot.register_next_step_handler(ans, passwd_new)
    

def passwd_new(message : Message):
    bot.send_message(message.chat.id, text=f"New password = {message.text}\nConfirm password\nClick Yes or No", reply_markup = Keyboard.confirm_keyboard())
    sd["pass"] = message.text


@bot.message_handler(commands=["Yes"])#OK
def pass_yes(message: Message):
    if SQL_Enter.exam_admin(message.chat.id):
        bot.send_message(message.chat.id, text = f"Password was update\nPassword = {sd['pass']}\nnClick '/go_main' to go to main menu", reply_markup = Keyboard.main_menu())
        SQL_Enter.pass_yes(sd["pass"])
    else:
        bot.send_message(message.chat.id, "sorry, you are not the admin.", reply_markup = Keyboard.main_menu())
    

@bot.message_handler(commands=["No"])
def pass_no(message: Message):
    if SQL_Enter.exam_admin(message.chat.id):
        bot.send_message(message.chat.id, text = "Password wasn't update\nClick '/back' to go to settings\nClick '/go_main' to go to main menu", reply_markup = Keyboard.after_passwd_keyboard())
    else:
        bot.send_message(message.chat.id, "sorry, you are not the admin.", reply_markup = Keyboard.main_menu())

#tested function - unbanned function
@bot.message_handler(commands=["test"])
def read_messages(message: Message):
    if SQL_Enter.exam_admin(message.from_user.id):
        count = 0
        while True:
            try:
                out = SQL_Enter.r_b(count)
                bot.send_message(chat_id = message.chat.id, text = f"{out[0]} {out[1]}")
                count +=1
            except:
                if count == 0:
                    bot.send_message(message.from_user.id, "No messages.")
                break         
    else:
        bot.send_message(message.from_user.id, "sorry, you are not the admin.", reply_markup = Keyboard.main_menu())

@bot.message_handler(commands=["read_messages"])
def read_messages(message: Message):
    if SQL_Enter.exam_admin(message.chat.id):
        count = sd["count"] = 0
        if SQL_Enter.check_on_0():
            bot.send_message(message.chat.id, text = "Now no message", reply_markup = Keyboard.after_passwd_keyboard())
        else:
            out = SQL_Enter.read_messages(count)
            dk1 = bot.send_message(message.chat.id, text= f"'send' - sending to a group\n'del' - delete message\nTotal message : {out[4]}\nMessage left : {out[4] - count-1}" , reply_markup= Keyboard.bn())
            dk2 = bot.send_message(message.chat.id, text = f"№ {count}\nDate: {out[2]}\nUsername: {out[1]}\nid: {out[0]}\nText:\n{out[3]}", reply_markup=Keyboard.sd(count))
            sd["del"] = dk2
            sd["del_2"] = dk1
    else:
        bot.send_message(message.chat.id, "sorry, you are not the admin.", reply_markup = Keyboard.main_menu())


@bot.callback_query_handler(func=lambda call: call.data == "next")
def next_call(call: CallbackQuery):
    count = sd["count"]
    if count >= SQL_Enter.range_tab()-1:
        bot.answer_callback_query(call.id, text= f"RANGE!")
    else:
        count = count+1
        sd["count"] = count
        out = SQL_Enter.read_messages(count)
        dk1 = bot.edit_message_text(chat_id = call.from_user.id, message_id = sd["del_2"].message_id, text = f"'send' - sending to a group\n'del' - delete message\nTotal message : {out[4]}\nMessage left : {out[4] - count-1}" , reply_markup= Keyboard.bn())
        dk2 = bot.edit_message_text(chat_id=call.from_user.id, message_id = sd["del"].message_id, text = f"№ {count}\nDate: {out[2]}\nUsername: {out[1]}\nid: {out[0]}\nText:\n{out[3]}", reply_markup=Keyboard.sd(count))
        sd["del"] = dk2
        sd["del_2"] = dk1

           
@bot.callback_query_handler(func=lambda call: call.data == "pre")
def back_call(call: CallbackQuery):
    count = sd["count"]
    if count <= 0:
        bot.answer_callback_query(call.id, text= f"RANGE!")
    else:
        count = count-1
        sd["count"] = count
        out = SQL_Enter.read_messages(count)
        dk1 = bot.edit_message_text(chat_id = call.from_user.id, message_id = sd["del_2"].message_id, text = f"'send' - sending to a group\n'del' - delete message\nTotal message : {out[4]}\nMessage left : {out[4] - count-1}" , reply_markup= Keyboard.bn())
        dk2 = bot.edit_message_text(chat_id=call.from_user.id, message_id = sd["del"].message_id, text = f"№ {count}\nDate: {out[2]}\nUsername: {out[1]}\nid: {out[0]}\nText:\n{out[3]}", reply_markup=Keyboard.sd(count))
        sd["del"] = dk2
        sd["del_2"] = dk1


@bot.callback_query_handler(func=lambda call: call.data.startswith("add"))
def send_gr(call: CallbackQuery):
    sd["adc"] = int(call.data[3:])
    bot.answer_callback_query(call.id, text = "Please write your answer to this message.")
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, callback = send_in_group)


def send_in_group(call: CallbackQuery):
    count = sd["adc"]
    bot.send_message(chat_id = group_id, text = f"Вопрос:\n{SQL_Enter.send_to_chanel(count)}\n________\nОтвет:\n{call.text}")
    bot.delete_message(call.chat.id, call.id)

    if SQL_Enter.check_on_0():
        bot.delete_message(chat_id = call.chat.id, message_id= sd["del"].message_id)
        bot.delete_message(chat_id = call.chat.id, message_id= sd["del_2"].message_id)
        bot.send_message(call.chat.id, text = "Message ran out", reply_markup=Keyboard.after_passwd_keyboard())
    elif SQL_Enter.range_tab() == count:
        back_call(call)
    else:
        out = SQL_Enter.read_messages(count)
        sd["count"] = count
        td = sd["del"]
        dk1 = bot.edit_message_text(chat_id = call.chat.id, message_id = sd["del_2"].message_id, text = f"'send' - sending to a group\n'del' - delete message\nTotal message : {out[4]}\nMessage left : {out[4] - count-1}" , reply_markup= Keyboard.bn())
        dk2 = bot.edit_message_text(chat_id=call.chat.id, message_id = td.message_id, text = f"№ {count}\nDate: {out[2]}\nUsername: {out[1]}\nid: {out[0]}\nText:\n{out[3]}", reply_markup=Keyboard.sd(count))
        sd["del"] = dk2
        sd["del_2"] = dk1


@bot.callback_query_handler(func=lambda call: call.data.startswith("del"))
def del_call(call: CallbackQuery):
    count = int(call.data[3:])
    SQL_Enter.delete_message(count)
    bot.answer_callback_query(call.id, text = f"Successfull.")
    if SQL_Enter.check_on_0():
        bot.delete_message(chat_id = call.message.chat.id, message_id= sd["del"].message_id)
        bot.delete_message(chat_id = call.message.chat.id, message_id= sd["del_2"].message_id)
        bot.send_message(call.message.chat.id, text = "Message ran out", reply_markup=Keyboard.after_passwd_keyboard())
    elif SQL_Enter.range_tab() == count:
        back_call(call)
    else:
        out = SQL_Enter.read_messages(count)
        sd["count"] = count
        td = sd["del"]
        dk1 = bot.edit_message_text(chat_id = call.message.chat.id, message_id = sd["del_2"].message_id, text = f"'send' - sending to a group\n'del' - delete message\nTotal message : {out[4]}\nMessage left : {out[4] - count-1}" , reply_markup= Keyboard.bn())
        dk2 = bot.edit_message_text(chat_id=call.message.chat.id, message_id = td.message_id, text = f"№ {count}\nDate: {out[2]}\nUsername: {out[1]}\nid: {out[0]}\nText:\n{out[3]}", reply_markup=Keyboard.sd(count))
        sd["del"] = dk2
        sd["del_2"] = dk1


@bot.callback_query_handler(func=lambda call: call.data.startswith("ban"))
def del_call(call: CallbackQuery):
    if SQL_Enter.check_on_0():
        bot.send_message(call.message.chat.id, text="ERROR. NO MESSAGE!", reply_markup=Keyboard.after_passwd_keyboard())
    else:
        if SQL_Enter.ban_func(int(call.data[3:])):
            bot.answer_callback_query(call.id, text = f"This user was BANNED")
        else:
            bot.answer_callback_query(call.id, text = f"This user was UNBANNED")

bot.infinity_polling() 