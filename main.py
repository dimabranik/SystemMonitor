from concurrent import futures
import logging.config

import settings
from manager import Manager
from collector import Collector

logging.config.dictConfig(settings.LOG_CONFIG)

logger = logging.getLogger()


def main():
    logger.debug('start of main')

    processes_set = set()
    data_list = list()

    is_running = [True]

    collector = Collector(is_running=is_running, processes_set=processes_set, data_list=data_list)
    manager = Manager(is_running=is_running, processes_set=processes_set, data_list=data_list)

    with futures.ThreadPoolExecutor(max_workers=settings.MAX_WORKERS) as executor:
        logger.debug('with thread pool')

        manager_future = executor.submit(manager.listen_user_input)
        collector_future = executor.submit(collector.collect)

        logger.debug('getting iterator for tasks')
        done_iter = futures.as_completed([manager_future, collector_future])

        logger.debug('waiting for tasks to complete:')
        for future in done_iter:
            logger.debug(f'{future}: {future.result()}')

    logger.debug('end of main')


if __name__ == '__main__':
    logger.debug('start of module')

    main()
    print('\n' + '#' * 36 + '\nAll processes exited. \n\nBye-bye.\n' + '#' * 36)
    logger.debug('end of module')
