"""
logit

A customer loging library that serves mostly as a thin wrapper for logging
allows customisation via config

@category   Utility
@version    $ID: 1.1.1, 2015-07-17 17:00:00 CST $;
@author     KMR
@licence    GNU GPL v.3
"""

import logging

class logit:
    """
    logit class, extends logging will the option to send all logging to the cli
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    max_lvl = None
    handler = None

    levels = {
                'DEBUG': logging.DEBUG,
                'INFO': logging.INFO,
                'WARNING': logging.WARNING,
                'ERROR': logging.ERROR,
                'CRITICAL': logging.CRITICAL
             }

    def __init__(self, conf):
        """ Initialise a new logit
        :param conf: the config object
        :return logit: a new instance of a logit
        """
        self.max_lvl = conf['DEBUG']
        if conf['DEBUG'] == 'Caveman':
            print 'Caveman debug selected, printing everything'
        else:
            # setup the handler
            handler = logging.FileHandler(conf['LOG_FILE'])

            # set the logging level
            handler.setLevel(self.levels[conf['DEBUG']])

            # create a logging format
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)

            # add the handlers to the logger
            self.logger.addHandler(handler)
            self.logger.info('Logit initialised')

    def __getattr__(self, name):
        """ Generalised function call, covers all methods
        :param name: the name of the function being called
        """
        def wrapper(*args, **kwargs):
            if self.max_lvl == 'Caveman':
                print args[0]
            else:
                method_to_call = getattr(self.logger, name)
                method_to_call(args[0])

        return wrapper