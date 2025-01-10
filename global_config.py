# -*- coding: utf-8 -*-

import dutil
from orderedattrdict import AttrDict
import os
from os.path import expanduser
import json
import codecs
import traceback

# g_config = {}
# def loadConfig(json_file_path):
#     global g_config
#     if not os.path.exists(json_file_path):
#         dutil.logInfo(f'skip loading {json_file_path}')
#         return
#     with open(json_file_path, "r", encoding="utf-8") as file:
#         g_config = json.load(file)

g_config = AttrDict()

def loadConfig(filename):
    global g_config

    loaded = False
    try:
        home = ''
        if os.name == 'posix':
            home = os.environ['HOME']
        elif os.name == 'nt':
            home = expanduser("~").replace('\\', '/')
            home = home.replace('/Documents','/') #アプリによってはマイドキュメントを拾ってくるので強制変換

        custom_config = filename
        dutil.logDebug('config:' + custom_config)
        if os.path.exists(custom_config):
            with codecs.open(custom_config, 'r', 'utf-8') as f:
                json_dict = json.load(f)
                for k, v in json_dict.items():
                    g_config[k] = v
                    dutil.logDebug(f'load param : {str(k)}:{str(v)}')

                loaded = True
        else:
            dutil.logDebug('not exist ' + custom_config)
    except:
        dutil.logError('load config failed. : ' + traceback.format_exc())

    if loaded :
        dutil.logDebug('load custom config.')
    else :
        dutil.logDebug('skipp loading custom config.')