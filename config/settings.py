from os import getenv
from dotenv import load_dotenv
from random import choices
from string import ascii_letters, digits
from pathlib import Path

load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

RANDOM_KEY = "".join(choices(ascii_letters + digits, k=128))
DJANGO_SECRET = getenv("DJANGO_SECRET")
SECRET_KEY = DJANGO_SECRET or RANDOM_KEY

if DJANGO_SECRET:
    DEBUG = False
    DEFAULT_CHANNEL_NAME = "general-game-signups"
    PRIORITY_CHANNEL_NAME = "patron-game-signups"
    CALENDAR_CHANNEL_NAME = "new-bot-testing-calendar"
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "None"
    SESSION_COOKIE_DOMAIN = ".tridengames.com"
    SERVER_URI = f"https://unseen-servant.tridengames.com"
    CSRF_TRUSTED_ORIGINS = ["https://*.tridengames.com"]
else:
    DEBUG = True
    DEFAULT_CHANNEL_NAME = "bot-test-channel"
    PRIORITY_CHANNEL_NAME = "bot-test-priority-channel"
    CALENDAR_CHANNEL_NAME = "bot-test-calendar-channel"
    SERVER_URI = "http://127.0.0.1:8000"
    CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1:3000", "http://localhost:3000"]

WEBAPP_URL = getenv("WEBAPP_URL", "http://127.0.0.1:3000")

# Security Controls
ALLOWED_HOSTS = ["127.0.0.1"]

# CORS_ALLOWED_ORIGINS = [WEBAPP_URL]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True

AUTH_USER_MODEL = "core.CustomUser"
AUTHENTICATION_BACKENDS = [
    "discord_login.auth.DiscordAuthenticationBackend",
    "core.auth.CustomUserModelBackend",
]

# Discord OAUTH config
DISCORD_CLIENT_ID = getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = getenv("DISCORD_CLIENT_SECRET")
AUTH_REDIRECT_URL = getenv("OAUTH_REDIRECT_URL", "")
AUTH_COMPLETE_URL = getenv("OAUTH_COMPLETE_URL", WEBAPP_URL + "/members")
AUTH_FAIL_URL = getenv("OAUTH_FAIL_URL", WEBAPP_URL + "/discord_auth/failed")

# Discord API config
DISCORD_TOKEN = getenv("DISCORD_TOKEN")
DISCORD_GUILDS = [getenv("DISCORD_GUILDS")]

# Unseen Servant Config
DISCORD_ADMIN_ROLES = ["Admin", "admin", "Master Code Wizard", "Moderator", "council"]
DISCORD_SIGNUP_ROLES = ["Signup Master"]
DISCORD_DM_ROLES = ["Dungeon Master"]

# Event role management configuration
EVENT_PLAYER_ROLE_NAME = "Event Participant"
EVENT_MANAGEMENT_ROLE_NAMES = ["Event DM", "Event Table Captain"]
DISCORD_EVENT_COORDINATOR_ROLES = ["Event Coordinator"]
DISCORD_EVENT_USER_ROLES = [EVENT_PLAYER_ROLE_NAME, *EVENT_MANAGEMENT_ROLE_NAMES]

CHANNEL_CREATION_DAYS = getenv("CHANNEL_CREATION_DAYS", 5)
CHANNEL_REMIND_HOURS = getenv("CHANNEL_REMIND_HOURS", 24)
CHANNEL_WARN_MINUTES = getenv("CHANNEL_WARN_MINUTES", 60)
CHANNEL_DESTROY_HOURS = getenv("CHANNEL_DESTROY_HOURS", 72)

CHANNEL_SEND_PINGS = getenv("CHANNEL_SEND_PINGS", False)

MOONSEACODEX_APIKEY = getenv("MOONSEACODEX_APIKEY")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "core",
    "api",
    "discord_bot",
    "discord_login",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "database" / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "admin_static/"
STATIC_ROOT = BASE_DIR / "admin_static"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
