LOG_FORMAT = '%(asctime)s :: %(filename)s:%(lineno)d :: %(funcName)s ::: %(message)s'
LOG_CONFIG = {'version': 1,
              'formatters': {'error': {'format': LOG_FORMAT},
                             'debug': {'format': LOG_FORMAT},
                             'info': {'format': LOG_FORMAT},
                             'warning': {'format': LOG_FORMAT}, },
              'handlers': {'console': {'class': 'logging.StreamHandler',
                                       'formatter': 'debug',
                                       'level': 0},
                           'file': {'class': 'logging.FileHandler',
                                    'filename': './system_monitor.log',
                                    'formatter': 'info',
                                    'level': 0}},
              'root': {'handlers': ('file',), 'level': 'DEBUG'}}

# collector, manager
MAX_WORKERS = 2

COLLECTOR_SLEEP = 2
UPDATER_SLEEP = 2
NUMBER_OF_PROCESSES_TO_PRINT = 20
