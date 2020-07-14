#
# Copyright (c) 2019 by Delphix. All rights reserved.
#
import dlpx.virtualization.api


def get_virtualization_api_version():
    """Returns the Virutalization API version string.

    :return: version string
    """
    return dlpx.virtualization.api.__version__
