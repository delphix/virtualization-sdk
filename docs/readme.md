# Virtualization SDK Repository

This is the Markdown-based documentation for the Virtualization SDK.

## Local Testing
Create a `virtualenv` using Python 3 and run `pipenv run mkdocs serve`

```
$ virtualenv -p /usr/local/bin/python3 .
Running virtualenv with interpreter /usr/local/bin/python3
Using base prefix '/usr/local/Cellar/python/3.7.2_1/Frameworks/Python.framework/Versions/3.7'
New python executable in /Users/asarin/Documents/repos/virt-sdk-docs/env/bin/python3.7
Also creating executable in /Users/asarin/Documents/repos/virt-sdk-docs/env/bin/python
Installing setuptools, pip, wheel...
done.

$ source bin/activate

$ pipenv run mkdocs serve
INFO    -  Building documentation... 
INFO    -  Cleaning site directory 
[I 200424 15:54:06 server:292] Serving on http://127.0.0.1:8000
[I 200424 15:54:06 handlers:59] Start watching changes
[I 200424 15:54:06 handlers:61] Start detecting changes
```

The docs would be served up at [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Live Testing and Reviews
The command `git docsdev-review` will handle publishing reviews, and putting your changes on a live docs server. For example, you can clone the `docsdev-server` image on DCOA, and then run `git docsdev-review -m <yourvm.dlpxdc.co>`. This will:

- Push your doc changes to your VM
- Give you a link to the docdev server so you can test your changes live in a browser
- Publish a review

## Workflow diagrams
We create workflow diagrams using a tool called `draw.io` which allows us to import/export diagrams in html format. If you want to add a diagram or edit an existing one, simply create or import the html file in `docs/References/html` into `draw.io` and make your desired changes. When you are done, select your diagram and export it as a png file. You can think of the html files as source code, and the png files as build artifacts. After this step, you will be prompted to crop what was selected. You'll want this box checked to trim the whitespace around the diagram. After the diagrams are exported, check in the updated html file to `docs/References/html` and png file to `docs/References/images`.
