LOG_LEVEL: str = "INFO"
FORMAT: str = "%(levelprefix)s %(asctime)s | %(message)s"

logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'basic': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'format': FORMAT
        }
    },
    'handlers': {
        'console': {
            'level': LOG_LEVEL,
            'formatter': 'basic',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout'
        }
    },
    'loggers': {
        '': {
            'level': LOG_LEVEL,
            'handlers': ['console']
        }
    }
}
