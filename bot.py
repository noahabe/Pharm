import os

import logging
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters, ConversationHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
PORT = int(os.environ.get('PORT', 5000))
TOKEN = '1135978630:AAFTaXp1A33RrCxkfOpBsixZ7LxPp8FxYb4'
logger = logging.getLogger(__name__)

FIRST, SECOND, PHARMDESCRIPTION, PHARMLOCATION, ENTRY1, ENTRY2, LOCATION = range(7)
class userdata(object):
    def __init__(self):
        self.dict = {
            "chat_id" : None,
            "drug_name" : None,
            "dosage" : None,
            "location" : {
                "longitude" : None,
                "latitude" : None
                }
        }


class pharmdata(object):
    def __init__(self):
        self.dict = {
            "chat_id" : None,
            "description" : None,
            "location" : {
                    "longitude" : None,
                    "latitude" : None,
            }
        }
def write_json(data, filename='drugusers.json'):
    with open(filename,'w') as f:
        json.dump(data, f, indent=4)
class methods():
    def __init__(self):
        pass
    def start(update, context):

        keyboard = [
            [InlineKeyboardButton("Pharmacist", callback_data= 'baby'),
             InlineKeyboardButton("Customer", callback_data= 'gaga')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Choose How You want to interact with the bot', reply_markup = reply_markup)
        return FIRST
    def acces(self, thing):
        self.x = thing
        return self.x
    def  check(self, drugname):
        f = open('druglist.json',"r")
        pdata = json.load(f)
        for i in pdata["Sheet1"]:
            if i["Descriptions of Medicnes "] == drugname:
                x = i["strength"]
                if x != None:
                    return True

    def vendorlocation(self, chatId):
        f = open('pharmacist.json',"r")
        pdata = json.load(f)
        for i in pdata["users"]:
            if i["chat_id"] == chatId:
                x = i["description"]
            return x





    def entry(update, context):
        logger.info('user has chosen customer ')
        query = update.callback_query
        #user = update.message.from_user
        chatId = query.message.chat.id
        query.edit_message_text(text="please Enter the name of the drug you wish to request")
        #query.message.reply_text('please Enter the name of the drug you wish to request')
        #update.reply_text('make sure you spell your query correctly, use google first if you have to')
        userdta = userdata()
        userdta.dict["chat_id"] = chatId
        methods.acces(userdta)
        return ENTRY1
    def entry1(update, context):
        user = update.message.from_user
        text = update.message.text
        if methods.check(text) == True:
            methods.x.dict["drug_name"] = update.message.text
            logger.info('%s entered %s for drug_name ', user.first_name, update.message.text)
            update.message.reply_text('please send the DOSAGE for the prescribed medicine')
            return ENTRY2
        else:
            update.message.reply_text('please recheck and re enter the name of the drug')
            return ENTRY1

    def entry2(update, context):
        user = update.message.from_user
        methods.x.dict["dosage"] = update.message.text
        logger.info('%s entered %s for dosage ', user.first_name, update.message.text)
        update.message.reply_text('Enter the gps location')
        return LOCATION
    def location(update, context):
            chatId = update.message.chat.id
            bot = context.bot
            callback = 'pm_' + str(chatId)
            keyboard = [
                [InlineKeyboardButton("Available", callback_data = str(callback)),
                InlineKeyboardButton("Flag as invalid request", callback_data = 'invalid')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            user = update.message.from_user
            user_location = update.message.location
            logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,
                        user_location.longitude)
            methods.x.dict["location"]["latitude"] = user_location.latitude
            methods.x.dict["location"]["longitude"] = user_location.longitude
            update.message.reply_text('Thank you for using our bot '
                                      'we will get back to you as soon as we can', reply_markup = ReplyKeyboardRemove())

            with open('drugusers.json') as json_file:
                data = json.load(json_file)
                temp = data["users"]
                temp.append(methods.x.dict)
            write_json(data)
            #methods.drugname = methods.x.["drug_name"]
            #with open('pending.json') as json_file:
            #    data = json.load(json_file)
            #    temp = data["users"]
            #    temp.append(methods.x.dict)
            #write_json(data, filename = 'pending.json')



            f = open('pharmacist.json', "r")
            pdata = json.load(f)
            for i in pdata["users"]:
                bot.send_message(chat_id = i["chat_id"], text = "Requested drug: " + methods.x.dict["drug_name"] + '\nDosage: '+ methods.x.dict["dosage"] ,reply_markup = reply_markup )



            return ConversationHandler.END

    def available(update, context):
        logger.info('got to here')
        query = update.callback_query
        chatId = query.message.chat.id
        user_id = update.callback_query.data.split("_")[1]
        location = methods.vendorlocation(chatId)
        bot = context.bot
        query.edit_message_text(text="Thankyou for replying to a customer query")
        bot.send_message(chat_id = user_id, text = "your query has been located at\n" + location)
        return ConversationHandler.END


    def pharmacist(update, context):
        #chatId  = update.message.chat.id
        logger.info('user just chose pharmacist')
        query = update.callback_query
        query.message.reply_text('If your a pharmacist and wish to get updates from customers please enter a description of your location')
        logger.info('user just chose pharmacist')
        pdata = pharmdata()
        pdata.dict["chat_id"] = query.message.chat.id
        methods.acces(pdata)

        return PHARMDESCRIPTION
    def typingdescription(update, context):
        update.message.reply_text("Thank you very much, the info you input will help customers find your pharmacy easily"
        "\nNow please send your location from within telegram by using the attachment option")
        methods.x.dict["description"] = update.message.text

        logger.info('user has sent location description')

        return PHARMLOCATION
    def pharmlocation(update,context):
        user_location = update.message.location
        update.message.reply_text('Thankyou for inputting your gps location.'
        '\nFrom now on you will get updates of requested drugs through this bot')
        methods.x.dict["location"]["longitude"] = user_location.longitude
        methods.x.dict["location"]["latitude"] = user_location.latitude
        update.message.reply_text('you can use /stop command to stop getting updates')
        logger.info('user has sent gps location')
        with open('pharmacist.json') as json_file:
            data = json.load(json_file)
            temp = data["users"]
            temp.append(methods.x.dict)
        write_json(data, filename = 'pharmacist.json')
        return STREAM

    def cancel(update, context):
        user = update.message.from_user
        update.message.reply_text('you cancelled so early',reply_markup = ReplyKeyboardRemove())
        return ConversationHandler.END

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    updater = Updater("1135978630:AAFTaXp1A33RrCxkfOpBsixZ7LxPp8FxYb4", use_context=True)
    dp = updater.dispatcher
#dp.add_handler(CommandHandler('re-enter', methods.entry))
    conv_handler = ConversationHandler(
        entry_points = [CommandHandler('start', methods.start)],

        states = {
            FIRST : [CallbackQueryHandler(methods.pharmacist, pattern = '^baby', ),
                CallbackQueryHandler(methods.entry, pattern = '^gaga', )],
            ENTRY1 : [MessageHandler(Filters.all, methods.entry1)],
            ENTRY2 : [MessageHandler(Filters.all, methods.entry2)],
            LOCATION : [MessageHandler(Filters.location, methods.location)],
            PHARMDESCRIPTION : [MessageHandler(Filters.all, methods.typingdescription)],
            PHARMLOCATION : [MessageHandler(Filters.location, methods.pharmlocation)]},
        fallbacks = [CommandHandler('cancel', methods.cancel)])
    updater.dispatcher.add_handler(CallbackQueryHandler(methods.available, pattern = '^pm_', ))


    dp.add_handler(conv_handler)
#updater.dispatcher.add_handler(CallbackQueryHandler(methods.available, pattern = '^pm_', ))
    dp.add_error_handler(error)
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://pharmabot3.herokuapp.com/' + TOKEN)
    updater.idle()
methods = methods()
if __name__ == '__main__':
    main()
