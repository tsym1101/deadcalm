import os
from client.bastionwindow import run
from global_config import loadConfig

if __name__ == "__main__":
    loadConfig(f'{os.path.dirname(__file__)}/config.default.json')
    loadConfig(f'{os.path.dirname(__file__)}/config.json')
    run()