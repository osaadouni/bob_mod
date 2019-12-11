from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
import logging


logger = logging.getLogger(__name__)

#@receiver(user_logged_in)
def my_login_callback(sender, user, request, **kwargs):
    print(f"my_login_callback({sender}, {user}, {request}, {kwargs}")
    logger.info("{} logged in with {}".format(user.email, request))


user_logged_in.connect(my_login_callback)