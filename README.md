# python_ssg_cli

Simple cli to generate a static site using python, [Jinja](https://jinja.palletsprojects.com/en/3.1.x/), and markdown files. [Typer](https://typer.tiangolo.com/) is also used. 

Here're the three commands to run while in the unboltedSoup directory:

```console
python3 -m unboltedSoup init
```

```console
python3 -m unboltedSoup build
```

```console
python3 -m unboltedSoup develop
```

The ```init``` command  creates a few directories: pages/, static/, and template/. These should be able to serve as the building blocks for a static site. 

Running build or develop creates a public/ directory which contains html files generated from the previously mentioned directories.
