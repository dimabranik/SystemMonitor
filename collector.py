import time
import datetime
import traceback
import logging.config

import psutil

import settings
from process import Process

logging.config.dictConfig(settings.LOG_CONFIG)

logger = logging.getLogger()


class Collector:

    def __init__(self, is_running, processes_set, data_list):
        self._is_running = is_running
        self.processes_set = processes_set
        self.data_list = data_list

    @property
    def is_running(self):
        return self._is_running[0]

    @is_running.setter
    def is_running(self, value):
        self._is_running[0] = value

    def stop(self):
        self.is_running = False

    def make_snapshot(self):
        system_snapshot = dict()
        for process in psutil.process_iter():
            try:
                pk = Process(process.pid, process.name(), process.create_time())
                if pk not in self.processes_set:
                    self.processes_set.add(pk)

                process_data = dict()

                with process.oneshot():

                    process_data['pid'] = process.pid
                    process_data['name'] = process.name()
                    process_data['username'] = process.username()
                    process_data['cpu'] = process.cpu_percent()
                    process_data['mem'] = process.memory_percent()
                    process_data['status'] = process.status()
                    process_data['create_time'] = process.create_time()
                    process_data['cpu_time'] = process.cpu_times()

                    cmdline = process.cmdline()
                    if cmdline:
                        process_data['cmdline'] = ' '.join(cmdline)
                    else:
                        process_data['cmdline'] = ''

                system_snapshot[pk] = process_data
            except Exception as exc:
                logger.debug(f'Skipping an Error: {exc}')

        # Not utcnow() - because it's easy to use history command without counting timezones.
        return datetime.datetime.now(), system_snapshot

    def collect(self):
        while self.is_running:
            try:
                logger.debug('collector loop')
                snapshot_tuple = self.make_snapshot()
                self.data_list.append(snapshot_tuple)
                time.sleep(settings.COLLECTOR_SLEEP)
            except Exception:
                logger.error(f'Internal Error: {traceback.format_exc()}')

        print('Collector exited.')
