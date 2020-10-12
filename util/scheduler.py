import threading
import datetime
import requests
from time import sleep
import traceback
from telegram import ParseMode


class Scheduler(threading.Thread):

    def __init__(self, bot):
        threading.Thread.__init__(self)
        self.bot = bot

    def run(self):
        while True:
            try:
                dt = datetime.datetime.now()
                if dt.hour == 19 and dt.minute == 30 and dt.weekday() == 3:
                    self.send_free_member_slots()
                    sleep(60)
                sleep(30)
            except Exception as e:
                traceback.print_exc()
                pass

    def send_free_member_slots(self):
        response = requests.get('https://aanmelden.djoamersfoort.nl/api/v1/free')
        if not response.ok:
            print(response.content)
            return

        slots = response.json()
        message = ''
        link = '<a href="https://aanmelden.djoamersfoort.nl/">aan te melden</a>'
        if slots['friday'] > 0 and slots['saturday'] > 0:
            message = f"Er zijn op vrijdag nog {slots['friday']} plekken vrij en op zaterdag nog {slots['saturday']}. Vergeet je niet {link}!"
        elif slots['friday'] > 0:
            message = f"Er zijn op vrijdag nog {slots['friday']} plekken vrij. Vergeet je niet {link}!"
        elif slots['saturday'] > 0:
            message = f"Er zijn op zaterdag nog {slots['saturday']} plekken vrij. Vergeet je niet {link}!"

        if message != '':
            self.bot.send_message(chat_id='@DJOAmersfoort', text=message, parse_mode=ParseMode.HTML,
                                  disable_web_page_preview=True)
