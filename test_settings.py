DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    },
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'legal',
)

AUTH_USER_MODEL = 'auth.User'
SECRET_KEY = 'abcde12345'
ROOT_URLCONF = 'test_urls'