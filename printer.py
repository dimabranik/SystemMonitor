import os
import logging.config

import settings
import screens
from workflow import TRANSITIONS

logging.config.dictConfig(settings.LOG_CONFIG)

logger = logging.getLogger()


class Printer:

    def __init__(self, state):
        self._current_state = state

    @property
    def current_state(self):
        return self._current_state[0]

    def get_current_menu_string(self):
        return '\n'.join(
            str(x) + ': ' + str(TRANSITIONS[self.current_state][x]) for x in TRANSITIONS[self.current_state])

    def print_screen(self, sceen_content):
        logger.debug('.')
        os.system('clear')
        print(screens.HEADER.format(self.current_state, self.get_current_menu_string()) + str(
            sceen_content) + screens.FOOTER)

    def main_menu(self):
        logger.debug('.')
        self.print_screen(screens.MAIN_MENU)

    def list_len(self, list_len):
        logger.debug('.')
        self.print_screen(screens.LIST_LEN.format(list_len))

    def monitoring(self, cpu_sorted_processes_data):
        logger.debug('.')
        templ = '%-15s %7s %5s %5s %15s\n'
        result = templ % ('NAME', 'PID', '%CPU', '%MEM', 'cmdline') + '\n'

        for p in cpu_sorted_processes_data:
            result += templ % (p['name'][:15], p['pid'], p['cpu'], round(p['mem'], 2), p['cmdline'])
        self.print_screen(screens.MONITORING.format(result))

    def stop(self):
        logger.debug('.')
        print(screens.STOP)

    def show_data(self, data):
        self.print_screen(f'list: {data}')

    def search(self):
        self.print_screen(screens.SEARCH)

    def history(self):
        self.print_screen(screens.HISTORY)
