# Welcome!

With this Delphix Virtualization SDK documentation we hope you will find all you need to know in order to develop your own plugins!

## Overview

If you already know about plugins, and are looking for something specific, use the links to the left to find what you are looking for or search.

If this is your first time here, and you are wondering what developing a Delphix plugin will do for you—read on!


## What Does a Delphix Plugin do?

The Delphix Engine is an appliance that lets you quickly and cheaply make **virtual copies** of large datasets. The engine has built-in support for interfacing with certain types of datasets, such as Oracle and SQL Server.

When you develop a plugin, you enable end users to use your dataset type as if they were using a built-in dataset type, whether it’s MongoDB, Cassandra, or something else. Your plugin will extend the Delphix Engine’s capabilities by teaching it how to run essential virtual data operations on your datasets:

 - How to stop and start them
 - Where to store their data
 - How to make virtual copies

These plugin operations are the building blocks of the Delphix Engine. From these building blocks, the engine can provide all of the normal Delphix functionality to the datasets you connect to such as:

 - Provisioning
 - Refreshing
 - Rewinding
 - Replication
 - Syncing


## Where to Start

Read through the first few sections of this documentation, and we will walk you through how to get setup for development, then how to develop, build, and deploy your first plugin.

[Getting Started](Getting_Started.md) will show you how to setup the SDK. When you finish this section, you will have a full plugin development environment, and you will be ready to start building.

[Building Your First Plugin](/Building_Your_First_Plugin/Overview.md) will walk you step-by-step through the process of developing a very simple plugin. With it, you will learn the concepts and techniques that you will need to develop fully-fledged plugins. That does not mean this first plugin is useless—you will be able to virtualize simple datasets with it.

Once you complete these sections, use the rest of the documentation whenever you would like. In addition to a full [reference section](/References/CLI.md), we include an example of a full-featured plugin that does complicated tasks (**Coming Soon!**).
