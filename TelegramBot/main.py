import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Location
from time import sleep
import time
import argparse
from pmw3901 import PMW3901, BG_CS_FRONT_BCM, BG_CS_BACK_BCM


TOKEN = '966238705:AAHkaDLxGiJJAEstjgsgjMWrMEGJxGGudAk'

LUIS_KEY = 'ad5e38b352f8403aa811cc5faaeea113'
ENDPOINT = 'https://westeurope.api.cognitive.microsoft.com/luis/v2.0/apps/bc56f4a2-d7b7-460d-9e99-f73d1ab24889?verbose=true&timezoneOffset=0&q='

stop = False

is_cleaning = False


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")


def location(update, context):
    context.bot.send_location(chat_id=update.message.chat_id, latitude=32.1589224, longitude=34.8084406)


def battery(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="I'm feeling okay, my battery percentage is 50%")


def set_alarm(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text='No problem, alarm is set')


def start_dog(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text='You got it, I\'ll play with the dog when I see him')
    stop = False
    listen_motion(update, context)

def stop_dog(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text='As you wish, I\'ll leave your dog for now')
    stop = True

def start_work(update, context):
    global is_cleaning
    is_cleaning=True
    context.bot.send_message(chat_id=update.message.chat_id,
                             text='Doing my thing, amigo! The house will be clean in no time')
def stop_work(update, context):
    global is_cleaning
    is_cleaning = False
    context.bot.send_message(chat_id=update.message.chat_id,
                             text='OK, going to get a bit of rest now. Good night!')


def state(update, context):
    response = ""
    if is_cleaning:
        response = "I'm currently cleaning"
    else:
        response = "I'm currently resting"
    context.bot.send_message(chat_id=update.message.chat_id, text=response)


def temp(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="It's 25.4 degrees Celsius in here")


def joke(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="why was 6 afraid of 7?")
    context.bot.send_message(chat_id=update.message.chat_id, text="Because 7 8 9!")

# Parse the message and call the right command handler
def handle_text_message(update, context):
    intent = get_intent(update.message.text)
    # if (intent == "battery"):
    #     battery(update, context)
    # elif (intent == "joke"):
    #     joke(update, context)
    # elif (intent == "get lock"):
    #     islocked(update, context)
    # elif (intent == "lock"):
    #     lock(update, context)
    # elif (intent == "Turn off the lights"):
    #     turn_off_lights(update, context)
    # elif (intent == "Turn on the lights"):
    #     turn_on_lights(update, context)
    # elif (intent == "unlock"):
    #     unlock(update, context)
    # else:
    #     update.messae.reply_text("Sorry I didn't understand you")
    print(intent)
    if intent == 'location':
        location(update, context)
    elif intent == 'battery':
        battery(update, context)
    elif intent == 'set_alarm':
        set_alarm(update, context)
    elif intent == 'start_dog':
        start_dog(update, context)
    elif intent == 'stop_dog':
        stop_dog(update, context)
    elif intent == 'start_work':
        start_work(update, context)
    elif intent == 'stop_work':
        stop_work(update, context)
    elif intent == 'state':
        state(update, context)
    elif intent == 'joke':
        joke(update, context)
    elif intent == 'temp':
        temp(update, context)
    else:
        print("in else")
        update.message.reply_text("Sorry I didn't understand you")


# Send the receieved message to the LUIS application and get the top scoring intent
def get_intent(message):
    # Set up the request headers
    headers = {
        'Ocp-Apim-Subscription-Key': LUIS_KEY,
    }

    try:
        # Send the request to the Luis application endpoint
        r = requests.get(ENDPOINT + message, headers=headers)

        # Get the top scoring intent from the possible intents list

        return r.json()['topScoringIntent']['intent']
    except Exception:
        print("in exception")
        return None


def listen_motion(update, context):
    # put code here
    print("motion")
    
	

    parser = argparse.ArgumentParser()
    parser.add_argument('--rotation', type=int,
                    default=0, choices=[0, 90, 180, 270],
                    help='Rotation of sensor in degrees.')
    parser.add_argument('--spi-slot', type=str,
                    default='front', choices=['front', 'back'],
                    help='Breakout Garden SPI slot.')

    args = parser.parse_args()

    flo = PMW3901(spi_port=0, spi_cs=1, spi_cs_gpio=BG_CS_FRONT_BCM if args.spi_slot == 'front' else BG_CS_BACK_BCM)
    flo.set_rotation(args.rotation)

    tx = 0
    ty = 0
    s = False
    try:
        while not s:
            try:
                x, y = flo.get_motion()
            except RuntimeError:
                continue
            tx += x
            ty += y
            print("Relative: x {:03d} y {:03d} | Absolute: x {:03d} y {:03d}".format(x, y, tx, ty))
            if(x > 8):
                print("motion6")
                context.bot.send_message(chat_id=update.message.chat_id, text="Found dog!")
                s = True
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass




	    








def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler("location", location))
    dispatcher.add_handler(CommandHandler('battery', battery))
    dispatcher.add_handler(CommandHandler('set_alarm', set_alarm))
    dispatcher.add_handler(CommandHandler('start_dog', start_dog))
    dispatcher.add_handler(CommandHandler('stop_dog', stop_dog))
    dispatcher.add_handler(CommandHandler('start_work', start_work))
    dispatcher.add_handler(CommandHandler('stop_work', stop_work))
    dispatcher.add_handler(CommandHandler('state', state))
    dispatcher.add_handler(CommandHandler('temp', temp))
    dispatcher.add_handler(CommandHandler('joke', joke))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_text_message))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
