import json
import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters,
                          ConversationHandler)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

ENTRY, ENTRY1, LOCATION, BYE= range(4)

class userdata(object):
    def __init__(self):
        self.dict = {
            'chatId' : {
                'drug_name' : None,
                'Dosage' : None,
                'longitude' : None,
                'latitude' : None
                }
        }


    def setUser(self, user):
        self.dict['chatId'] = user
        return 0

    def set_drugName(self, major):
        self.dict['drug_name'] = major
        return 0
    def setdosage(self, dosage):
        self.dict['Dosage'] = dosage
        return 0
    def set_longitude(self, year):
        self.dict['longitude'] = year
        return 0

    def set_latitude(self, fileId):
        self.dict['latitude'] = fileId
        return 0

userdata = userdata()

def start(update, context):
    update.message.reply_text('please enter the name of the drug')
    userdata.setUser(update.message.chat.id)

    return ENTRY

def entry(update, context):
    user = update.message.from_user
    chatId = update.message.chat.id

    userdata.dict(chatId).drug_name = update.message.text

    logger.info('%s entered %s for drugs ', user.first_name, update.message.text)
    update.message.reply_text('Now Enter the dosage:---')
    return ENTRY1



def entry1(update, context):
    user = update.message.from_user
    chatId = update.message.chat.id
    userdata.dict(chatId).Dosage = update.message.text
    logger.info('%s entered %s for dosage ', user.first_name, update.message.text)
    update.message.reply_text('please send your location')
    return LOCATION

def location(update, context):
        bot = context.bot
        chatId = update.message.chat.id
        keyboard = [
            [InlineKeyboardButton("Available", callback_data= '1'),
             InlineKeyboardButton("Unavailable", callback_data= '2')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        user = update.message.from_user
        user_location = update.message.location
        logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,
                    user_location.longitude)
        userdata.set_latitude(user_location.latitude)
        userdata.set_longitude(user_location.longitude)
        update.message.reply_text('Thank you for using our bot '
                                  'we will get back to you as soon as we can', reply_markup = ReplyKeyboardRemove())
        with open('drugusers.json', 'a') as f:
            json.dump(userdata.dict, f, indent =2)

        bot.send_message(chat_id = '@trial13', text = 'user : ' +user.first_name +'\nDrug Requested : ' + userdata.dict(chatId).drug_name +'\n Dosage : '
                    + userdata.dict(chatId).dosage,
                reply_markup = reply_markup)


        return ConversationHandler.END

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
        updater = Updater("1135978630:AAFTaXp1A33RrCxkfOpBsixZ7LxPp8FxYb4", use_context=True)
        dp = updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points = [CommandHandler('start', start)],
            states = {
                ENTRY : [MessageHandler(Filters.all, entry)],
                ENTRY1 : [MessageHandler(Filters.all, entry1)],
                LOCATION : [MessageHandler(Filters.location, location)]
            },

            fallbacks = [CommandHandler('cancel',cancel)]
        )


        dp.add_handler(conv_handler)
        dp.add_error_handler(error)

        updater.start_polling()
        updater.idle()
if __name__== '__main__':
    main()
