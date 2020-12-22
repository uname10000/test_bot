from .shop_bot import bot
from telebot.apihelper import ApiException
from ..models.shop_models import User
import time
from threading import Thread

class Sender:
    def __init__(self, users, **message_data):
        self.message_data = message_data
        self._users = users

    def send_message(self):
        users = self._users.filter(is_block=True)
        blocked_ids = []
        for u in users:
            try:
                bot.send_message(
                    u.telegram_id,
                    **self.message_data
                )
            except ApiException as e:
                if e.error_code == 403:
                    blocked_ids.append(u.telegram_id)
                else:
                    raise e
            time.sleep(0.1)

        if not blocked_ids:
            blocked_ids = 0

        User.objects(telegram_id=blocked_ids).update(is_block=True)


def cron_unlock_users():
    while True:
        User.objects(is_block=True).update(is_block=False)
        minute = 60
        hour = 60 * minute
        day = 24 * hour
        time.sleep(2 * day)


# Thread(target=cron_unlock_users()).start()

