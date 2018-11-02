from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import logging
import sqlite3
from mail import send_mail
from sensitive import tok, user_id, name, username

TOKEN = tok


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TO, SUBJECT, MESSAGE = range(3)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.


def start(bot, update):
    """Send a message when the command /start is issued."""
    user = update.message.from_user
    send = f"{user.username} started your bot. \n First name {user.first_name} \n ID:{user.id}"
    bot.send_message(chat_id=user_id, text=send)
    update.message.reply_text('Hi!')


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('COMMANDS \n /view_events@eventattendbot \n /add_event@eventattendbot \n '
                              '/remove_event@eventattendbot \n')


def add_event(bot, update):
    message = update.message.text
    link = message.split()[1]
    user = update.message.from_user['username']

    with sqlite3.connect("events.db") as con:
        conn = con.cursor()
        # conn.execute('''CREATE TABLE EVENT
        #              (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        #              LINK           TEXT    NOT NULL);''')
        conn.execute("INSERT INTO EVENT (LINK) VALUES (?)", (link, ));
        con.commit()
    update.message.reply_text("@" + str(user) + ' Added An Event Link!')


def remove_event(bot, update):
    message = update.message.text
    link = message.split()[1]
    user = update.message.from_user['username']

    with sqlite3.connect("events.db") as con:
        conn = con.cursor()
        conn.execute("DELETE FROM EVENT WHERE LINK=?", (link,))
        con.commit()
    update.message.reply_text("@" + str(user) + ' Deleted An Event Link!')


def view_events(bot, update):
    with sqlite3.connect("events.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM EVENT ORDER BY ID DESC")
        all = cur.fetchall()
        links = " LINKS \n\n"
        for a in range(len(all)):
            link = all[a][1]
            links += str((a+1)) + ". " + str(link) + "\n\n"
        links += "\n\n"
        update.message.reply_text(links)


# def echo(bot, update):
#     """Echo the user message."""
#     update.message.reply_text("Hi!")


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def email(bot, update):
    id = update.message.from_user.id
    if id == user_id and update.message.from_user.first_name == name and update.message.from_user.username == username:
        update.message.reply_text("Give me an email address",
                                  reply_markup=ReplyKeyboardMarkup([['arushsharma91@gmail.com']],
                                                                   one_time_keyboard=True))
    return TO


def to(bot, update, user_data):
    user = update.message.from_user
    key = f"{user.id} to"
    value = update.message.text
    user_data[key] = value
    logger.info("email request by %s to %s", user.first_name, update.message.text)
    update.message.reply_text("Now, the Subject for the email", reply_markup=ReplyKeyboardRemove())
    return SUBJECT


def subject(bot, update, user_data):
    user = update.message.from_user
    key = f"{user.id} subject"
    value = update.message.text
    user_data[key] = value
    logger.info("email subject %s", update.message.text)
    update.message.reply_text("Now, the Body for the email")
    return MESSAGE


def body(bot, update, user_data):
    user = update.message.from_user

    logger.info("email body %s", update.message.text)

    email_to = user_data[f"{user.id} to"]
    email_subject = user_data[f"{user.id} subject"]
    send_mail(email_to, email_subject, update.message.text)

    del user_data[f"{user.id} to"]
    del user_data[f"{user.id} subject"]

    update.message.reply_text(f"email sent!")
    return ConversationHandler.END


def cancel(bot, update):
    update.message.reply_text('Canceled.')
    return ConversationHandler.END


def main():
    """Start the bot."""
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(CommandHandler("add_event", add_event))
    dp.add_handler(CommandHandler("view_events", view_events))
    dp.add_handler(CommandHandler("remove_event", remove_event))

    email_handler = ConversationHandler(
        entry_points=[CommandHandler('email', email)],
        states={
            TO: [MessageHandler(Filters.text, to, pass_user_data=True)],
            SUBJECT: [MessageHandler(Filters.text, subject, pass_user_data=True)],
            MESSAGE: [MessageHandler(Filters.text, body, pass_user_data=True)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(email_handler)

    # dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()