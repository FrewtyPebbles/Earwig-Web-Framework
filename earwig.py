#EARWIG TEMPLATE SYSTEM BY William Lim
#ver 1.0.0
from http.server import BaseHTTPRequestHandler, HTTPServer
import ssl
from urllib.parse import unquote as URLDECODEPERCENT
import re
from io import StringIO
from contextlib import redirect_stdout
import textwrap
import cgi

compiledCode = {}
VERSION_NUMBER = "1.0.0"
earwigVars = {}
earwigPages = {}

def renderPagePython(filename, fileContent, R_get, R_post, recompile):
	global compiledCode
	compiledHTML=""
	#TOKENIZER
	parsedSource = ""
	sections =  re.split("<\?|\?>", fileContent)
	for i in range(0,len(sections)):
		backend = i % 2 # see if it is earwig code
		if backend:
			parsedSource += sections[i]
		else:
			parsedSource += '"""' + sections[i] + '"""'
	if recompile:
		print(f"EARWIG - - [FILE \"{filename}\"] Recompiling source")
	f = StringIO()
	with redirect_stdout(f):
		if recompile:
			compiledCode[filename] = compile(source=textwrap.dedent(parsedSource[6:-7]), filename="fake", mode="exec")
		exec(compiledCode[filename])
	compiledHTML = f.getvalue()
	return compiledHTML

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global earwigPages
        self.send_response(200)
        urlVars = {}
        render=""
        if '?' in self.path and not self.path.endswith(".js") and not self.path.endswith(".css") and not self.path.endswith(".json"):
            self.send_header('Content-type','text/html')
            self.end_headers()
            rawURLVars = self.path.split('?')[1].split('&')
            for i in range(0, len(rawURLVars)):
                data = rawURLVars[i].split('=')
                urlVars[data[0]] = URLDECODEPERCENT(data[1])
            if urlVars['page']+'.ewtl' not in earwigPages:
                earwigPages[urlVars['page']+'.ewtl'] = open(urlVars['page']+'.ewtl', 'r').read()
                render = f"{renderPagePython(urlVars['page']+'.ewtl', earwigPages[urlVars['page']+'.ewtl'], R_get=urlVars, R_post={}, recompile=True)}"
            elif earwigPages[urlVars['page']+'.ewtl'] != open(urlVars['page']+'.ewtl', 'r').read():
                earwigPages[urlVars['page']+'.ewtl'] = open(urlVars['page']+'.ewtl', 'r').read()
                render = f"{renderPagePython(urlVars['page']+'.ewtl', earwigPages[urlVars['page']+'.ewtl'], R_get=urlVars, R_post={}, recompile=True)}"
            else:
                earwigPages[urlVars['page']+'.ewtl'] = open(urlVars['page']+'.ewtl', 'r').read()
                render = f"{renderPagePython(urlVars['page']+'.ewtl', earwigPages[urlVars['page']+'.ewtl'], R_get=urlVars, R_post={}, recompile=False)}"
        elif self.path.endswith(".js") or self.path.endswith(".css") or self.path.endswith(".json"):
            pathString = ""
            for pathpart in self.path.split('/')[1:]:
                pathString += f"/{pathpart}"
            if self.path.endswith(".js"):
                self.send_header('Content-type','text/javascript')
            if self.path.endswith(".css"):
                self.send_header('Content-type','text/css')
            if self.path.endswith(".json"):
                self.send_header('Content-type','text/json')
            self.end_headers()
            render = f"{open(pathString[1:], 'r').read()}"
        self.wfile.write(bytes(render, "utf8"))
    def do_POST(self):
        global earwigPages
        self.send_response(200)
        urlVars = {}
        headerVars = {}
        headerValues = self.headers.items()
        for i in range(0, len(headerValues)):
            headerVars[headerValues[i][0]] = headerValues[i][1]
        ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
        formVars = {}
        if ctype == 'multipart/form-data':
            pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')
            formVars = cgi.parse_multipart(self.rfile, pdict)
            headerVars.update(formVars)
        render=""
        if '?' in self.path and not self.path.endswith(".js") and not self.path.endswith(".css") and not self.path.endswith(".json"):
            self.send_header('Content-type','text/html')
            self.end_headers()
            rawURLVars = self.path.split('?')[1].split('&')
            for i in range(0, len(rawURLVars)):
                data = rawURLVars[i].split('=')
                urlVars[data[0]] = URLDECODEPERCENT(data[1])
            if urlVars['page']+'.ewtl' not in earwigPages:
                earwigPages[urlVars['page']+'.ewtl'] = open(urlVars['page']+'.ewtl', 'r').read()
                render = f"{renderPagePython(urlVars['page']+'.ewtl', earwigPages[urlVars['page']+'.ewtl'], R_get=urlVars, R_post=headerVars, recompile=True)}"
            elif earwigPages[urlVars['page']+'.ewtl'] != open(urlVars['page']+'.ewtl', 'r').read():
                earwigPages[urlVars['page']+'.ewtl'] = open(urlVars['page']+'.ewtl', 'r').read()
                render = f"{renderPagePython(urlVars['page']+'.ewtl', earwigPages[urlVars['page']+'.ewtl'], R_get=urlVars, R_post=headerVars, recompile=True)}"
            else:
                earwigPages[urlVars['page']+'.ewtl'] = open(urlVars['page']+'.ewtl', 'r').read()
                render = f"{renderPagePython(urlVars['page']+'.ewtl', earwigPages[urlVars['page']+'.ewtl'], R_get=urlVars, R_post=headerVars, recompile=False)}"
        elif self.path.endswith(".js") or self.path.endswith(".css") or self.path.endswith(".json"):
            pathString = ""
            for pathpart in self.path.split('/')[1:]:
                pathString += f"/{pathpart}"
            self.send_header('Content-type','*/*')
            self.end_headers()
            render = f"{open(pathString[1:], 'r').read()}"
        self.wfile.write(bytes(render, "utf8"))
setting = {}
with open('Settings.txt') as settingsFile:
    settingsLines = settingsFile.read().splitlines()
    for line in settingsLines:
        settingPair = line.split('=')
        setting[settingPair[0]] = settingPair[1]
print(f"EARWIG - - [PORT { 8000 if setting['port'] == 'default' else int(setting['port'])}] Starting server")

with HTTPServer(('' if setting['ip'] == 'default' else setting['ip'], 8000 if setting['port'] == 'default' else int(setting['port'])), handler) as server:
    server.serve_forever()