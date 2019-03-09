from dlpx.virtualization.platform import plugin

plugin = plugin.Plugin()

#
# Below is an example of the repository discovery operation. This is
# the first operation that should be implemented.
#
# NOTE: The decorators come from the 'plugin' object defined above.
#
# Mark the function below as the operation that does repository discovery.
# @plugin.discovery.repository()
# def repository_discovery(source_connection):
#   # This is an object generated from the repositoryDefinition schema.
#   # In order to use it you must:
#   #   Run the 'compile' command provided by the SDK tools
#   #   Import it in the generated file like:
#   #      from generated.definitions import RepositoryDefinition
#   repo = RepositoryDefinition('repo')
#   return repo
#
