import threading
import datetime
import requests
from time import sleep
import traceback


class Scheduler(threading.Thread):

    def __init__(self, bot):
        threading.Thread.__init__(self)
        self.bot = bot
        self.running = True

    def run(self):
        while self.running:
            dt = datetime.datetime.now()
            if dt.hour == 19 and dt.minute == 30 and dt.weekday() == 3:
                self.send_free_member_slots()
            sleep(60)

    def send_free_member_slots(self):
        try:
            response = requests.get('https://aanmelden.djoamersfoort.nl/api/v1/free')
        except Exception as e:
            traceback.print_exc()
            return

        if response.ok:
            slots = response.json()
            message = ''
            if slots['friday'] > 0 and slots['saturday'] > 0:
                message = f"Er zijn op vrijdag nog {slots['friday']} plekken vrij en op zaterdag nog {slots['saturday']}. Vergeet je niet aan te melden!"
            elif slots['friday'] > 0:
                message = f"Er zijn op vrijdag nog {slots['friday']} plekken vrij. Vergeet je niet aan te melden!"
            elif slots['saturday'] > 0:
                message = f"Er zijn op zaterdag nog {slots['saturday']} plekken vrij. Vergeet je niet aan te melden!"

            if message != '':
                try:
                    self.bot.send_message(chat_id='@DJOAmersfoort', text=message)
                except Exception as e:
                    traceback.print_exc()
                    pass
