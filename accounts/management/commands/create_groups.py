"""
Create permission groups
Create permissions to models for a set of groups
"""
import logging

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User
from django.contrib.auth.models import Permission
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError


GROUPS = ['verbalisant', 'interceptie_desk']
MODELS = { 'resources': 'bobaanvraag'}
PERMISSIONS = ['view', 'add', 'change', 'delete']

GROUP_USERS = {
    'verbalisant': [
        'corrado', 'albert', 'omar', 'daan'
    ],
    'interceptie_desk': [
        'wouter', 'renate', 'admin'
    ]
}



class Command(BaseCommand):

    help = 'Creates read only default permissions for groups of users'

    def handle(self, *args, **options):
        for group in GROUPS:
            new_group , created = Group.objects.get_or_create(name=group)
            for app_label,model_name in MODELS.items():
                for permission in PERMISSIONS:
                    codename = 'can_{}_{}'.format(permission, model_name)
                    name = 'Can {} {}'.format(permission, model_name)
                    print("Creating {}".format(name))

                    try:
                        model_add_perm = Permission.objects.get(name=name)
                    except Permission.DoesNotExist:
                        logging.warning('Permission not found with name "{}".'.format(name))

                        model = apps.get_model(app_label, model_name)
                        ct = ContentType.objects.get_for_model(model)

                        model_add_perm = Permission.objects.create(codename=codename,
                                                                   name=name,
                                                                   content_type=ct)
                        logging.warning('Permission not found with name "{}".'.format(name))
                        #continue

                    new_group.permissions.add(model_add_perm)

        print("Created default group and permissions")

        for group_name, user_names in GROUP_USERS.items():
            group = Group.objects.get(name=group_name)

            for username in user_names:
                email = '{}@test.com'.format(username)
                password = 'testme123'
                self.get_or_create(username, email, password)

            users = [User.objects.get(username=un) for un in user_names]
            group.user_set.set(users)

    def get_or_create(self, username, email, password, *args, **kwargs):
        try:
            new_user = User.objects.create_user(username, email, password)
        except IntegrityError:
            return User.objects.get(username=username)
        else:
            pass
        return new_user