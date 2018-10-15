from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import re
import sqlite3
from sensitive import tok


def find(string):
    # findall() has been used
    # with valid conditions for urls in string
    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+] | [! * \(\),] | (?: %[0-9a-fA-F][0-9a-fA-F]))+', string)[0]
    return url


#add token here
TOKEN = tok


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
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


def echo(bot, update):
    """Echo the user message."""
    reply = "Tu " + update.message.text + "!"
    update.message.reply_text(reply)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(CommandHandler("add_event", add_event))
    dp.add_handler(CommandHandler("view_events", view_events))
    dp.add_handler(CommandHandler("remove_event", remove_event))

    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()