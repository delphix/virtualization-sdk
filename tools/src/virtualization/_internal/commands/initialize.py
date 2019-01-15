#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import logging

logger = logging.getLogger(__name__)


def init(type, root):
    """
    The implementation of init
    """
    logger.info('Type: %s', type)
    logger.info('Root: %s', root)
