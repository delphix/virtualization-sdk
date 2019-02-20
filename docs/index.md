# Welcome!

Welcome to the Delphix Virtualization SDK doc page! Here, we hope you'll find all you need to know in order to develop your own plugins.

## Overview

Is this your first time here? Are you wondering what a plugin is, and why you'd want to develop one? Read on!

If you already know about plugins, and are looking for something specific, you can use the links to the left, or the search bar above, to find what you're looking for.


## What Is a Plugin For?

The Delphix Engine is an appliance that lets users quickly and cheaply make "virtual copies" of large datasets. The Delphix Engine has built-in support for interfacing with certain types of datasets (for example Oracle and SQL Server).

But what happens when you want to use a Delphix Engine with a dataset that does not have built-in support? That's where plugins come in.

A plugin extends the functionality of the Delphix Engine to add support for some particular kind of dataset. The plugin teaches the Delphix Engine how to do some operations on such datasets: How are they stopped and started? Where is there data stored? How can they be copied? Etc.

These plugin operations are used as building blocks by the Delphix Engine. From these building blocks, the engine can provide all of the normal Delphix functionality: provisioning, rewinding, replication, syncing, etc.

When you develop a plugin, you enable end users to use your dataset type just the same as if they were using a builtin dataset type.


## How to Get Started

We recommend that you read through the first few sections of this documentation. As you read, the docs will walk you through how to get setup for development, and how to develop, build, and deploy your first plugin.

First, follow the Getting Started With the SDK **TODO: link to this doc when it is done** documentation. When you finish with this, you will have a full plugin development environment, and you'll be ready to start development.

Second, follow the [Your First Plugin](/Your_First_Plugin) documentation. This is a step-by-step tutorial in which you will develop a very simple plugin. This first plugin is intended mainly as a way to learn the concepts and techniques you'll need to develop your own real plugins later. Nevertheless, this first plugin is not useless -- you will really be able to virtualize simple datasets with it.

Once you've completed these two sections, feel free to use the rest of the documentation however you feel. We have a full [reference section](/References), and a more detailed example of a more full-featured plugin that does more complicated work **TODO: link to this doc when it exists**.
