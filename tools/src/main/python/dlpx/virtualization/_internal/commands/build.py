#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import errno
import json
import logging
import os
import re

from dlpx.virtualization._internal import exceptions, package_util

logger = logging.getLogger(__name__)

ENGINE_API_VERSION = {
    'type': 'APIVersion',
    'major': 1,
    'minor': 11,
    'micro': 0
}

# A locale filename is "<locale>.txt", such as "en-us.txt" or "fr.txt"
LOCALE_REGEX = re.compile(r'^\w[\w-]*\.txt$')

# A message identifier must be a Python identifier.
# So, a letter optionally followed by letters/numerals/underscores.
IDENTIFIER_REGEX = re.compile(r'^[A-Za-z]\w*$')

# Upgrade scripts should be tagged with a major/minor version string
UPGRADE_VERSION_REGEX = re.compile(r'^([0-9]+)\\.([0-9]+)$')

# Swap files will end with either swp or swa.
# Also matches hidden files which are not swap files
SWAP_AND_HIDDEN_FILE_REGEX = re.compile(r'^\..*[\.sw[ap]]?')

# Directories under which we look for source code.
SOURCE_CODE_DIRS = ['direct', 'staged', 'virtual', 'discovery']


def build(root, outfile):
    """
    This builds the plugin from main.json and source code and generates
    plugin json file which will be used by upload command later.

    Input :

    root - Root directory of the build containing main.json and source code.
    outfile - The file to which output of build (plugin json) is written to.

    Output : None

    Raises :

    """
    logger.debug('root: %s', root)
    logger.debug('outfile: %s', outfile)

    # read manifest into JSON object to start off
    logger.info('Reading main.json')
    toolkit_dir = root
    manifest = None
    try:
        with open(os.path.join(toolkit_dir, 'main.json'), 'r') as f:
            try:
                manifest = json.load(f)
            except ValueError:
                raise exceptions.UserError('Build failed because main.json'
                                           ' was not a valid json file.')
    except IOError as err:
        raise exceptions.UserError('Unable to read main.json file from {}'
                                   ' Error code: {}. Error message: {}'.format(
                                       toolkit_dir, err.errno,
                                       errno.errorcode.get(
                                           err.errno, 'unknown err')))

    logger.info('Generating plugin json file at %s', outfile)

    # read resources
    logger.info('Reading resources ...')
    read_resources(manifest, toolkit_dir)

    # read workflow scripts from relevant directories into manifest JSON
    logger.info('Reading linked source definition')
    read_linked_source_definition(manifest, toolkit_dir)

    logger.info('Reading virtual source definition')
    read_virtual_source_definition(manifest, toolkit_dir)

    logger.info('Reading discovery definition')
    read_discovery_definition(manifest, toolkit_dir)

    logger.info('Reading upgrade definition')
    read_upgrade_definition(manifest, toolkit_dir)

    # read localizable messages info
    logger.info('Reading localizable messages')
    read_messages(manifest, toolkit_dir)

    logger.info('Reading snapshot schema')
    if 'snapshotSchema' not in manifest:
        raise exceptions.UserError('A toolkit must contain a snapshot schema')

    # set Engine API version
    manifest['engineApi'] = ENGINE_API_VERSION

    # set SDK version of build
    manifest['buildApi'] = get_build_api_version()

    # dump JSON into toolkit directory
    try:
        with open(outfile, 'w') as f:
            f.write(json.dumps(manifest, indent=4))
    except IOError as err:
        raise exceptions.UserError('Failed to write plugin json file to {}'
                                   ' Error code: {}. Error message: {}'.format(
                                       outfile, err.errno,
                                       errno.errorcode.get(
                                           err.errno, 'unknown err')))
    # exit with success
    logger.info('SUCCESS - Generated plugin json file at %s', outfile)
    return


def get_build_api_version():
    major, minor, micro = (int(n)
                           for n in package_util.get_version().split('.'))
    build_api_version = {
        'type': 'APIVersion',
        'major': major,
        'minor': minor,
        'micro': micro
    }
    return build_api_version


def read_resources(manifest, toolkit_dir):
    if 'resources' in manifest:
        raise exceptions.UserError("main.json must not contain resources.")
    manifest['resources'] = {}

    # iterate through resources directory
    rdir = os.path.join(toolkit_dir, 'resources')
    for dirpath, _, filenames in os.walk(rdir):
        for filename in filenames:
            abspath = os.path.join(dirpath, filename)
            rname = os.path.relpath(abspath, start=rdir)
            logger.info('  resources/{}'.format(rname))
            if SWAP_AND_HIDDEN_FILE_REGEX.match(rname):
                logger.info("Skipping swap/hidden file %s" % rname)
                continue
            try:
                with open(abspath, mode="r") as f:
                    try:
                        file_content = f.read()
                        file_content.decode('utf-8')
                        manifest["resources"][rname] = file_content
                    except UnicodeDecodeError:
                        raise exceptions.UserError(
                            'ERROR: Please check resources folder to ensure '
                            'that all files are UTF-8 text. '
                            'Please delete {} file in resources'
                            ' folder since it does not contain '
                            ' UTF-8 text'.format(abspath))
            except IOError as err:
                raise exceptions.UserError(
                    'Unable to read file {}'
                    ' Error code: {}. Error message: {}'.format(
                        abspath, err.errno,
                        errno.errorcode.get(err.errno, 'unknown err')))


def read_linked_source_definition(manifest, toolkit_dir):
    is_staged_toolkit = manifest['linkedSourceDefinition'][
        'type'] == 'ToolkitLinkedStagedSource'
    is_direct_toolkit = manifest['linkedSourceDefinition'][
        'type'] == 'ToolkitLinkedDirectSource'

    if not is_staged_toolkit and not is_direct_toolkit:
        raise exceptions.UserError('A plugin linked source definition'
                                   ' must be of type ToolkitLinkedStagedSource'
                                   ' or ToolkitLinkedDirectSource')

    # make sure appropriate directory exists (staged or linking)
    has_staged_dir = os.path.isdir(os.path.join(toolkit_dir, 'staged'))
    has_direct_dir = os.path.isdir(os.path.join(toolkit_dir, 'direct'))

    if has_staged_dir and has_direct_dir:
        raise exceptions.UserError(
            'A toolkit directory cannot contain both '
            'staged and direct directory.'
            ' The direct must match the toolkit LinkedSourceDefinition type')

    if is_staged_toolkit:
        if has_direct_dir:
            raise exceptions.UserError(
                'The toolkit LinkedSourceDefinition type '
                'ToolkitLinkedStagedSource requires a staged folder, '
                'not a direct folder')
        manifest['linkedSourceDefinition']['preSnapshot'] = read_script(
            toolkit_dir, 'staged/preSnapshot.py')
        manifest['linkedSourceDefinition']['postSnapshot'] = read_script(
            toolkit_dir, 'staged/postSnapshot.py', True, True)
        manifest['linkedSourceDefinition']['startStaging'] = read_script(
            toolkit_dir, 'staged/startStaging.py')
        manifest['linkedSourceDefinition']['status'] = read_script(
            toolkit_dir, 'staged/status.py')
        manifest['linkedSourceDefinition']['stopStaging'] = read_script(
            toolkit_dir, 'staged/stopStaging.py')
        manifest['linkedSourceDefinition']['resync'] = read_script(
            toolkit_dir, 'staged/resync.py')
        manifest['linkedSourceDefinition']['worker'] = read_script(
            toolkit_dir, 'staged/worker.py')
        if os.path.exists(os.path.join(toolkit_dir, 'staged/mountSpec.py')):
            mount_script = read_script(toolkit_dir, 'staged/mountSpec.py')
            manifest['linkedSourceDefinition']['mountSpec'] = mount_script
        if os.path.exists(
                os.path.join(toolkit_dir, 'staged/ownershipSpec.py')):
            owner_script = read_script(toolkit_dir, 'staged/ownershipSpec.py')
            manifest['linkedSourceDefinition']['ownershipSpec'] = owner_script

    elif is_direct_toolkit:
        if has_staged_dir:
            raise exceptions.UserError(
                'The toolkit LinkedSourceDefinition type '
                'ToolkitLinkedDirectSource requires a direct folder, '
                'not a staged folder')
        manifest['linkedSourceDefinition']['preSnapshot'] = read_script(
            toolkit_dir, 'direct/preSnapshot.py')
        manifest['linkedSourceDefinition']['postSnapshot'] = read_script(
            toolkit_dir, 'direct/postSnapshot.py', True, True)


def read_virtual_source_definition(manifest, toolkit_dir):
    manifest['virtualSourceDefinition']['configure'] = read_script(
        toolkit_dir, 'virtual/configure.py', True, True)
    manifest['virtualSourceDefinition']['unconfigure'] = read_script(
        toolkit_dir, 'virtual/unconfigure.py')
    manifest['virtualSourceDefinition']['reconfigure'] = read_script(
        toolkit_dir, 'virtual/reconfigure.py', True, True)
    manifest['virtualSourceDefinition']['start'] = read_script(
        toolkit_dir, 'virtual/start.py')
    manifest['virtualSourceDefinition']['stop'] = read_script(
        toolkit_dir, 'virtual/stop.py')
    manifest['virtualSourceDefinition']['preSnapshot'] = read_script(
        toolkit_dir, 'virtual/preSnapshot.py')
    manifest['virtualSourceDefinition']['postSnapshot'] = read_script(
        toolkit_dir, 'virtual/postSnapshot.py', True, True)
    manifest['virtualSourceDefinition']['status'] = read_script(
        toolkit_dir, 'virtual/status.py')

    # These Hook scripts are optional.
    # Only add to manifest if scripts actually exist.
    if os.path.exists(os.path.join(toolkit_dir, 'virtual/initialize.py')):
        init_script = read_script(toolkit_dir, 'virtual/initialize.py')
        manifest['virtualSourceDefinition']['initialize'] = init_script
    if os.path.exists(os.path.join(toolkit_dir, 'virtual/mountSpec.py')):
        mount_script = read_script(toolkit_dir, 'virtual/mountSpec.py')
        manifest['virtualSourceDefinition']['mountSpec'] = mount_script
    if os.path.exists(os.path.join(toolkit_dir, 'virtual/ownershipSpec.py')):
        owner_script = read_script(toolkit_dir, 'virtual/ownershipSpec.py')
        manifest['virtualSourceDefinition']['ownershipSpec'] = owner_script


def read_discovery_definition(manifest, toolkit_dir):
    repository_discovery = read_script(
        toolkit_dir, 'discovery/repositoryDiscovery.py', False)
    source_config_discovery = read_script(
        toolkit_dir, 'discovery/sourceConfigDiscovery.py', False)
    """
    A discoveryDefinition (in main.json) requires both a repositoryDiscovery
    and sourceConfigDiscovery to also exist. Without a discoveryDefinition,
    there should not be a repositoryDiscovery or a sourceConfigDiscovery.
    """
    if 'discoveryDefinition' in manifest:
        if not (repository_discovery and source_config_discovery):
            raise exceptions.UserError(
                'A toolkit supports discovery if it has a discoveryDefinition '
                'in its main.json. A discoveryDefinition was found and so '
                'there must exist a repositoryDiscovery.py and '
                'sourceConfigDiscovery.py script in the discovery folder.')
    else:
        if repository_discovery or source_config_discovery:
            raise exceptions.UserError(
                'A toolkit supports discovery if it has a discoveryDefinition '
                'in its main.json. A discoveryDefinition was not found and so '
                'there must not exist repositoryDiscovery.py '
                'and sourceConfigDiscovery.py script in the discovery folder.')
        # Exit without discovery definition
        return

    # Repository discovery
    if 'repositorySchema' not in manifest['discoveryDefinition']:
        raise exceptions.UserError(
            'A discovery definition must contain the field repositorySchema')
    if 'repositoryIdentityFields' not in manifest['discoveryDefinition']:
        raise exceptions.UserError(
            'A discovery definition must contain the field '
            'repositoryIdentityFields')
    if 'repositoryNameField' not in manifest['discoveryDefinition']:
        raise exceptions.UserError(
            'A discovery definition must contain the field repositoryNameField'
        )
    manifest['discoveryDefinition'][
        'repositoryDiscovery'] = repository_discovery

    # Source config discovery
    if 'sourceConfigSchema' not in manifest['discoveryDefinition']:
        raise exceptions.UserError(
            'A discovery definition must contain the field sourceConfigSchema')
    if 'sourceConfigIdentityFields' not in manifest['discoveryDefinition']:
        raise exceptions.UserError(
            'A discovery definition must contain the field '
            'sourceConfigIdentityFields')
    if 'sourceConfigNameField' not in manifest['discoveryDefinition']:
        raise exceptions.UserError(
            'A discovery definition must contain the field '
            'sourceConfigNameField')
    manifest['discoveryDefinition'][
        'sourceConfigDiscovery'] = source_config_discovery


def read_upgrade_definition(manifest, toolkit_dir):
    upgrade_dir = os.path.join(toolkit_dir, 'upgrade')
    if not os.path.isdir(upgrade_dir):
        return

    # Ensure that the upgrade directory only has a single directory,
    # the name will be the fromVersion
    from_version_dir = [
        sub_dir for sub_dir in os.listdir(upgrade_dir)
        if os.path.isdir(os.path.join(upgrade_dir, sub_dir))
    ]
    if len(from_version_dir) != 1:
        raise exceptions.UserError('The upgrade directory must contain'
                                   ' a single sub-directory which is the'
                                   ' fromVersion containing the required'
                                   ' upgrade scripts')

    version_dir = from_version_dir[0]
    snapshot_upgrade = read_script(
        toolkit_dir, 'upgrade/{}/upgradeSnapshot.py'.format(version_dir),
        False)
    virtual_source_upgrade = read_script(
        toolkit_dir, 'upgrade/{}/upgradeVirtualSource.py'.format(version_dir),
        False)
    linked_source_upgrade = read_script(
        toolkit_dir, 'upgrade/{}/upgradeLinkedSource.py'.format(version_dir),
        False)
    source_config_upgrade = read_script(
        toolkit_dir, 'upgrade/{}/upgradeSourceConfig.py'.format(version_dir),
        False)

    if not (snapshot_upgrade and virtual_source_upgrade
            and linked_source_upgrade):
        raise exceptions.UserError(
            'Upgrade requires all of the following scripts '
            'to be present and nonempty:'
            'upgradeSnapshot, upgradeVirtualSource, and upgradeLinkedSource')

    manifest['upgradeDefinition'] = {}
    manifest['upgradeDefinition']['type'] = 'ToolkitUpgradeDefinition'
    manifest['upgradeDefinition']['fromVersion'] = standardize_upgrade_version(
        version_dir)
    manifest['upgradeDefinition']['upgradeSnapshot'] = snapshot_upgrade
    manifest['upgradeDefinition'][
        'upgradeVirtualSource'] = virtual_source_upgrade
    manifest['upgradeDefinition']['upgradeLinkedSource'] = \
        linked_source_upgrade
    if source_config_upgrade:
        manifest['upgradeDefinition'][
            'upgradeManualSourceConfig'] = source_config_upgrade


def is_valid_upgrade_version(version):
    return bool(UPGRADE_VERSION_REGEX.match(version))


def standardize_upgrade_version(dir_name):
    if not is_valid_upgrade_version(dir_name):
        logger.error(
            'The upgrade sub-directory must be a minor/major version number.'
            ' For example 1.0')

    # We need to construct a valid full version string
    # from the major/minor version. Since the patch level is ignored,
    # we can pick any old patch identifier here.
    return dir_name + '.0'


def read_script(toolkit_dir,
                script,
                default_script=True,
                default_return_empty=False):
    script_path = os.path.join(toolkit_dir, script)
    if os.path.isfile(script_path):
        logger.info('  {} added'.format(script))
        try:
            with open(script_path) as f:
                return f.read()
        except IOError as err:
            raise exceptions.UserError(
                'Unable to read file {}'
                ' Error code: {}. Error message: {}'.format(
                    script_path, err.errno,
                    errno.errorcode.get(err.errno, 'unknown err')))
    else:
        message = '  {} does not exist'.format(script)
        if default_script:
            message += ', adding no-op script'
        logger.info(message)
        if default_return_empty:
            return 'return {}'
        else:
            return ''


def read_messages(manifest, toolkit_dir):
    """
    get the default (fallback) locale, which defines the absolute set of
    message_ids (this way, if we ever encounter a message_id not defined
    for the user's locale, we always have a locale to "fallback" to)
    """
    default_locale = read_default_locale(manifest)

    msg_dir = os.path.join(toolkit_dir, 'messages')
    has_msg_dir = os.path.isdir(msg_dir)
    has_msg_obj = 'messages' in manifest
    """
    The "messages" object can be explicitly included in the JSON manifest
    before the plugin is built, or generated from message files in
    a "messages" directory in the pre-built plugin.

    Below we check which case we fall into:
        - If neither the "messages" object or a "messages" directory exist,
          we log it telling the user they have included no messages.
          (This case is valid because messages are optional.)
        - If both a "messages" object and "message" directory exist,
          we log an error, as it is likely the plugin author made a mistake.
        - If only the "messages" object exist,
          we do nothing because no additional JSON needs to be generated.
        - If only the "messages" directory exists,
          we load the message files from this directory, validate them,
          and convert them to JSON.
    """
    if not (has_msg_dir or has_msg_obj):
        logger.info('No localizable messages found...')
        return
    elif has_msg_dir and has_msg_obj:
        logger.error('ERROR: Both a messages object in main.json'
                     ' and a messages directory were found')
        raise exceptions.UserError(
            'Place all your messages in the messages directory or '
            'in a messages object in main.json and build again.')
    elif has_msg_obj:
        logger.info('Using messages object in main.json '
                    'to define localizable messages.')
        return

    errors = []
    locales, message_ids = parse_message_files(msg_dir, errors)

    # make sure the default locale has a messages file
    if default_locale not in locales:
        raise exceptions.UserError(
            'ERROR: Default locale must have a message file')

    # ensure all message_ids are a subset of the default locale's set
    for msg_id in message_ids:
        if msg_id not in locales[default_locale].keys():
            errors.append(
                'message id {} is not defined for default locale {}'.format(
                    msg_id, default_locale))

    if len(errors) > 0:
        raise exceptions.UserError('ERROR: Message file validation failed.'
                                   ' Errors are : {}'.format(
                                       json.dumps(errors)))

    # add message info to json manifest
    messages_to_json(manifest, locales)


def parse_message_files(msg_dir, errors):
    """
     Loops through the input "messages" directory (msg_dir)
     and calls parse_message_file on each message file.

     Also checks if duplicate files exist for particular locales.

     Input:
        msg_dir: the absolute path to the "messages" directory in the toolkit
        errors: a list of errors found while parsing the message files.

     Output:
        locales: nested dictionary generated from the message files:
                    locale names -> (dictionary of message_ids -> messages)
        message_ids: the set of all message_ids found in the message files

    """
    locales = {}
    message_ids = set()

    for dir_path, _, file_names in os.walk(msg_dir):
        for filename in file_names:
            if is_locale_filename(filename):
                locale = get_locale_name(filename)
                if locale in locales:
                    errors.append(
                        'Duplicate locale message files for locale {} found. '.
                        format(locale))

                logger.info(
                    'Parsing message file for locale {}'.format(locale))
                abspath = os.path.join(dir_path, filename)
                locales[locale] = parse_message_file(abspath, errors)

                for key in locales[locale].keys():
                    message_ids.add(key)

    return locales, message_ids


def parse_message_file(abspath, errors):
    """
    Parses an individual message file, including:
        - ignoring empty lines and comments
        - recording an error for malformed lines (no "=" delimiter)
        - recording an error for duplicate message_id
        - recording an error for non-alphanumeric message_id

    Input:
        abspath: string representing the absolute path to the messages file
        errors: a list of error messages (strings) to report to the user

    Output:
        A string->string dictionary of message_id to messages in the file
    """
    try:
        with open(abspath) as f:
            contents = f.read()
    except IOError as err:
        raise exceptions.UserError('Unable to read file {}'
                                   ' Error code: {}. Error message: {}'.format(
                                       abspath, err.errno,
                                       errno.errorcode.get(
                                           err.errno, 'unknown err')))

    messages = {}

    for line_num, line in enumerate(contents.splitlines()):
        message_id, sep, msg = line.partition('=')
        message_id = message_id.rstrip()
        msg = msg.lstrip()

        if message_id == '' or message_id.startswith('#'):
            continue
        elif message_id == line:
            errors.append('Message file {} has malformed message definition'
                          '"{}" at line {}'.format(abspath, line, line_num))
        elif message_id in messages:
            errors.append('Message file {} has duplicate message id'
                          '{} at line {}'.format(abspath, message_id,
                                                 line_num))
        elif not IDENTIFIER_REGEX.match(message_id):
            errors.append('Message file {} has invalid message id'
                          '{} at line {}'.format(abspath, message_id,
                                                 line_num))
            errors.append('Messages must begin with a letter, and contain'
                          'only letters, numbers and underscores')

        messages[message_id] = msg

    return messages


def messages_to_json(manifest, locales):
    """
    Translate the locales nested map back to json.
    By mutating the "manifest" object here, the contents of the messages
    object will be escaped later in the script.

    Input:
        manifest: a dictionary representing the JSON manifest from main.json
        locales: A nested dictionary that maps a locale (string)
                to a dictionary of message_ids (string) to messages (string).

    Output: None.
    """
    manifest['messages'] = []
    for locale, message_map in locales.iteritems():
        obj = {'type': 'ToolkitLocale', 'localeName': locale, 'messages': {}}
        obj['messages'] = {
            msg_id: msg
            for (msg_id, msg) in message_map.iteritems()
        }
        manifest['messages'].append(obj)


def get_locale_name(filename):
    """
    Returns a locale name based on a file name.
    We may want to change how file names map to locales, so this logic
    is abstracted out separately (even if it is simple right now).
    """
    return filename.split('.')[0]


def is_locale_filename(filename):
    return bool(LOCALE_REGEX.match(filename))


def read_default_locale(manifest):
    if 'defaultLocale' not in manifest:
        raise exceptions.UserError(
            'ERROR: A toolkit must contain a defaultLocale property')
    return manifest['defaultLocale']
