import logging.config
import os

TIME_ZONE = 'Europe/Moscow'

urls = {
    'login': 'https://lk.sut.ru',
    'auth': 'https://lk.sut.ru/cabinet/lib/autentificationok.php',
    'schedule': 'https://cabs.itut.ru/cabinet/project/cabinet/forms/raspisanie.php',
    'start_class': 'https://lk.sut.ru/cabinet/project/cabinet/forms/raspisanie.php'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
}


# Logging config

logging_config = {
    'version': 1,
    'loggers': {
        '': {
            'level': logging.DEBUG,
            'handlers': ['console', 'fileDebug']
        }
    },
    'handlers': {
        'console': {
            'level': logging.WARNING,
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
        'fileDebug': {
            'level': logging.DEBUG,
            'class': 'concurrent_log_handler.ConcurrentRotatingFileHandler',
            'filename': os.path.join(os.path.abspath(os.getcwd()), 'logs', 'debug.log'),
            'maxBytes': 1024 * 1024,
            'backupCount': 1,
            'formatter': 'default'
        },
        'fileError': {
            'level': logging.ERROR,
            'class': 'concurrent_log_handler.ConcurrentRotatingFileHandler',
            'filename': os.path.join(os.path.abspath(os.getcwd()), 'logs', 'error.log'),
            'maxBytes': 1024 * 1024,
            'backupCount': 1,
            'formatter': 'default'
        }
    },
    'formatters': {
        'default': {
            'format': '{levelname} {asctime} {name}    {message}',
            'style': '{'
        }
    }
}

if not os.path.exists('logs'):
    os.makedirs('logs')

logging.config.dictConfig(logging_config)


# Celery config

CELERY_BROKER_URL = 'redis://localhost:6379'

CELERY_RESULT_BACKEND = 'redis://localhost:6379'
