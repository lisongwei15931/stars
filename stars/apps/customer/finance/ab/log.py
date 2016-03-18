import logging
import os
from logging.handlers import TimedRotatingFileHandler

from stars.settings import BASE_DIR

ab_log = logging.getLogger('ab')
if len(ab_log.handlers) == 0:
    level = logging.DEBUG
    # filename='d:\\project\\source\\test1\\stars\\logs\\log.txt'
    filename = BASE_DIR+'/logs/fin/ab_log.txt'
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
    hdlr = TimedRotatingFileHandler(filename,"midnight",1)
    format = '%(asctime)s %(levelname)s %(module)s.%(funcName)s Line:%(lineno)d%(message)s'
    fmt = logging.Formatter(format)
    hdlr.setFormatter(fmt)

    ab_log.addHandler(hdlr)
    ab_log.setLevel(level)

    logging.Handler().flush()