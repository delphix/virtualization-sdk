---
title: Virtualization SDK
---

# Discovery

## What is Discovery?
In order to ingest data from a source environment, the Delphix Engine first needs to learn information about that data: Where does it live? How can it be accessed? What is it called?

[Discovery](/References/Glossary/#discovery) is the process by which the Delphix Engine learns about remote data. Discovery can be either [automatic](/References/Glossary/#automatic-discovery) (where the plugin finds the remote data on its own), or [manual](/References/Glossary/#manual-discovery) (where the user tells us about the remote data). For our first plugin, we'll be using a mix of these two techniques.

## Source Configs and Repositories

### What are Source Configs and Repositories?
A [source config](/References/Glossary/#source-config) is a collection of information that Delphix uses to represent a dataset. Different plugins will have different ideas about what a "dataset" is (an entire database? a set of config files? an application?), but for our first plugin, it is simply a directory tree on the filesystem of the remote environment.

A [repository](/References/Glossary/#repository) represents what you might call "data dependencies" -- anything installed on the remote host that the dataset depends on. For example, if you're working with a Postgres database, then your repository will represent an installation of a particular version of the Postgres DBMS. In this plugin, we don't have any special dependencies, except for the simple existence of the unix system on which the directory lives.

### Defining Your Data Formats
Because each plugin will have different ideas about what a repository or source config represents, different plugins will have different sets of information that they will need to collect/store for each of these.

Delphix needs to know the format of this information. How many pieces of information are collected? What are they called? Are they strings? Numbers?

For our first plugin, we don't need a lot of information here, but see (link to advanced example) for a more complicated example. We use no special information about our repositories (except some way for the user to identify them). For source configs, we just need to know the path to the directory from which we will be ingesting data.

The plugin needs to describe all of this to the Delphix Engine, and it does it using [schemas](/References/Glossary/#schema).  To create the necessary schemas for our first plugin, (TODO: describe here where exactly these schemas go, when that is finalized… e.g. "create a new file called 'repositorySchema.json' and add the following content)

```json
{
  "type": "object",
  "properties": {
    "repoName": { "type": "string" }
  },
  "required": ["repoName"],
  "nameField": "repoName",
  "identityFields": ["repoName"]
}
```
(TODO: if possible, autogenerate this snippet from actual checked-in tested code instead of having it manually typed out here, so that we guarantee our doc code snippets never stop working)
(TODO: change this if we decide to keep the "name" and "identity" bits outside of the schema)

For detailed information about exactly how repository schemas works, see (link to reference). In essence, we are here defining only a single string property which will serve to uniquely identify the repository and will serve as a user-visible name.

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "prettyName": "Dataset Name",
      "description": "User-visible name for this dataset"
    }
    "path": {
      "type": "string",
      "format": "unixpath",
      "prettyName": "Path",
      "description": "Full path to data location on the remote environment"
    }
  },
  "required": ["name", "path"],
  "additionalFields": false,
  "nameField": "name",
  "identityFields": ["path"]
}
```

Because we are going to be asking the user to fill in these fields, we've added some extra information in our schemas. Our values for "prettyName" and "description" will be show to the user in the UI. In addition, we've used the "additionalFields" flag to stop the user from (accidentally?) providing extra information that we don't need. Finally, note that we're using the special `unixpath` format specifier, which will allow the UI to enforce that a valid Unix path is entered by the user.

Please see (link to reference) for full details about what you can do in these schemas.

## Implementing Discovery in Your Plugin

### About Python Code

As described in the overview section, plugins customize the behavior of the Delphix Engine by providing Python code. Each customizable piece of behavior is called a "plugin operation". The plugin provides separate Python functions for each of the operations that it wants to customize.

Right now, we're concerned with discovery. There are two customizable operations related to automatic discovery, one for repositories and one for source configs. In both cases, the job of the Python method is to automatically collect whatever information the schemas (see above) require, and to return that information to the Delphix Engine. The Delphix Engine will run these customized operations whenever a new environment is added, or when an existing environment is rediscovered.


### Repository Discovery
For repositories, we'll need to write a "repository discovery" operation in Python. The job of this operation is to examine a remote environment, find any repositories, and return information about them to the Delphix Engine.

In our case, we know that each remote environment is going to have exactly one repository, and so our "repository discovery" operation can be very simple.

Create a file in your preferred editor (TODO: add suggested/required filename), and add the following Python code. (TODO: revisit when decorators are finalized)

```python
@delphix.repository_discovery
def do_discovery_for_repositories(environment):
    the_repo = Repository()
    the_repo.name = "Directory Tree"

    return [ the_repo ]
```

!!! note "Gotcha"
    Be careful to always use consistent indentation in Python code!

Taking this line-by-line, here's what's happening in our new method:

```python
@delphix.repository_discovery
```
This is a Python [decorator](/References/Glossary/#decorator) which signals to the Delphix Engine that we want to customize the behavior of repository discovery, and that this function is the one that provides that customization

```python
def do_discovery_for_repositories(environment):
```

This begins a Python function definition. We can call this function whatever we like, but generally you'll want to pick something descriptive. As with most operations, the Delphix Engine will provide input to the repository discovery operation. In this particular case, the Engine provides one input which describes the remote environment which we are describing. For more details about operation inputs, see (link to reference).

```python
the_repo = Repository()
```
Here, we are constructing a new Python object which will conform to the repository schema we created in the previous section. This Python type `Repository` is automatically created for you based on that schema, and so this python object will have properties to correspond to the properties defined in that schema.

```python
the_repo.name = "Directory Tree"
```
Our repository only has one property: a user-visible name. Here we want to choose some name that will let the user understand what kind of data this repository can work with. We'll just call it "Directory Tree".

```python
return [ the_repo ]
```
The job of this operation is to return a list of all repositories on the remote environment. In our case, we want exactly one repository per environment. So, here we just make a one-item Python list, and return it to the Delphix Engine.

### Source Config Discovery

For source configs, we'll rely solely on manual discovery -- the user will tell us which directories they want to ingest from. Because we are not using automatic source config discovery, we will not need to write a custom operation here. But, see (link to advanced example) for a plugin that does define its own discovery operation for source configs,

To declare that we want to allow manual source config discovery, we just need to specify that in our manifest (link to manifest page). To do this,
(TODO: We have not finalized what the manifest/metadata/main.json will look like. When we do, add in details here about how to modify it to allow manual discovery)

When the user tries to add a new source config, the Delphix Engine will generate a UI based on the contents of your source config schema. Thus, the user will be able to enter all the data that your plugin needs.

## How to Run Discovery in the Delphix Engine

Let's try it out and make sure discovery works!

First, follow the instructions here (link to SDK doc) to build your plugin and install it onto a Delphix Engine.

Once the plugin is installed, add a remote unix environment to your engine. To do this, go to "Manage/Environments", click "add", answer the questions, and submit. (If you already have an environment set up, you can just refresh it).

To keep an eye on this discovery process, you may need to open the "operations" tab on the UI. If any errors happen, they'll be reported here.

(TODO: animated GIF here showing where to click on the UI?)

After the automatic discovery process completes, go to the "Databases" tab. You should see an entry for "Directory Tree". That's the repository you created in your Python code.

Because you've specified that manual discovery of source configs is allowed, you should be able to click the "Add Dataset" button next to "Directory Tree". This should bring up a UI which will allow you to enter all the pieces of information that your plugin has specified in the schema.

(TODO: animated GIF here showing manual discovery?)

!!! note "Gotcha"
    Once you've manually created a source config, you will not be allowed to modify your plugin's source config schema. We'll cover how to deal with this correctly later, in the upgrade section. For now, if you need to change your plugin's source config schema, you'll have to first delete any source configs you've manually added.
