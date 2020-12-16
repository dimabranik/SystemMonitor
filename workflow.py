import enum
import settings


class State(enum.Enum):
    MAIN_MENU = 'MAIN MENU'
    MONITORING = f'ACTIVE MONITORING (TOP {settings.NUMBER_OF_PROCESSES_TO_PRINT} PROCESSES BY CPU USAGE)'

    SEARCH = 'SEARCH PROCESS BY NAME'
    HISTORY = 'SHOW STATISTIC FOR TIME PERIOD'

    LIST_LEN = 'SHOW LEN OF DATA LIST'

    SHOW_DATA = 'SHOW LAST DATA'

    STOP = 'STOP SYSTEM MONITOR'

    def __str__(self):
        return f'<{self.value}>'


TRANSITIONS = {
    State.MAIN_MENU: {
        1: State.MONITORING,
        2: State.SEARCH,
        3: State.HISTORY,
        4: State.LIST_LEN,
        5: State.SHOW_DATA,
        90: State.STOP,
    },
    State.SEARCH: {
        1: State.MAIN_MENU,
        90: State.STOP,
    },
    State.HISTORY: {
        1: State.MAIN_MENU,
        90: State.STOP,
    },
    State.SHOW_DATA: {
        1: State.MAIN_MENU,
        90: State.STOP,
    },
    State.MONITORING: {
        1: State.MAIN_MENU,
        90: State.STOP,
    },
    State.LIST_LEN: {
        1: State.MAIN_MENU,
        90: State.STOP,

    },
    State.STOP: {
        90: State.STOP,
    }
}
