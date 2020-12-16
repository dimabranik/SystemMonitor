import time
import traceback
import datetime
import logging.config
import threading
import queue

import settings
from workflow import State, TRANSITIONS
from printer import Printer

logging.config.dictConfig(settings.LOG_CONFIG)

logger = logging.getLogger()


class Manager:
    def __init__(self, is_running, processes_set, data_list):
        self._is_running = is_running

        self.processes_set = processes_set
        self.data_list = data_list

        self._current_state = [State.MAIN_MENU]

        self.printer = Printer(self._current_state)
        self.printer.main_menu()

        self.updater_thread_q = queue.Queue()

    @property
    def is_running(self):
        return self._is_running[0]

    @is_running.setter
    def is_running(self, value):
        self._is_running[0] = value

    @property
    def current_state(self):
        return self._current_state[0]

    @current_state.setter
    def current_state(self, value):
        self._current_state[0] = value

    def stop(self):
        self.is_running = False
        self.printer.stop()
        self.stop_updaters()

    def updater(self):
        t = threading.currentThread()
        while self.is_running and getattr(t, 'do_run', True):
            logger.debug('.')
            self.process_current_state()
            time.sleep(settings.UPDATER_SLEEP)
        print('Updater exited.')

    def list_len(self):
        self.printer.list_len(len(self.data_list))

    def sort_by_cpu(self, snapshot, reverse=True):
        logger.debug(f'reverse: {reverse}')
        list_to_sort = [snapshot[x] for x in snapshot]
        return sorted(list_to_sort, key=lambda x: x['cpu'], reverse=reverse)

    def start_updater(self):
        logger.debug('.')
        if self.updater_thread_q.empty():
            logger.debug('updater_thread_q is empty, starting new updater thread..')
            updater_thread = threading.Thread(target=self.updater)
            updater_thread.start()
            self.updater_thread_q.put(updater_thread)

    def stop_updaters(self):
        logger.debug('.')
        while not self.updater_thread_q.empty():
            logger.debug('got updater from updater_thread_q, stopping..')
            updater_thread = self.updater_thread_q.get()
            updater_thread.do_run = False
            updater_thread.join()

    def monitoring(self):
        logger.debug('.')
        self.printer.monitoring(self.sort_by_cpu(self.data_list[-1][1])[:settings.NUMBER_OF_PROCESSES_TO_PRINT])

    def show_data(self):
        logger.debug('.')
        self.printer.show_data(self.data_list[-1] if len(self.data_list) else '')

    def back_to_main_menu(self):
        logger.debug('.')
        self.stop_updaters()
        self.current_state = State.MAIN_MENU
        self.process_current_state()

    def search_processes_with_substr_in_name(self, substr):
        result_list = list()
        for p in self.processes_set:
            if substr in p.name.lower():
                result_list.append(p)
        return result_list

    def search(self):
        logger.debug('.')
        self.printer.search()

        searching = True

        while self.is_running and searching:
            user_input = input()

            try:
                command = int(user_input)
                next_state = TRANSITIONS[self.current_state][command]
                self.current_state = next_state
                self.process_current_state()
            except ValueError:
                logger.error(f'Error: {traceback.format_exc()}')

                if not user_input:
                    print('Please input non-empty string.\n>>>')
                    continue
                processes_list = self.search_processes_with_substr_in_name(user_input.lower())

                if not processes_list:
                    print(f'There is NO processes with {user_input!r} in process name. Try again.\n>>>')
                    continue

                searching = False

                print('\nHere is what was found:')
                for i in range(len(processes_list)):
                    print(f'{i} - {processes_list[i]}\n')

                print('Input corresponding index to select one of the processes and see detail info '
                      '(or anything else to return back to main menu)\n>>>')
                user_input = input()

                try:
                    index = int(user_input)
                    logger.debug(f'index={index!r}')
                    if -1 < index < len(processes_list):
                        logger.debug('index in a range')
                        selected_process = processes_list[index]
                        print(f'Detailed info for {selected_process}')

                        detailed_info_list = list()

                        for entry in self.data_list:
                            if selected_process in entry[1]:
                                detailed_info_list.append((entry[0], entry[1][selected_process]))

                        templ = '%5s %5s %10s\n\n'
                        print(' ' * 22 + templ % ('%CPU', '%MEM', 'CPU_TIME'))

                        for entry in detailed_info_list:
                            cpu_time = time.strftime('%M:%S', time.localtime(sum(entry[1]['cpu_time'])))

                            print(f'{entry[0].strftime("%Y-%m-%d %H:%M:%S")} : ' + templ % (
                                entry[1]['cpu'], round(entry[1]['mem'], 2), cpu_time))

                        print('Input anything to return back to main menu.\n>>>')
                        input()
                        self.back_to_main_menu()
                    else:
                        logger.debug('index is out of range')
                        self.back_to_main_menu()

                except Exception:
                    logger.error(f'Error: {traceback.format_exc()}')
                    self.back_to_main_menu()

    def history(self):
        logger.debug('.')
        self.printer.history()

        parsing_input = True

        while self.is_running and parsing_input:
            user_input = input()

            try:
                command = int(user_input)
                next_state = TRANSITIONS[self.current_state][command]
                self.current_state = next_state
                self.process_current_state()
            except ValueError:
                logger.error(f'Error: {traceback.format_exc()}')

                if not user_input:
                    print('Please input non-empty string.\n>>>')
                    continue

                try:
                    start_date_str, end_time_str = user_input.split('|')
                    start_datetime = datetime.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M')
                    end_datetime = datetime.datetime.strptime(end_time_str, '%Y-%m-%d %H:%M')

                except Exception:
                    logger.error(f'Error: {traceback.format_exc()}')
                    print('Something wrong with your input. Correct your input or choose one of Menu option:')
                    continue

                if start_datetime > end_datetime:
                    print('start datetime > end datetime. Correct your input or choose one of Menu option:')
                    continue

                if not (start_datetime < self.data_list[-1][0] and self.data_list[0][0] < end_datetime):
                    print(start_datetime)
                    print(self.data_list[-1][0])
                    print(end_datetime)
                    print(self.data_list[0][0])
                    print(start_datetime < self.data_list[-1][0])
                    print(self.data_list[0][0] < end_datetime)
                    print('The System Monitor does not have info for the chosen time period. '
                          'Correct your input or choose one of Menu option:')
                    continue

                parsing_input = False

                statistic = dict()

                def in_period(date_time):
                    return start_datetime <= date_time <= end_datetime

                def add_stats(snapshot):
                    for process in snapshot:

                        if not statistic.get(process):
                            statistic[process] = {
                                'pid': snapshot[process]['pid'],
                                'name': snapshot[process]['name'],
                                'username': snapshot[process]['username'],
                                'cpu': snapshot[process]['cpu'],
                                'mem': snapshot[process]['mem'],
                                'status': snapshot[process]['status'],
                                'create_time': snapshot[process]['create_time'],
                                'cpu_time': snapshot[process]['cpu_time'],
                                'cmdline': snapshot[process]['cmdline'],
                                'count': 1,
                            }
                        else:
                            statistic[process]['count'] += 1
                            statistic[process]['cpu'] += snapshot[process]['cpu']
                            statistic[process]['mem'] += snapshot[process]['mem']
                            statistic[process]['cpu_time'] = snapshot[process]['cpu_time']

                def finalize_stats():
                    for process in statistic:
                        statistic[process]['cpu'] /= statistic[process]['count']
                        statistic[process]['mem'] /= statistic[process]['count']

                def get_top_stats():
                    # Return top settings.NUMBER_OF_PROCESSES_TO_PRINT processes stats sorted by CPU.

                    processes_list = list()
                    for process in statistic:
                        processes_list.append((process, statistic[process]))

                    return sorted(processes_list,
                                  key=lambda process_list_entry: process_list_entry[1]['cpu'],
                                  reverse=True)[:settings.NUMBER_OF_PROCESSES_TO_PRINT]


                for snapshot_tuple in self.data_list:
                    if not in_period(snapshot_tuple[0]) and statistic:
                        # We have already got some info - that mean we already were in the period,
                        # and if we now not in the period - then we passed all the period and
                        # there is no reason to iterate.
                        break
                    elif in_period(snapshot_tuple[0]):
                        add_stats(snapshot_tuple[1])

                finalize_stats()

                top_stats = get_top_stats()

                templ = '%7s %-15s %15s %5s %5s\n'
                print(templ % ('pid', 'name', 'records_count', '%CPU(avg)', '%MEM(avg)') + '\n')

                for process_tuple in top_stats:
                    print(templ % (process_tuple[1]['pid'], process_tuple[1]['name'],
                                   process_tuple[1]['count'], round(process_tuple[1]['cpu'], 2),
                                   round(process_tuple[1]['mem'], 2)))

                print('Input anything to return back to main menu.\n>>>')
                input()
                self.back_to_main_menu()

    def process_current_state(self):
        logger.debug(f'current_state: {self.current_state}')

        if self.current_state == State.MAIN_MENU:
            self.printer.main_menu()

        elif self.current_state == State.MONITORING:
            self.start_updater()
            self.monitoring()

        elif self.current_state == State.SEARCH:
            self.search()

        elif self.current_state == State.HISTORY:
            self.history()

        elif self.current_state == State.SHOW_DATA:
            self.show_data()

        elif self.current_state == State.LIST_LEN:
            self.start_updater()
            self.list_len()

        elif self.current_state == State.STOP:
            self.stop()

        else:
            self.printer.print_screen(f'{self.current_state} is not ready yet.')

    def listen_user_input(self):
        while self.is_running:
            logger.debug('manager loop')

            try:
                user_input = input()
                logger.debug(f'user_input={user_input!r}')

                command = int(user_input)
                next_state = TRANSITIONS[self.current_state][command]

            except Exception:
                logger.error(f'Error: {traceback.format_exc()}')
                logger.debug(f'Unknown input: {user_input}')
                self.printer.print_screen(f'Unknown input: {user_input}. Try again.')

            else:
                try:
                    self.stop_updaters()
                    self.current_state = next_state
                    self.process_current_state()
                except Exception:
                    logger.error(f'Internal Error: {traceback.format_exc()}')
                    self.back_to_main_menu()

        print('Manager exited.')
