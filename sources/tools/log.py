import datetime
import sys

class bcolors:
    DEBUG   = '\033[94m'
    INFO    = '\033[92m'
    WARNING = '\033[93m'
    ERROR   = '\033[91m'
    ENDC    = '\033[0m'

class Log():
    def __init__(self, name:str):
        self.name = name

    def __fmt(self, level, msg):
        d = datetime.datetime.now().isoformat()
        return d + " [" + level + "] [" + self.name + "]: " + msg

    def dbg(self, msg):
        print(bcolors.DEBUG + self.__fmt("DBG", msg), bcolors.ENDC)

    def inf(self, msg):
        print(bcolors.INFO + self.__fmt("INF", msg), bcolors.ENDC)

    def wrn(self, msg):
        print(bcolors.WARNING + self.__fmt("WRN", msg), bcolors.ENDC)

    def err(self, msg):
        print(bcolors.ERROR + self.__fmt("ERR", msg), bcolors.ENDC, file=sys.stderr)
