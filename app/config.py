import logging


DB_NAME = "data.db"

LOGGER_CONFIG = {
    'version': 1,
    'formatters': {
        'default': {
            'format': "[%(asctime)s] [%(levelname)s] - %(name)s: %(message)s",
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'filename': 'app.log',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': logging.DEBUG,
    },
    'loggers': {
        'Api': {
            'handlers': ['file', 'console'],
            'level': logging.DEBUG,
        },
        'Tasks': {
            'handlers': ['file', 'console'],
            'level': logging.DEBUG,
        },
    },
}

CODE_CURRENCY = {
    840: "USD",
    933: "BYN",
    978: "EUR",
    1000: "BTC",
}

HTTP_TIMEOUT = 15

IP_LIST = ["127.0.0.1", "127.0.0.10"]
