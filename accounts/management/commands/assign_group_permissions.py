"""
Create permission groups
Create permissions to models for a set of groups
"""
import logging

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError

from accounts.models import User

MODELS = { 'resources': 'bobaanvraag'}

VERB_PERMISSIONS = [
    'aanmaken', 
    'aanpassen', 
    'verwijderen', 
    'indienen', 
]

IDESK_PERMISSIONS = [ 
    'aanmaken', 
    'aanpassen', 
    'verwijderen', 
        
    'indienen', 
    'behandelen', 
    'goedkeuren',
    'afkeuren',
    'verzenden_om',
    'goedkeuren_om',
    'afkeuren_om',
    'annuleren',
    'in_de_wacht_zetten',
]

GROUP_DICT = {
    'interceptie_desk': {
        'users': [     
                'wouter', 'renate', 'admin'
        ], 
        'permissions': IDESK_PERMISSIONS 
    }, 
    'verbalisant': {
        'users': [     
                'omar', 'isc65207', 'daan'
        ], 
        'permissions': VERB_PERMISSIONS 
    }
}



class Command(BaseCommand):

    help = 'Creates read only default permissions for groups of users'

    def handle(self, *args, **options):
        for group, data in GROUP_DICT.items():
            new_group , created = Group.objects.get_or_create(name=group)

            for app_label, model_name in MODELS.items():
                                    
                for permission in data['permissions']:
        
                    old_codename = 'can_{}_{}'.format(permission, model_name)
                    codename = 'can_{}'.format(permission)
                    name = 'Kan {} {}'.format(model_name, permission)
                    print("<< Deleting permission: {} -  {} / {}".format(name, codename, old_codename))

                    model = apps.get_model(app_label, model_name)
                    content_type = ContentType.objects.get_for_model(model)

                    Permission.objects.filter(content_type=content_type, codename__in=[codename, old_codename]).delete()

                    print(">> Creating permission: {} -  {}".format(codename, name))
                    new_perm = Permission.objects.create(codename=codename,
                                                               name=name,
                                                               content_type=content_type)
                    #continue

                    print(new_perm)
                    new_group.permissions.add(new_perm)

        print("Created default group and permissions")

        for group_name, data in GROUP_DICT.items():
            group , created = Group.objects.get_or_create(name=group_name)
            user_names = data['users']
        
            print(user_names)

            for username in user_names:
                print(f"Checking user: {username}")
                email = '{}@test.com'.format(username)
                password = 'testme123'
                user = self.get_or_create(username, email, password)

            users = [User.objects.get(username=un) for un in user_names]
            print(f"users: {users}")
            group.user_set.set(users)

    def get_or_create(self, username, email, password, *args, **kwargs):
        try:
            new_user = User.objects.create_user(username, email, password)
        except IntegrityError:
            return User.objects.get(username=username)
        else:
            pass
        return new_user
