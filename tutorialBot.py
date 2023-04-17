import logging

from telegram import Update, ForceReply, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from pymongo import MongoClient
import requests
import datetime;

logger = logging.getLogger(__name__)

#test

def store(func):
    def wrapper_store(*args, **kwargs):
        update = args[0]
        print(update.message.text)

        history = {
            'time' : str(datetime.datetime.now()),
            'message': update.message.text
        }

        global collection
        insert_id = collection.insert_one(history).inserted_id

        func(*args, **kwargs)

        save = collection.find_one({"_id": insert_id})
        print(save)

    return wrapper_store

@store
def echo(update: Update, context: CallbackContext) -> None:
    update.message.copy(update.message.chat_id)

@store
def visit(update: Update, context: CallbackContext) -> None:
    """
    This function would be added to the dispatcher as a handler for messages coming from the Bot API
    """

    # Print to console
    try:
        url = update.message.text.split("/visit")[1].strip()
        htmlReply = requests.get(url)

        context.bot.send_message(
            update.message.chat_id,
            htmlReply.text[:max(4096, len(htmlReply.text))],
            # To preserve the markdown, we attach entities (bold, italic...)
            entities=update.message.entities
        )
    except Exception as e:
        context.bot.send_message(
            update.message.chat_id,
            str(e),
            # To preserve the markdown, we attach entities (bold, italic...)
            entities=update.message.entities
        )

@store
def help(update: Update, context: CallbackContext)-> None:

    context.bot.send_message(
            update.message.chat_id,
            "Help!",
            # To preserve the markdown, we attach entities (bold, italic...)
            entities=update.message.entities
        )

def main() -> None:
    global mongodb_client, database, collection
    mongodb_client = MongoClient("mongodb://root:pw@54.196.132.215")
    database = mongodb_client["test"]
    collection = database['chat-history']
    # collection.drop()

    updater = Updater("6075707365:AAGkabhp1JEsCnYVOw305YABKUjyyK6vAuA")

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("visit", visit))
    dispatcher.add_handler(CommandHandler("help", help))

    dispatcher.add_handler(MessageHandler(~Filters.command, echo))
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()