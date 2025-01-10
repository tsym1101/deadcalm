# -*- coding: utf-8 -*-
#this is debug util modules***************

import inspect
import sys

#0=debug 1=info 2=warn 3=error 4=fatal
debug_level =1

import colorama
from colorama import Fore, Back, Style
colorama.init()

class pycolor:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    END = '\033[0m'
    BOLD = '\038[1m'
    UNDERLINE = '\033[4m'
    INVISIBLE = '\033[08m'
    REVERCE = '\033[07m'

# def location(depth=0):
#   frame = inspect.currentframe().f_back
#   # return str(os.path.basename(frame.f_code.co_filename)), 'func:' + str(frame.f_code.co_name), 'line:' + str(frame.f_lineno)
#   return str(frame.f_code.co_filename), 'line:' + str(frame.f_lineno)

def location(depth=1):  # デフォルトの深さを1に設定
    frame = inspect.currentframe()
    for _ in range(depth):
        if frame:
            frame = frame.f_back
    if frame:
        return str(frame.f_code.co_filename), 'line:' + str(frame.f_lineno)
    return 'Unknown', 'line:Unknown'

def logFatal(comment):
    if (debug_level < 5):
        print(Fore.MAGENTA + 'FATAL: ' + str(comment) + ' ' + str(location(2)) + Fore.RESET)

def logError(comment):
    if (debug_level < 4):
        print(Fore.RED + 'ERR  : ' + str(comment) + ' ' + str(location(2)) + Fore.RESET)

def logWarn(comment):
    if (debug_level < 3):
        print(Fore.YELLOW + 'WARN : ' + str(comment) + ' ' + str(location(2)) + Fore.RESET)

def logInfo(comment):
    if (debug_level < 2):
        print(Fore.GREEN + 'INFO : ' + str(comment) + ' ' + str(location(2)) + Fore.RESET)

def logDebug(comment):
    if (debug_level < 1):
        print(Fore.CYAN + 'DEBUG: ' + str(comment) + ' ' + str(location(2)) + Fore.RESET)

if __name__ == '__main__':
    debug_level = 0

    logError('hoge')
    logDebug('hoge')
    logWarn('hoge')
    logInfo('hoge')
    logFatal('hoge')
    exit(0)
