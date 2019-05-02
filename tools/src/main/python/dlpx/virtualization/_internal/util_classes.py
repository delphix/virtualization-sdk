#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import enum


class ValidationMode(enum.Enum):
    """
    Defines the validation mode that validator uses.
    INFO - validator will give out info messages if validation fails.
    WARNING - validator will log a warning if validation fails.
    ERROR - validator will raise an exception if validation fails.
    """
    INFO = 1
    WARNING = 2
    ERROR = 3
