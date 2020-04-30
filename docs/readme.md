# Virtualization SDK Repository

This is the Markdown-based documentation for the Virtualization SDK.

## Live Testing and Reviews
The command `git docsdev-review` will handle publishing reviews, and putting your changes on a live docs server. For example, you can clone the `docsdev-server` image on DCOA, and then run `git docsdev-review -m <yourvm.dlpxdc.co>`. This will:

- Push your doc changes to your VM
- Give you a link to the docdev server so you can test your changes live in a browser
- Publish a review

## Workflow diagrams
We create workflow diagrams using a tool called `draw.io` which allows us to import/export diagrams in html format. If you want to add a diagram or edit an existing one, simply create or import the html file in `docs/References/html` into `draw.io` and make your desired changes. When you are done, select your diagram and export it as a png file. You can think of the html files as source code, and the png files as build artifacts. After this step, you will be prompted to crop what was selected. You'll want this box checked to trim the whitespace around the diagram. After the diagrams are exported, check in the updated html file to `docs/References/html` and png file to `docs/References/images`.