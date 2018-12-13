# /bin/bash/python
# encoding: utf-8

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode
from util.filehandler import FileHandler
from util.database import DatabaseHandler
from util.processing import BatchProcess
from util.feedhandler import FeedHandler
from util.inventoryhandler import InventoryHandler


class RobotRss(object):

    def __init__(self, telegram_token, update_interval):

        # Initialize bot internals
        self.db = DatabaseHandler("resources/userdata/datastore.db")
        self.fh = FileHandler("..")
        self.inventory = InventoryHandler()

        # Register webhook to telegram bot
        self.updater = Updater(telegram_token)
        self.dispatcher = self.updater.dispatcher

        # Add Commands to bot
        self._addCommand(CommandHandler("start", self.start))
        self._addCommand(CommandHandler("stop", self.stop))
        self._addCommand(CommandHandler("help", self.help))
        self._addCommand(CommandHandler("list", self.list))
        self._addCommand(CommandHandler("about", self.about))
        self._addCommand(CommandHandler("add", self.add, pass_args=True))
        self._addCommand(CommandHandler("get", self.get, pass_args=True))
        self._addCommand(CommandHandler("remove", self.remove, pass_args=True))
        self._addCommand(CommandHandler("addgroup", self.add_group, pass_args=True))
        self._addCommand(CommandHandler("search", self.inventory_search, pass_args=True))
        self._addCommand(MessageHandler(Filters.text, self.vechten))
        self._addCommand(MessageHandler(Filters.command, self.unknown))

        # Start the Bot
        self.processing = BatchProcess(
            database=self.db, update_interval=update_interval, bot=self.dispatcher.bot)

        self.processing.start()
        self.updater.start_polling()
        self.updater.idle()

    def _addCommand(self, command):
        """
        Registers a new command to the bot
        """

        self.updater.dispatcher.add_handler(command)

    def start(self, bot, update):
        """
        Send a message when the command /start is issued.
        """

        telegram_user = update.message.from_user

        # Add new User if not exists
        if not self.db.get_user(telegram_id=telegram_user.id):
            message = "Hee, jou ken ik nog niet.. Ik stop je ff in mijn database, momentje."
            update.message.reply_text(message)

            self.db.add_user(telegram_id=telegram_user.id,
                             username=telegram_user.username,
                             firstname=telegram_user.first_name,
                             lastname=telegram_user.last_name,
                             language_code=telegram_user.language_code,
                             is_bot=telegram_user.is_bot,
                             is_active=1)

        self.db.update_user(telegram_id=telegram_user.id, is_active=1)

        message = "Je krijgt nu persoonlijk nieuws. Tik /help voor de commando's"
        update.message.reply_text(message)

    def add(self, bot, update, args):
        """
        Adds a rss subscription to user
        """

        telegram_user = update.message.from_user

        if len(args) != 2:
            message = "Ja, daar snap dus ik dus niks van. Probeer dit eens:\n" \
                      " /add <url> <naampje>"
            update.message.reply_text(message)
            return

        arg_url = FeedHandler.format_url_string(string=args[0])
        arg_entry = args[1]

        # Check if argument matches url format
        if not FeedHandler.is_parsable(url=arg_url):
            message = "Die url lijkt niet helemaal lekker!"
            update.message.reply_text(message)
            return

        # Check if entry does not exists
        entries = self.db.get_urls_for_user(telegram_id=telegram_user.id)

        if any(arg_url.lower() in entry for entry in entries):
            message = "Deze url heb je al toegevoegd!"
            update.message.reply_text(message)
            return

        if any(arg_entry in entry for entry in entries):
            message = "Je hebt hetzelfde naampje gebruikt als een andere url, da ga nie"
            update.message.reply_text(message)
            return

        self.db.add_user_bookmark(
            telegram_id=telegram_user.id, url=arg_url.lower(), alias=arg_entry)
        message = "Hij staat erbij! Gebruik /list als je me niet gelooft"
        update.message.reply_text(message)

    def get(self, bot, update, args):
        """
        Manually parses an rss feed
        """

        telegram_user = update.message.from_user

        if len(args) > 2:
            message = "To get the last news of your subscription please use /get <entryname> [optional: <count 1-10>]. Make sure you first add a feed using the /add command."
            update.message.reply_text(message)
            return

        if len(args) == 2:
            args_entry = args[0]
            args_count = int(args[1])
        else:
            args_entry = args[0]
            args_count = 4

        url = self.db.get_user_bookmark(
            telegram_id=telegram_user.id, alias=args_entry)

        if url is None:
            message = "I can not find an entry with label " + \
                      args_entry + " in your subscriptions! Please check your subscriptions using /list and use the delete command again!"
            update.message.reply_text(message)
            return

        entries = FeedHandler.parse_feed(url[0], args_count)
        for entry in entries:
            message = "[" + url[1] + "] <a href='" + \
                      entry.link + "'>" + entry.title + "</a>"
            print(message)

            try:
                update.message.reply_text(message, parse_mode=ParseMode.HTML)
            except Unauthorized:
                self.db.update_user(telegram_id=telegram_user.id, is_active=0)
            except TelegramError:
                # handle all other telegram related errors
                pass

    def remove(self, bot, update, args):
        """
        Removes an rss subscription from user
        """

        telegram_user = update.message.from_user

        if len(args) != 1:
            message = "To remove a subscriptions from your list please use /remove <entryname>. " \
                      "To see all your subscriptions along with their entry names use /list !"
            update.message.reply_text(message)
            return

        entry = self.db.get_user_bookmark(
            telegram_id=telegram_user.id, alias=args[0])

        if entry:
            self.db.remove_user_bookmark(
                telegram_id=telegram_user.id, url=entry[0])
            message = "I removed " + args[0] + " from your subscriptions!"
            update.message.reply_text(message)
        else:
            message = "I can not find an entry with label " + \
                      args[
                          0] + " in your subscriptions! Please check your subscriptions using /list and use the delete command again!"
            update.message.reply_text(message)

    def list(self, bot, update):
        """
        Displays a list of all user subscriptions
        """

        telegram_user = update.message.from_user

        message = "Hier is het lijstje met url's en groepen/users:"
        update.message.reply_text(message)

        # Group URL's
        entries = self.db.get_channels()
        for entry in entries:
            message = "[" + entry[0] + "]\n " + entry[1]
            update.message.reply_text(message)

        # User URL's
        entries = self.db.get_urls_for_user(telegram_id=telegram_user.id)
        for entry in entries:
            message = "[" + entry[1] + "]\n " + entry[0]
            update.message.reply_text(message)

    def help(self, bot, update):
        """
        Send a message when the command /help is issued.
        """

        message = "Ik snap de volgende commando's:\n" \
                  "/help: Deze helptekst\n" \
                  "/about: Info over deze bot\n" \
                  "/start: Zet het sturen van nieuwsupdates aan\n" \
                  "/stop: Stop met sturen van nieuwsupdates\n" \
                  "/list: Geef een lijst van feeds\n" \
                  "/add <url> <naam>: Voeg een nieuwe feed toe\n" \
                  "/addgroup <url> <@grouphandle>\n" \
                  "/search <keyword>: Zoek in de DJO inventaris"
        update.message.reply_text(message)

    def stop(self, bot, update):
        """
        Stops the bot from working
        """

        telegram_user = update.message.from_user
        self.db.update_user(telegram_id=telegram_user.id, is_active=0)

        message = "Jahaaa, ik stop al."
        update.message.reply_text(message)

    def about(self, bot, update):
        """
        Shows about information
        """

        message = "Dit is de officiele DJO Amersfoort Telegram Bot. Hier staat mijn source: " \
                  " <a href='https://github.com/djoamersfoort/djo-telegram-bot'>Github</a>."
        update.message.reply_text(message, parse_mode=ParseMode.HTML)

    def add_group(self, bot, update, args):
        if len(args) != 2:
            message = "Ja, daar snap ik dus helemaal niks van. Probeer dit eens:\n" \
                      "/addgroup <url> <groupame>"
            update.message.reply_text(message)
            return

        arg_url = FeedHandler.format_url_string(string=args[0])
        arg_channel = args[1]

        # Check if argument matches url format
        if not FeedHandler.is_parsable(url=arg_url):
            message = "Die url lijkt niet helemaal lekker!"
            update.message.reply_text(message)
            return

        if not arg_channel.startswith('@'):
            message = "Een groepnaam moet met @ starten"
            update.message.reply_text(message)
            return

        channels = self.db.get_channels()
        if any(channel[0] == arg_channel and channel[1] == arg_url for channel in channels):
                update.message.reply_text("Deze url is al aanwezig voor deze groep!")
                return

        # Add the channel + url
        self.db.add_url(arg_url)
        self.db.add_channel(arg_channel, arg_url)
        message = "Channel en url zijn toegevoegd!"
        update.message.reply_text(message)

    def inventory_search(self, bot, update, args):
        if len(args) != 1:
            update.message.reply_text('Waar wil je naar zoeken?')
            return

        keyword = args[0]
        (text, image) = self.inventory.search(keyword)
        update.message.reply_text(text, parse_mode=ParseMode.HTML)
        update.message.reply_photo(image, quote=False)

    def vechten(self, bot, update):
        if "kom vechten" in update.message.text.lower():
            print("Iemand wil vechten")
            update.message.reply_document('https://i.kym-cdn.com/photos/images/original/001/356/324/914.gif')

    def unknown(self, bot, update):
        message = "Computer says no"
        update.message.reply_text(message)


if __name__ == '__main__':
    # Load Credentials
    fh = FileHandler("..")
    credentials = fh.load_json("resources/credentials.json")

    # Pass Credentials to bot
    token = credentials["telegram_token"]
    update = credentials["update_interval"]
    RobotRss(telegram_token=token, update_interval=update)
