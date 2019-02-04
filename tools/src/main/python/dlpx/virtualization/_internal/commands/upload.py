#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import logging

logger = logging.getLogger(__name__)


def upload(engine, user, plugin, build, password):
    """The implementation of upload"""
    logger.info('Engine: %s', engine)
    logger.info('User: %s', user)
    logger.info('Plugin: %s', plugin)
    logger.info('Build flag: %s', build)
    logger.info('Password: %s', password)
