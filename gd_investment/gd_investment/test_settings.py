from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'finance',
        'OPTIONS': {
            'options': '-c search_path=finance'
        },
        'USER': 'xxxx',
        'PASSWORD': 'xxxx',
        'HOST': 'localhost',
        'PORT': 5432
    },
}

TEST_RUNNER = 'gd_investment.test_runner.NoDbTestRunner'