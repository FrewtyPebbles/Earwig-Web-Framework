#EARWIG TEMPLATE SYSTEM BY William Lim
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote as URLDECODEPERCENT
import re
from io import StringIO
from contextlib import redirect_stdout
import textwrap
import cgi
HTTP_IMPORTS = ['http.server','urllib.parse','re','io','contextlib','textwrap','cgi', __name__]

compiledCode = {}
VERSION_NUMBER = "1.4.1"
Universal = {}
earwigPages = {}

#parse settings file
setting = {}
routingPath = {}
forbiddenExtensions = []
with open('settings.txt') as settingsFile:
	settingsLines = settingsFile.read().splitlines()
	for line in settingsLines:
		if line[0] == '!':
			forbiddenExtensions.append(line[1:])
		elif not line.startswith("/!/"):
			settingPair = line.split('=')
			if line.startswith('ip') or line.startswith('port') or line.startswith('devmode'):
				if line.startswith('devmode'):
					setting[settingPair[0]] = True if settingPair[1].upper() == "TRUE" else False
				else:
					setting[settingPair[0]] = settingPair[1]
			elif line.startswith('~'):
				routingPath[''] = settingPair[1]
			else:
				routingPath[settingPair[0]] = settingPair[1]
def check_forbidden(fileEx):
	if fileEx in forbiddenExtensions:
		return False
	return True

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
		print(f"EARWIG -{' DEV' if setting['devmode'] else ''} - [FILE \"{filename}\"] Recompiling source")
	f = StringIO()
	with redirect_stdout(f):
		if recompile or setting["devmode"]:
			compiledCode[filename] = compile(source=textwrap.dedent(parsedSource), filename="fake", mode="exec")
		exec(compiledCode[filename])
	compiledHTML = f.getvalue()
	return compiledHTML

class handler(BaseHTTPRequestHandler):
	def do_GET(self):
		global earwigPages
		self.send_response(200)
		urlVars = {}
		if '/?' in str(self.path):
			urlSlug = self.path.split('/',1)[1].split('?', 1)[0]
			if urlSlug[len(urlSlug)-1] == '/':
				urlSlug = urlSlug[:-1]
		elif self.path[len(self.path)-1] == '/':
			urlSlug = self.path.split('/',1)[1][:-1]
		else:
			urlSlug = self.path.split('/',1)[1]
		render=""
		if '.' not in self.path:
			self.send_header('Content-type','text/html')
			self.end_headers()
			rawURLVars = []
			if '?' in self.path:
				rawURLVars = self.path.split('?', 1)[1].split('&')
			for i in range(0, len(rawURLVars)):
				data = rawURLVars[i].split('=')
				urlVars[data[0]] = URLDECODEPERCENT(data[1])
			if routingPath[urlSlug] +'.ear' not in earwigPages:
				earwigPages[routingPath[urlSlug]+'.ear'] = open(routingPath[urlSlug]+'.ear', 'r').read()
				render = f"{renderPagePython(routingPath[urlSlug]+'.ear', earwigPages[routingPath[urlSlug]+'.ear'], R_get=urlVars, R_post={}, recompile=True)}"
			elif earwigPages[routingPath[urlSlug]+'.ear'] != open(routingPath[urlSlug]+'.ear', 'r').read():
				earwigPages[routingPath[urlSlug]+'.ear'] = open(routingPath[urlSlug]+'.ear', 'r').read()
				render = f"{renderPagePython(routingPath[urlSlug]+'.ear', earwigPages[routingPath[urlSlug]+'.ear'], R_get=urlVars, R_post={}, recompile=True)}"
			else:
				earwigPages[routingPath[urlSlug]+'.ear'] = open(routingPath[urlSlug]+'.ear', 'r').read()
				render = f"{renderPagePython(routingPath[urlSlug]+'.ear', earwigPages[routingPath[urlSlug]+'.ear'], R_get=urlVars, R_post={}, recompile=False)}"
		elif check_forbidden(self.path.rsplit('.', 1)[1]):
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
		if '/?' in str(self.path):
			urlSlug = self.path.split('/',1)[1].split('?', 1)[0]
			if urlSlug.endswith('/'):
				urlSlug = urlSlug[:-1]
		else:
			urlSlug = self.path.split('/',1)[1]
		headerVars = {}
		formVars = {}
		headerValues = self.headers.items()
		for i in range(0, len(headerValues)):
			headerVars[headerValues[i][0]] = headerValues[i][1]
		if self.headers['Content-Type'] != None:
			ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
			if ctype == 'multipart/form-data':
				pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')
				formVars = cgi.parse_multipart(self.rfile, pdict)
				headerVars.update(formVars)
		render=""
		if '.' not in self.path:
			self.send_header('Content-type','text/html')
			self.end_headers()
			rawURLVars = []
			if '?' in self.path:
				rawURLVars = self.path.split('?', 1)[1].split('&')
			for i in range(0, len(rawURLVars)):
				data = rawURLVars[i].split('=')
				urlVars[data[0]] = URLDECODEPERCENT(data[1])
			if routingPath[urlSlug]+'.ear' not in earwigPages:
				earwigPages[routingPath[urlSlug]+'.ear'] = open(routingPath[urlSlug]+'.ear', 'r').read()
				render = f"{renderPagePython(routingPath[urlSlug]+'.ear', earwigPages[routingPath[urlSlug]+'.ear'], R_get=urlVars, R_post=headerVars, recompile=True)}"
			elif earwigPages[routingPath[urlSlug]+'.ear'] != open(routingPath[urlSlug]+'.ear', 'r').read():
				earwigPages[routingPath[urlSlug]+'.ear'] = open(routingPath[urlSlug]+'.ear', 'r').read()
				render = f"{renderPagePython(routingPath[urlSlug]+'.ear', earwigPages[routingPath[urlSlug]+'.ear'], R_get=urlVars, R_post=headerVars, recompile=True)}"
			else:
				earwigPages[routingPath[urlSlug]+'.ear'] = open(routingPath[urlSlug]+'.ear', 'r').read()
				render = f"{renderPagePython(routingPath[urlSlug]+'.ear', earwigPages[routingPath[urlSlug]+'.ear'], R_get=urlVars, R_post=headerVars, recompile=False)}"
		elif check_forbidden(self.path.rsplit('.', 1)[1]):
			pathString = ""
			for pathpart in self.path.split('/')[1:]:
				pathString += f"/{pathpart}"
			self.send_header('Content-type','*/*')
			self.end_headers()
			render = f"{open(pathString[1:], 'r').read()}"
		self.wfile.write(bytes(render, "utf8"))

print(f"\n----\nEARWIG -{' DEV' if setting['devmode'] else ''} - [PORT { 8000 if setting['port'] == 'default' else int(setting['port'])}] Starting server")
print("\nSettings:")
for settingKey in setting.keys():
	print(f"\t- {settingKey}: {setting[settingKey]}")
print("\nRoutes:")
for routingKey in routingPath.keys():
	print(f"\t- {routingKey if routingKey != '' else '~'}: {routingPath[routingKey]}")
print(f"\nEARWIG -{' DEV' if setting['devmode'] else ''} - [ROOT { setting['ip'] }] Your root page can be found at:\n\n - http://localhost:{ 8000 if setting['port'] == 'default' else int(setting['port'])}/\n\n----")
with HTTPServer(('' if setting['ip'] == 'default' else setting['ip'], 8000 if setting['port'] == 'default' else int(setting['port'])), handler) as server:
	server.serve_forever()