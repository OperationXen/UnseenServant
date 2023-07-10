from datetime import timedelta
from django.db.models import QuerySet, Q
from django.utils import timezone
from asgiref.sync import sync_to_async

from core.models import Credit, CustomUser


# ########################################################################## #
def get_user_credit_available(user: CustomUser) -> QuerySet:
    """Get the available, spendable credits for a user"""
    queryset = user.credits.filter(expired=False, active=False, locked=False)
    return queryset


@sync_to_async
def async_get_user_credit_available(user: CustomUser) -> list[Credit]:
    """async wrapper that gets a user's available credits"""
    queryset = get_user_credit_available(user)
    # Forcing to list collapses the lazy queryset down to a solved query
    return list(queryset)


# ########################################################################## #
def get_user_credit_active(user: CustomUser) -> QuerySet:
    """Get all of a user's current credit balance, including anything currently being used to hold a slot"""
    queryset = user.credits.filter(expired=False)
    return queryset


@sync_to_async
def async_get_user_credit_active(user: CustomUser) -> list[Credit]:
    """async wrapper to get a user's current credit balance"""
    queryset = get_user_credit_active(user)
    # Forcing to list collapses the lazy queryset down to a solved query before we leave syncronous context
    return list(queryset)
