import telebot
from datetime import datetime, timedelta
from config import TOKEN, DB_NAME
from logic import DB_Manager

bot = telebot.TeleBot(TOKEN)


# Функция для добавления запрещённой ссылки
@bot.message_handler(commands=['addlink'])
def add_link(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    chat_member = bot.get_chat_member(message.chat.id, user_id)
    if chat_member.status in ['creator', 'administrator']:
        link = message.text.split()[1]
        manager.add_link(chat_id, link)
        bot.reply_to(message, f"Ссылка {link} успешно добавлена в список запрещённых.")
    else:
        bot.reply_to(message, "У вас недостаточно прав.")

# Обработчик команды /checkwarns
@bot.message_handler(commands=['warns'])
def warns(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    warns_count = manager.get_warning_count(user_id, chat_id)
    bot.reply_to(message, f"У вас {warns_count} предупреждений.")

# Обработчик команды /getlinks
@bot.message_handler(commands=['getlinks'])
def get_links(message):
    chat_id = message.chat.id
    links = manager.get_blocked_links(chat_id)
    if links:
        bot.reply_to(message, "Запрещённые ссылки:\n" + "\n".join(links))
    else:
        bot.reply_to(message, "Запрещённых ссылок нет.")

# Функция для удаления запрещённой ссылки
@bot.message_handler(commands=['dellink'])
def del_link(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    chat_member = bot.get_chat_member(message.chat.id, user_id)
    if chat_member.status in ['creator', 'administrator']:
        link = message.text.split()[1]
        result = manager.del_link(chat_id, link)
        if result:
            bot.reply_to(message, f"Ссылка {link} успешно удалена из списка запрещённых.")
        else:
            bot.reply_to(message, f"Ссыдкт {link} нет в базе данных.")
    else:
        bot.reply_to(message, "У вас недостаточно прав.")

# Хендлер для проверки всех сообщений
@bot.message_handler(func=lambda message: True)
def check_message(message):
    print("Обработчик вызван")
    if message.entities:
        print("Есть сущности")
        for entity in message.entities:
            print(f"Тип сущности: {entity.type}")
            if entity.type == 'url':
                print("Обнаружена ссылка")
                url = message.text[entity.offset:entity.offset + entity.length]
                chat_id = message.chat.id
                user_id = message.from_user.id
                if manager.check_link_in_db(chat_id, url):
                    print("Ссылка найдена в базе данных")
                    warnings = manager.add_warning(user_id, chat_id)
                    if warnings < 3:
                        bot.reply_to(message, f"@{message.from_user.username}, это запрещённая ссылка. У вас {warnings}/3 варнов.\nПри достижении 3-х вы получите бан на 30 дней.")
                    else:
                        now = datetime.now()
                        until_date = now + timedelta(days=30)
                        bot.ban_chat_member(message.chat.id, message.from_user.id, until_date)
                        bot.reply_to(message, f"@{message.from_user.username}, это запрещённая ссылка. У вас {warnings}/3 варнов.\nПри достижении 3-х вы получите бан на 30 дней.")
                        bot.send_message(message.chat.id, f"Пользователь {message.from_user.first_name} забанен за превышение количества варнов.")
                    bot.delete_message(message.chat.id, message.message_id)
                    break
    else:
        print("Сущностей нет в сообщении")

if __name__ == '__main__':
    manager = DB_Manager(DB_NAME)
    bot.infinity_polling()
