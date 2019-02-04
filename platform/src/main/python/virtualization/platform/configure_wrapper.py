#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import delphix_platform_pb2


def configure_wrapper(configure_input):
    config = configure(source=configure_input.source,
                                   repository=configure_input.repository,
                                   snapshot=configure_input.snapshot)
    configure_output = delphix_platform_pb2.ConfigureOutput()
    configure_output.sourceConfig.json = config.to_json()
    return configure_output

