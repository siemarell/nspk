import logging

def getMyLogger(name):
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-9.9s]  [%(name)-9.9s] [%(levelname)-5.5s]  %(message)s")
    logger = logging.getLogger(name)

    fileHandler = logging.FileHandler("{0}.log".format('log'))
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.INFO)
    return logger
