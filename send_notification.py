from shop.bot.sending_news import Sender
from shop.models.shop_models import User

s = Sender(User.objects(), text='рассылка')
s.send_message()