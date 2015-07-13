"""
gmail-auto-label start

automatically generates labels for use in gmail,
based on either sender address, or recipient address (use with catch all addresses)

@category   Utility
@version    $ID: 1.1.1, 2015-07-01 17:00:00 CST $;
@author     KMR
@licence    GNU GPL v.3
"""

import logging

class logit:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    maxLvl = None
    handler = None

    levels = {
                'DEBUG': logging.DEBUG,
                'INFO': logging.INFO,
                'WARNING': logging.WARNING,
                'ERROR': logging.ERROR,
                'CRITICAL': logging.CRITICAL
             }

    def __init__(self, conf):
        self.maxLvl = conf['DEBUG']
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
        def wrapper(*args, **kwargs):
            if self.maxLvl == 'Caveman':
                print args[0]
            else:
                methodToCall = getattr(self.logger, name)
                methodToCall(args[0])

        return wrapper