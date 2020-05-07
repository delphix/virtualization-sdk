# Contributions and Reviews

This guide will help get you set up to author, edit, and review documentation within our gitlab repo.

----

- [Contributions and Reviews](#contributions-and-reviews)
	- [Roles & Tools](#roles-tools)
		- [Requirements for Authoring and Editing](#requirements-for-authoring-and-editing)
		- [Requirements for Reviewing](#requirements-for-reviewing)
	- [Guidelines](#guidelines)
		- [Authoring Guidelines](#authoring-guidelines)
		- [Reviewing Guidelines](#reviewing-guidelines)
	- [Publishing](#publishing)

----

## Roles & Tools

This section provides a brief overview of the main roles in the git authoring and publishing process.

**Authors and Editors**

* Create _markdown_ documentation content
* Commit new/edited documentation to _git_
* Submit a review with _reviewboard_
* Push reviews to _gitlab_

**Technical Reviewers**

* Review diffs in _reviewboard_
* Provide feedback and/or "ship it"

**Gatekeeper Reviewers**

* Review diffs in _reviewboard_
* View changes locally in _mkdocs_ using _reviewboard_ patches
* Provide feedback and/or "ship it"

### Requirements for Authoring and Editing

This documentation is written in Markdown. Markdown is an absurdly simple markup language for creating easy to read documents. [Here](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet) is a fairly popular cheat sheet for Markdown basics. You can also find many Markdown GUI tools or integrations. Atom, Sublime Text, and Eclipse all have built-in Markdown editing. Tools like MacDown for Mac may also help.

In order to create and edit documentation, you will need to be set up with the engineering git stack. Full instructions working with git can be found in the [Engineering Handbook](https://docs.delphix.com/display/EH/Setting+Up+Git).

The base requirements to make changes to this git repo are:

* [Install git-utils](https://docs.delphix.com/display/EH/Setting+Up+Git#SettingUpGit-Installgit-utils) (make sure you do this **outside** of your docsdev repo)
* Configure your PATH environment variable with [these instructions](https://gitlab.delphix.com/git/git-utils)
* Configure [git and reviewboard](https://docs.delphix.com/display/EH/Setting+Up+Git#SettingUpGit-ConfigureGit)
* Set up your local dev environment with instructions found [here](https://gitlab.delphix.com/docs/docsdev)

### Requirements for Reviewing

Technically, all you need to do a review is access to reviewboard. Since Markdown is easy to read in plain text, you can review changes by simply going to reviewboard and looking at the diff for any document you're assigned to review. Once done you can provide commentary and/or vote to ship it.

To provide a more thorough review or gatekeeper review, you should [set up your local dev environment](https://gitlab.delphix.com/docs/docsdev) so you can download the diff as a patch and check out the changes visually, or simply use the rbt patch command to sync your local repo up with a review. For example, assuming you already have a local docsdev environment and are reviewing reviewboard ID 99999:

1. cd ~/\<docsdev location\>
2. git checkout -B review-99999
3. rbt patch 99999

These commands created a new branch for your testing called "review-99999", then applied review 99999's changes to your local repo so you can view the changes in mkdocs.

## Guidelines

We have two goals: Provide the best documentation we can for our customers, and ensure that the publish process is smooth and intuitive every release. To that end, we have some guidelines for how to create, edit, and review content.

### Authoring Guidelines

1. Learn Markdown or use a really good IDE. It's easy to use, but there are complex topics like tables, admonishments, links, and images that you may need some practice with. Look at the other docs in the repo for inspiration and tutelage.
2. Test everything in mkdocs locally. Best practice is to always have mkdocs running in one terminal tab. It auto-refreshes when you make changes, so you can make sure that nothing breaks, and that your content looks good.
3. Do not create new directories (nav categories) in /docs without working with Jaspal Sumal (jaspal.sumal@delphix.com)
4. Place all screenshots in the local media/ directory of the category you're editing in. For example, if you're editing a page in docs/Getting_Started, put any screenshots you're going to use in docs/Getting_Started/media
5. Use relative links to reference screenshots (./media/image.png) and other pages (../Getting_Started/pagename/)
6. Beware the .pages file. .pages is a hidden file in every folder that provides page order. Any pages not listed in .pages will be alphabetically ordered _after_ the pages that have been listed. If you have a typo in this file or specify a renamed/deleted page, it will break mkdocs.
7. Always abide by Engineering requirements for branching, tagging, etc.
8. Provide verbose and descriptive commit messages.
9. Submit all changes for review and provide any necessary description on reviewboard when you publish it.
10. Assign one technical reviewer and one QA reviewer to any change in procedure/technical content. No technical/QA reviewers are necessary for typographical or non-contextual formatting changes.
11. Pushing requires technical signoff and gatekeeper signoff from the docs team.

### Reviewing Guidelines

1. The diff can usually provide what you need for reviewing changes. However, use mkdocs to review locally whenever possible to ensure good formatting and no breaks to mkdocs.
2. For minor corrections, leave a general comment on the review and vote to ship it so the author can fix it and push.
3. For major docs projects (e.g. whole new sections of docs or large batches of changes), coordinate with Jas. It is possible we'd be better off using another approach to review (e.g. track notes via Google Sheets)
4. If you're a reviewer that is not hooked into reviewboard, and unable to get set up to use it, work with Jas on an alternative approach (e.g. track notes via Google Sheets)
5. If there are issues in production docs, the current procedure is to post the issue in the #docs channel.

## Publishing

Publishing is currently a manual process that will be automated into the release process at a future point in time. The publishing workflow follows these steps:

1. After the git repo is frozen, Jas begins review and adjustments.
2. If there are technical questions or issues, Jas will take back to engineering for review.
3. The publish process will run. This process will:
  * Pull the appropriate branch to a build machine
  * Run "mkdocs build clean" to compile documentation to HTML
  * Push the documentation to the S3 bucket for Masking Docs

In the future, stage 3 of this process should be automated via a jenkins job and incorporated into the GA release process along with branching/tagging requirements like our app gate.
