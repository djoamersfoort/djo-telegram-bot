#!/usr/bin/env python3
#

from telegram.error import (TelegramError, Unauthorized)
from telegram import ParseMode
from multiprocessing.dummy import Pool as ThreadPool
from threading import Thread as RunningThread
from util.datehandler import DateHandler
from util.feedhandler import FeedHandler
import threading
import traceback
from time import sleep


class BatchProcess(threading.Thread):

    def __init__(self, database, update_interval, bot):
        RunningThread.__init__(self)
        self.db = database
        self.update_interval = float(update_interval)
        self.bot = bot
        self.running = True

    def run(self):
        """
        Starts the BatchThreadPool
        """

        while self.running:
            # Init workload queue, add queue to ThreadPool
            url_queue = self.db.get_all_urls()
            self.parse_parallel(queue=url_queue, threads=4)

            # Sleep for interval
            sleep(self.update_interval)

    def parse_parallel(self, queue, threads):
        pool = ThreadPool(threads)
        pool.map(self.update_feed, queue)
        pool.close()
        pool.join()

    def update_feed(self, url):
        telegram_users = self.db.get_users_for_url(url=url[0])
        telegram_channels = self.db.get_channels_for_url(url=url[0])

        try:
            posts = FeedHandler.parse_feed(url[0])
        except ValueError:
            traceback.print_exc()
            return

        for post in posts:
            for user in telegram_users:
                if user[6]:  # is_active
                    self.send_newest_messages(url=url, post=post, user=user)
            for channel in telegram_channels:
                self.send_newest_messages(url=url, post=post, user=channel)

        self.db.update_url(url=url[0], last_updated=str(
            DateHandler.get_datetime_now()))

    def send_newest_messages(self, url, post, user):
        post_update_date = DateHandler.parse_datetime(datetime=post.updated)
        url_update_date = DateHandler.parse_datetime(datetime=url[1])

        if post_update_date > url_update_date:
            message = "Er is door {0} een nieuw artikel op de website geplaatst!\n" \
                      "<a href='{1}'>{2}</a>".format(post.author, post.link, post.title)
            print(message)
            try:
                self.bot.send_message(
                    chat_id=user[0], text=message, parse_mode=ParseMode.HTML)
            except Unauthorized:
                if not user[0].startswith('@'):
                    self.db.update_user(telegram_id=user[0], is_active=0)
            except TelegramError:
                # handle all other telegram related errors
                traceback.print_exc()
                pass

    def set_running(self, running):
        self.running = running
