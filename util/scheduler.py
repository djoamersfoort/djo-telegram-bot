import threading
import datetime
import requests
from time import sleep
from telegram import ParseMode
import traceback


class Scheduler(threading.Thread):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.running = True

    def run(self):
        while self.running:
            dt = datetime.datetime.now()
            if dt.hour == 21 and dt.minute % 5 == 0 and dt.weekday() == 4:
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
            message = f"Er zijn op vrijdag nog {slots['friday']} plekken vrij en op zaterdag nog {slots['saturday']}. Schrijf je snel in!"
            try:
                self.bot.send_message(chat_id='@Moes17', text=message)
            except Exception as e:
                traceback.print_exc()
                pass
