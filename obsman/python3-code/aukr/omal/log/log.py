import logging
from ..args import args

# in case no --logfile was specified
try:
    logfile = args.logfile
except:
    logfile = ''

# Logs into console with given level
# if provided, logs into file with logging.DEBUG level
# use "logger.warning(), logger.info(), logger.debug()"
def getLogger(name, consoleLevel=args.verboselevel, logfile=logfile):
    '''returns logger with streams to console and a logfile(if provided)
    loglevel for logfile is logging.DEBUG
    :param consoleLevel: one of logging.[WARNING, INFO, DEBUG]
    :param logfile: path for logfile
    '''
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    # includes timestamp at beginning (for extensive debugging or timekeeping)
    #debugForm = logging.Formatter("%(asctime)s [%(filename)14s:%(lineno)3s %(funcName)14s] %(levelname)-7s %(message)s")
    debugForm = logging.Formatter("[%(filename)14s:%(lineno)3s %(funcName)14s] %(levelname)-7s %(message)s")

    # For logfile
    if logfile:  # default args.logfile is ''; (False)
        fileHand = logging.FileHandler(logfile)
        fileHand.setLevel(logging.DEBUG)
        fileHand.setFormatter(debugForm)
        #fileHand.setLevel(logging.DEBUG)
        logger.addHandler(fileHand)

    # For console output
    consoleHand = logging.StreamHandler()
    if consoleLevel == logging.DEBUG:    
        consoleHand.setFormatter(debugForm)
    else:
        consoleHand.setFormatter(logging.Formatter('%(message)s'))
    #logger.setLevel(consoleLevel)
    consoleHand.setLevel(consoleLevel)
    logger.addHandler(consoleHand)
    
    return logger

def banner(title, logger):
    logger.debug('')
    logger.debug(f' //{"%" * 54}\\\\ ')
    logger.debug(f'||{title.center(56, "-")}||')
    logger.debug(f' \\\\{"%" * 54}// ')

def heading1(title, logger):
    logger.debug('')
    logger.debug(f'##{title.center(56, "=")}##')

def heading2(title, logger):
    logger.debug(f'@{title.center(52, "~")}@'.center(60, ' '))

def heading3(title, logger):
    logger.debug(f'>{title.center(46, "-")}<'.center(60, ' '))
