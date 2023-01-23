from setuptools import setup, find_packages

setup(
    name='sourgrapes',
    version='0.8',
    description='A simple command-line interface for static site generation',
    author='Matt Zacharski',
    author_email='matthew.zacharski@gmail.com',
    url='https://github.com/zacharskim/python_ssg_cli',
    packages=find_packages(),
    install_requires=[
        'typer',
        'markdown2',
        'jinja2',
        'python-frontmatter',
        
    ],
    entry_points='''
        [console_scripts]
        grape-init=sourgrapes.cli:init
        grape-build=sourgrapes.cli:build
        grape-develop=sourgrapes.cli:develop
    ''',
)



