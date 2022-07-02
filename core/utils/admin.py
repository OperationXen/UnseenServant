import re
import string
from asgiref.sync import sync_to_async

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.forms import ValidationError

from core.models.admin import DM
from core.utils.passwords import generate_random_password

@sync_to_async
def create_new_dm_from_discord_user(discord_user, name=None, description=None):
    new_dm_name = name or discord_user.name
    existing = DM.objects.filter(name=new_dm_name)
    if existing.exists():
        raise ValidationError('DM name already taken')

    new_dm_details = {
        'name': new_dm_name, 
        'discord_id': discord_user.id, 
        'discord_name': f"{discord_user.name}#{discord_user.discriminator}",
        'description': description
    }
    new_dm = DM.objects.create(**new_dm_details)
    return new_dm

def _allocate_limited_admin_permissions(user):
    """ Grant DM specific permissions """
    permissions = []
    permissions = permissions + list(Permission.objects.filter(codename__in=['add_player', 'view_player', 'change_player', 'delete_player']))
    permissions = permissions + list(Permission.objects.filter(codename__in=['add_game', 'view_game', 'change_game', 'delete_game']))
    permissions = permissions + list(Permission.objects.filter(codename__in=['add_dm', 'view_dm', 'change_dm', 'delete_dm']))
    permissions = permissions + list(Permission.objects.filter(codename__in=['add_character', 'view_character', 'change_character', 'delete_character']))
    
    user.user_permissions.add(*permissions)
    return user

def _create_new_limited_admin_user(username, password):
    """ Creates a new Admin user that can sign into the admin panel"""
    username = re.sub(f"[{string.punctuation}]", '', username)
    username = re.sub(f"[{string.whitespace}]", '-', username)
    new_user_details = {
        'username': username,
        'email': None,
        'password': password,
        'is_staff': True
    }
    return get_user_model().objects.create_user(**new_user_details)

@sync_to_async
def create_new_admin_user(username):
    """ Creates a new Admin user that can sign into the admin panel"""
    random_password = generate_random_password()
    new_admin_user = _create_new_limited_admin_user(username, random_password)
    _allocate_limited_admin_permissions(new_admin_user)

    return new_admin_user.username, random_password
