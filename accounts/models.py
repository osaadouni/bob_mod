from django.contrib.auth.models import AbstractUser

from .groups import VERBALISANT_GROUPS, INTERCEPTIE_GROUPS

# Create your models here.
class User(AbstractUser):

    @property
    def is_idesk_member(self):
        return self.is_staff == True or self.groups.filter(name__in=INTERCEPTIE_GROUPS).exists()

    @property
    def is_verbalisant(self):
        return self.groups.filter(name__in=VERBALISANT_GROUPS).exists()
