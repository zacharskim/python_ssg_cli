
from typing import Optional
import http.server
import os
import shutil
import typer
import concurrent.futures 
from sourgrapes import __app_name__, __version__
import time
from markdown2 import markdown
from jinja2 import Environment, FileSystemLoader
import frontmatter
import threading
from http.server import ThreadingHTTPServer
import webbrowser
import re

tabOpen = False 

app = typer.Typer()

def _version_callback(value: bool) -> None:
    if value: 
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return
   

@app.command()
def init():
    """
    Initialize a sourgrape project in the current directory
    """
    for dirName in ["pages", "static", "template"]:
        makeDir(dirName)

    with open('pages/index.md', 'w') as f:
        f.write('---\ntemplate: homepage\ntitle: homepage\n---\n# Hello World\n Look at this!')
    
    with open('static/main.js', 'w') as f:
        f.write('console.log("Hello World :)")')
    
    with open('template/homepage.html', 'w') as f:
        f.write('<html><body><div>{{htmlPage}}</div><script type="text/javascript" src="public/main.js"></script></body></html>')


@app.command()
def build():
    """
    Build static html files and add them to a /public directory
    """
    makeDir("public")
    copyFiles("static", "public")
    processFiles("pages", "template")


def copyFiles(src: str, dest: str, htmlFiles: str=None) -> None:

    if not os.path.isdir(dest):
        shutil.copytree(src, dest)
    else:
        shutil.rmtree(dest)
        shutil.copytree(src, dest)



def processFiles(src: str, dest: str) -> list[str]:
    files = os.listdir(src)
    template_env = Environment(loader=FileSystemLoader(searchpath='template'))
    
    
    #loop over all files in ./pages, apply them to their respective templates...
    for f in files:
        if f.find(".md") > -1:
            with open("pages/"+f) as markdown_file:
                htmlPage = markdown(
                    #need to parse out the yaml stuff apprently bc frontmatter.load() returns a post object, not a string...
                    re.sub('---[^-]+---','',markdown_file.read()),
                    extras=['fenced-code-blocks', 'code-friendly'])


            yamlData = frontmatter.load("pages/"+f)    
            template = template_env.get_template(yamlData["title"] + '.html')
            
            with open(f'./public/{yamlData["title"]}.html', 'w') as output_file:
                output_file.write(
                    template.render(
                        htmlPage=htmlPage
                    )
                )
        else:
            raise Exception("Please make sure all files in the /pages directory end with .md")
    

@app.command()
def develop(): 
    """
    Start a local server that updates when changes are saved
    """
    build()
    s = MyServer()
    s.start()
    
    with concurrent.futures.ThreadPoolExecutor() as executor:   
        t = executor.submit(newWatcher)
        
        res = t.result()
    
        if res:
            s.stop()
            develop()
   
                

def newWatcher():
    fileNameArr, m_timeArr = generateFileNames()

    watcher = fileWatcher(fileNameArr, m_timeArr)
    while True:
        try: 
            res = watcher.check()
            time.sleep(0.5)
            if res: return True
        except KeyboardInterrupt:
            return False
        except:
            return False


def generateFileNames() -> tuple[list[str], list[int]]:
    filesPages, filesTemplates, filesStatic = os.listdir("pages"), os.listdir("template"), os.listdir("static")
    files, m_times = [], []

    for f in filesPages:
        file = "pages/" + f
        files.append(file)
        m_times.append(os.stat(file).st_mtime)

    for f in filesTemplates:
        file = "template/" + f
        files.append(file)
        m_times.append(os.stat(file).st_mtime)
    
    for f in filesStatic:
        file = "static/" + f
        files.append(file)
        m_times.append(os.stat(file).st_mtime)

    return (files, m_times)

                
class Handler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/':
            self.path = 'public/homepage.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
    

    # #mute output into terminal...
    def log_message(self, format, *args):
        return 


def makeDir(dirName: str) -> None:
    
    if not os.path.isdir(dirName):
        os.makedirs(dirName)
    else:
        shutil.rmtree(dirName)
        os.makedirs(dirName)


class MyServer(threading.Thread):

    def run(self):
        global tabOpen
       
        try:
            self.server = ThreadingHTTPServer(('localhost', 8080), Handler)
            print("\nLocal server at http://localhost:8080/")
            url = "http://localhost:8080/"
            if not tabOpen:
                webbrowser.get(using="chrome").open(url,new=0)
                tabOpen = True
                
            self.server.serve_forever()
        except (OSError, KeyboardInterrupt):
            print("oops, socket error, or some type of error at least...")
        
    def stop(self):
        self.server.shutdown()
        self.server.server_close()


class fileWatcher(object):
    def __init__(self, fileNames, file_mtimes):
        self.fileNames = fileNames
        self._cached_stamps = file_mtimes
        

    def check(self):
        files_times = zip(self.fileNames, self._cached_stamps)
        #for each file in pages/, template/, and static/, 
        # check the cached time stamp for last modification with the present time stamp..
        for f, t in files_times:
            stamp = os.stat(f).st_mtime
            if stamp != t:
                print("Changes detected, restarting server...refresh page to observe changes")
                return True
            else:
                pass
        