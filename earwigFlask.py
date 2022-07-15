from contextlib import redirect_stdout
from io import StringIO
import re
import textwrap
from flask import Flask, request, Response, send_from_directory
from urllib.parse import unquote_plus as URLDECODEPERCENT

compiledCode = {}
moduleCache = {}
VERSION_NUMBER = "0.5.1"
Universal = {}
AuthTokens = {}
earwigPages = {}

#parse settings file
requestMimeType = ''
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

def mime_type(mime):
	global requestMimeType
	if mime.lower() == "json":
		mime = 'text/json'
	requestMimeType = mime

def importEar(filepath: str):
	global requestMimeType
	with open(filepath) as fileobj:
		fileContent = fileobj.read()
		parsedSource = ""
		sections =  re.split("<\?|\?>", fileContent.replace('\\n', '\\\\n'))
		for i in range(0,len(sections)):
			backend = i % 2 # see if it is python code
			if backend:
				parsedSource += sections[i]
			else:
				parsedSource += '"""' + sections[i] + '"""'
		if filepath not in compiledCode.keys() or filepath not in moduleCache.keys() or parsedSource != moduleCache[filepath] or setting["devmode"]:
			moduleCache[filepath] = parsedSource
			compiledCode[filepath] = compile(source=textwrap.dedent(parsedSource), filename="fake", mode="exec")
		exec(compiledCode[filepath])

def renderPagePython(filename, fileContent, R_get, R_post, recompile):
	global compiledCode
	global requestMimeType
	compiledHTML=""
	#parsed source
	parsedSource = ""
	sections =  re.split("<\?|\?>", fileContent.replace('\\n', '\\\\n'))
	for i in range(0,len(sections)):
		backend = i % 2 # see if it is python code
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

app = Flask(__name__)

@app.route('/')
@app.route("/<path:path>", methods=["POST", "GET"])
def earwig(path=""):
	print(compiledCode.keys())
	global earwigPages
	global requestMimeType
	if request.method == 'POST':
		requestMimeType = ''
		urlVars = {}
		postVars = request.form
		postVars = {**postVars, **request.headers}
		postVars = {**postVars, **request.files}
		urlSlug = request.path[1:]
		render=""
		if '.' not in request.path:
			requestMimeType = 'text/html'
			rawURLVars = []
			if '?' in request.url:
				rawURLVars = request.full_path.split('?', 1)[1].split('&')
			for i in range(0, len(rawURLVars)):
				data = rawURLVars[i].split('=')
				urlVars[data[0]] = URLDECODEPERCENT(data[1])
			if routingPath[urlSlug] +'.ear' not in earwigPages:
				earwigPages[routingPath[urlSlug]+'.ear'] = open(routingPath[urlSlug]+'.ear', 'r').read()
				render = f"{renderPagePython(routingPath[urlSlug]+'.ear', earwigPages[routingPath[urlSlug]+'.ear'], R_get=urlVars, R_post=postVars, recompile=True)}"
			elif earwigPages[routingPath[urlSlug]+'.ear'] != open(routingPath[urlSlug]+'.ear', 'r').read():
				earwigPages[routingPath[urlSlug]+'.ear'] = open(routingPath[urlSlug]+'.ear', 'r').read()
				render = f"{renderPagePython(routingPath[urlSlug]+'.ear', earwigPages[routingPath[urlSlug]+'.ear'], R_get=urlVars, R_post=postVars, recompile=True)}"
			else:
				earwigPages[routingPath[urlSlug]+'.ear'] = open(routingPath[urlSlug]+'.ear', 'r').read()
				render = f"{renderPagePython(routingPath[urlSlug]+'.ear', earwigPages[routingPath[urlSlug]+'.ear'], R_get=urlVars, R_post=postVars, recompile=False)}"
		elif check_forbidden(request.path.rsplit('.', 1)[1]):
			if request.path.endswith(".js"):
				requestMimeType = 'text/javascript'
			if request.path.endswith(".css"):
				requestMimeType = 'text/css'
			if request.path.endswith(".json"):
				requestMimeType = 'text/json'
			if request.path.endswith(".wasm"):
				requestMimeType = 'application/wasm'
				print(request.path.rsplit('/', 1)[0][1:] + request.path.rsplit('/', 1)[1])
				return send_from_directory(request.path.rsplit('/', 1)[0][1:], request.path.rsplit('/', 1)[1])
			render = f"{open(request.path.split('/', 1)[1], 'r').read()}"
		print(requestMimeType)
		return Response(render, mimetype=requestMimeType)
	else:
		print(path)
		requestMimeType = ''
		urlVars = {}
		urlSlug = request.path[1:]
		render=""
		if '.' not in request.path:
			requestMimeType = 'text/html'
			rawURLVars = []
			if '?' in request.url:
				rawURLVars = request.full_path.split('?', 1)[1].split('&')
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
		elif check_forbidden(request.path.rsplit('.', 1)[1]):
			if request.path.endswith(".js"):
				requestMimeType = 'text/javascript'
			if request.path.endswith(".css"):
				requestMimeType = 'text/css'
			if request.path.endswith(".json"):
				requestMimeType = 'text/json'
			if request.path.endswith(".wasm"):
				requestMimeType = 'application/wasm'
				print(request.path.rsplit('/', 1)[0][1:] + request.path.rsplit('/', 1)[1])
				return send_from_directory(request.path.rsplit('/', 1)[0][1:], request.path.rsplit('/', 1)[1])
			render = f"{open(request.path.split('/', 1)[1], 'r').read()}"
		return Response(render, mimetype=requestMimeType)



if __name__ == "__main__":
	print(f"\n----\nEARWIG -{' DEV' if setting['devmode'] else ''} - [PORT { 8000 if setting['port'] == 'default' else int(setting['port'])}] Starting server")
	print("\nSettings:")
	for settingKey in setting.keys():
		print(f"\t- {settingKey}: {setting[settingKey]}")
	print("\nRoutes:")
	for routingKey in routingPath.keys():
		print(f"\t- {routingKey if routingKey != '' else '~'}: {routingPath[routingKey]}")
	app.run(host=('0.0.0.0' if setting['ip'] == 'default' else setting['ip']), port=( 8000 if setting['port'] == 'default' else int(setting['port'])))
