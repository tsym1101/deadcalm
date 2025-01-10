# -*- coding: utf-8 -*-

import logging.handlers

if __name__ == "__main__":

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    trh = logging.handlers.TimedRotatingFileHandler(
        filename='tmp/test.log%(asctime)s',
        when='D',
        backupCount=30
    )

    logger.addHandler(trh)

    sh = logging.StreamHandler()
    logger.addHandler(sh)

    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s at line %(lineno)d in %(filename)s')
    trh.setFormatter(formatter)
    sh.setFormatter(formatter)

    logger.info(['info','test'])
    logger.warning('warning')