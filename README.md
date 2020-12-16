# System Monitor

The application uses psutil library to get information about processes and has Command Line Interface.


## How to run
```
pip install -r requirements.txt
sudo python main.py
```

## Files description

* [main.py](main.py) - create shared data variables and starts 2 threads for Manager and Collector

* [collector.py](collector.py) - Collector class which periodically get information for all running processes, compose it into proper data structure and add to the list with all data

* [manager.py](manager.py) - Manager class which listen and process user input (command line interface)

* [workflow.py](workflow.py) - State class and TRANSITIONS (defines available commands depends on current state)

* [printer.py](printer.py) - Printer class which is used by Manager for printing

* [screens.py](screens.py) - Contains some prepared strings for printing cli screens

* [process.py](process.py) - Named tupple containing info about Process

* [settings.py](settings.py) - Contains some system parameters (sleeps, print len, logger settings)




## Author

* **Dmitriy Branitskiy** - [dimabranik](https://github.com/dimabranik)


