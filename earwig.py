from contextlib import redirect_stdout
from io import StringIO
import os
import re
import textwrap
import threading
from werkzeug.wrappers import Request, Response
from urllib.parse import unquote_plus as URLDECODEPERCENT
from werkzeug.utils import send_from_directory
from werkzeug.serving import run_simple
from werkzeug.datastructures import Headers

#EARWIG FILES
from libs.earwigUtils import *
from libs.earwigParser import parse_EAR_to_string

#EARWIG MODULES
from projectModules.htmlconstructor import *
from projectModules.accountManager import *

#TODO
#
# #  Change routing system from dict to SQL Alchemy database that uses sqlite by default in order to prevent over usage of RAM when dynamically creating routes.
#
#
##############################################
# GLOBAL VARS (nessicary for request system)
##############################################

compiledCode = {}
moduleCache = {}
VERSION_NUMBER = "0.10.1"
Universal = {}
AuthTokens = {}
earwigPages = {}

#parse settings file
requestMimeType = ''
setting = {}
routingPath = {}
forbiddenExtensions = []
headers = Headers()


######################################
# SETTINGS PARSER
######################################

with open('settings.EWS') as settingsFile:
	settingsLines = settingsFile.read().splitlines()
	linenum = 0
	for line in settingsLines:
		linenum += 1
		if line == "":
			continue
		elif line[0] == '!':
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
			elif line.startswith('@'):
				setting['_boot_'] = line[1:]
			elif '~' in line:
				LRside = line.split('~', 1)
				if '[' in LRside[1] or '{' in LRside[1]:
					setting[LRside[0]] = json.loads(LRside[1])
				elif LRside[1] == "true" or LRside[1] == "false":
					setting[LRside[0]] = bool(LRside[1])
				elif LRside[1].replace(".","",1).replace("-","",1).isdigit():
					if '.' in LRside[1]:
						setting[LRside[0]] = float(LRside[1])
					else:
						setting[LRside[0]] = int(LRside[1])
				else:
					if '"' not in LRside[1][0]:
						FatalERROR("settings", "Expected opening \", none provided.  String type assumed.", linenum)
					if '"' not in LRside[1][-1]:
						FatalERROR("settings", "Expected closing \", none provided.  String type expected.", linenum)
					setting[LRside[0]] = LRside[1][1:-1]
			else:
				routingPath[settingPair[0]] = settingPair[1]
globalEW = {}
globalEW["EWcompiledCode"] = compiledCode
globalEW["EWmoduleCache"] = moduleCache
globalEW["EWUniversal"] = Universal
globalEW["EWAuthTokens"] = AuthTokens
globalEW["EWearwigPages"] = earwigPages
globalEW["EWsetting"] = setting
globalEW["EWroutingPath"] = routingPath
globalEW["EWforbiddenExtensions"] = forbiddenExtensions


###########################
# UTILS
###########################

#http settings modifiers
def mime_type(mime: str):
	if mime.lower() == "json":
		globalEW["requestMimeType"] = 'text/json'
	elif mime.lower() == "html":
		globalEW["requestMimeType"] = 'text/html'
	elif mime.lower() == "css":
		globalEW["requestMimeType"] = 'text/css'
	elif mime.lower() == "js" or mime.lower() == "javascript":
		globalEW["requestMimeType"] = 'text/javascript'
	elif mime.lower() == "wasm":
		globalEW["requestMimeType"] = 'application/wasm'
	else:
		globalEW["requestMimeType"] = mime
	return globalEW["requestMimeType"]

def set_headers(headerDict:dict = {}):
	for key, val in headerDict.items():
		globalEW["EWheaders"].set(key, val)
	return globalEW["EWheaders"]

#setting modifiers
def set_setting(_setting:str, _newvalue):
	setting[_setting] = _newvalue
	return _newvalue

def set_route(_route:str, _path:str):
	routingPath[_route] = _path
	return (_route, _path)

def delete_route(_routeOrPath:str, _isRoute: bool = True) -> bool:
	if _isRoute:
		try:
			del routingPath[_routeOrPath]
			return True
		except:
			return False
	else:
		try:
			for route in routingPath:
				if routingPath[route] == _routeOrPath:
					del routingPath[route]
					return True
			return False
		except:
			return False

def append_setting(_setting:str, _appendvalue):
	try:
		setting[_setting].append(_appendvalue)
		return setting[_setting]
	except:
		return False

def delete_setting(_setting:str) -> bool:
	try:
		del setting[_setting]
		return True
	except:
		return False

def pop_setting(_setting, num:int = False):
	try:
		if num == False:
			setting[_setting].pop()
		else:
			setting[_setting].pop(num)
		return setting[_setting]
	except:
		return False

def renderPagePython(filename: str, fileContent, R_get, R_post, recompile):
	#FRAMEWORK VARS
	_BASE_URL = globalEW["ew_BASE_URL"]
	_FULL_URL = globalEW["ew_FULL_URL"]
	_PATH_URL = globalEW["ew_PATH_URL"]
	_ORIGIN = globalEW["ew_REQUEST_ORIGIN"]
	_COOKIES = globalEW["ew_REQUEST_COOKIES"]
	_MIME_TYPE = globalEW["EWheaders"]
	#
	compiledHTML=""
	extensionStr = filename.split('.')[1]
	parsedSource = ""
	if extensionStr == "ear":
		parsedSource = textwrap.dedent(parse_EAR_to_string(filename))
	elif extensionStr == "py":
		pyfile = open(filename)
		parsedSource = pyfile.read()
		pyfile.close()
	if recompile:
		print(f"EARWIG -{' DEV -' if setting['devmode'] else ''} [FILE \"{filename}\"] Recompiling source")
	if recompile or setting["devmode"]:
		tfname = f"{filename}tmp" if setting['devmode'] else ''
		if setting['devmode']:
			tempfile = open(tfname, 'w')
			tempfile.write(parsedSource)
			tempfile.close()
		globalEW["EWcompiledCode"][filename] = compile(parsedSource, tfname, "exec")
		if setting['devmode']:
			threading.Thread(target=lambda:os.remove(tfname), daemon=True).start()
	f = StringIO()
	with redirect_stdout(f):
		exec(globalEW["EWcompiledCode"][filename])
	compiledHTML = f.getvalue()
	return compiledHTML

############################
# REQUESTS
############################

@Request.application
def application(request):
	#FRAMEWORK VARIABLES
	globalEW["ew_BASE_URL"] = request.root_url
	globalEW["ew_FULL_URL"] = request.base_url
	globalEW["EWheaders"] = Headers()
	globalEW["ew_PATH_URL"] = request.path
	globalEW["ew_REQUEST_ORIGIN"] = request.origin
	globalEW["ew_REQUEST_COOKIES"] = request.cookies
	if request.method == 'POST':
		globalEW["requestMimeType"] = ''
		urlVars = {}
		postVars = request.form
		postVars = {**postVars, **request.headers}
		postVars = {**postVars, **request.files}
		urlSlug = request.path[1:]
		render=""
		if '.' not in request.path:
			globalEW["requestMimeType"] = 'text/html'
			rawURLVars = []
			if '?' in request.url:
				rawURLVars = request.full_path.split('?', 1)[1].split('&')
			for i in range(0, len(rawURLVars)):
				data = rawURLVars[i].split('=')
				urlVars[data[0]] = URLDECODEPERCENT(data[1])
			if routingPath[urlSlug]  not in globalEW["EWearwigPages"]:
				globalEW["EWearwigPages"][routingPath[urlSlug]] = open(routingPath[urlSlug], 'r').read()
				render = f"""{renderPagePython(routingPath[urlSlug],
							globalEW["EWearwigPages"][routingPath[urlSlug]],
							R_get=urlVars, R_post=postVars, recompile=True)}"""
			elif globalEW["EWearwigPages"][routingPath[urlSlug]] != open(routingPath[urlSlug], 'r').read():
				globalEW["EWearwigPages"][routingPath[urlSlug]] = open(routingPath[urlSlug], 'r').read()
				render = f"""{renderPagePython(routingPath[urlSlug],
							globalEW["EWearwigPages"][routingPath[urlSlug]],
							R_get=urlVars, R_post=postVars, recompile=True)}"""
			else:
				globalEW["EWearwigPages"][routingPath[urlSlug]] = open(routingPath[urlSlug], 'r').read()
				render = f"""{renderPagePython(routingPath[urlSlug],
							globalEW["EWearwigPages"][routingPath[urlSlug]],
							R_get=urlVars, R_post=postVars, recompile=False)}"""
		elif check_forbidden(request.path.rsplit('.', 1)[1], forbiddenExtensions):
			if request.path.endswith(".js"):
				globalEW["requestMimeType"] = 'text/javascript'
			if request.path.endswith(".css"):
				globalEW["requestMimeType"] = 'text/css'
			if request.path.endswith(".json"):
				globalEW["requestMimeType"] = 'text/json'
			if request.path.endswith(".wasm"):
				globalEW["requestMimeType"] = 'application/wasm'
				print(request.path.rsplit('/', 1)[0][1:] + request.path.rsplit('/', 1)[1])
				return send_from_directory(request.path.rsplit('/', 1)[0][1:], request.path.rsplit('/', 1)[1])
			render = f"{open(request.path.split('/', 1)[1], 'r').read()}"
		return Response(render, mimetype=globalEW["requestMimeType"], headers=globalEW["EWheaders"])
	else:
		globalEW["requestMimeType"] = ''
		urlVars = {}
		urlSlug = request.path[1:]
		render=""
		if '.' not in request.path:
			globalEW["requestMimeType"] = 'text/html'
			rawURLVars = []
			if '?' in request.url:
				rawURLVars = request.full_path.split('?', 1)[1].split('&')
			for i in range(0, len(rawURLVars)):
				data = rawURLVars[i].split('=')
				urlVars[data[0]] = URLDECODEPERCENT(data[1])
			if routingPath[urlSlug]  not in globalEW["EWearwigPages"]:
				globalEW["EWearwigPages"][routingPath[urlSlug]] = open(routingPath[urlSlug], 'r').read()
				render = f"""{renderPagePython(routingPath[urlSlug],
							globalEW["EWearwigPages"][routingPath[urlSlug]],
							R_get=urlVars, R_post={}, recompile=True)}"""
			elif globalEW["EWearwigPages"][routingPath[urlSlug]] != open(routingPath[urlSlug], 'r').read():
				globalEW["EWearwigPages"][routingPath[urlSlug]] = open(routingPath[urlSlug], 'r').read()
				render = f"""{renderPagePython(routingPath[urlSlug],
							globalEW["EWearwigPages"][routingPath[urlSlug]],
							R_get=urlVars, R_post={}, recompile=True)}"""
			else:
				globalEW["EWearwigPages"][routingPath[urlSlug]] = open(routingPath[urlSlug], 'r').read()
				render = f"""{renderPagePython(routingPath[urlSlug],
							globalEW["EWearwigPages"][routingPath[urlSlug]],
							R_get=urlVars, R_post={}, recompile=False)}"""
		elif check_forbidden(request.path.rsplit('.', 1)[1], forbiddenExtensions):
			if request.path.endswith(".js"):
				globalEW["requestMimeType"] = 'text/javascript'
			if request.path.endswith(".css"):
				globalEW["requestMimeType"] = 'text/css'
			if request.path.endswith(".json"):
				globalEW["requestMimeType"] = 'text/json'
			if request.path.endswith(".wasm"):
				globalEW["requestMimeType"] = 'application/wasm'
				print(request.path.rsplit('/', 1)[0][1:] + request.path.rsplit('/', 1)[1])
				return send_from_directory(request.path.rsplit('/', 1)[0][1:], request.path.rsplit('/', 1)[1])
			render = f"{open(request.path.split('/', 1)[1], 'r').read()}"
		return Response(render, mimetype=globalEW["requestMimeType"], headers=globalEW["EWheaders"])

#######################################
# SERVER STARTUP
#######################################

if __name__ == "__main__":#execute server
	#display server parameters
	print(f"\n----\nEARWIG -{' DEV -' if setting['devmode'] else ''} [PORT { 8000 if setting['port'] == 'default' else int(setting['port'])}] Starting server...")
	print("\nSettings:")
	
	for settingKey in setting.keys():
		print(f"\t- {settingKey}: {setting[settingKey]}")
	
	print("\nForbidden Extensions:")
	
	for forbidden in forbiddenExtensions:
		print(f"\t- {forbidden}")

	print("\nRoutes:")

	for routingKey in routingPath.keys():
		print(f"\t- {routingKey if routingKey != '' else '~'}: {routingPath[routingKey]}")
	
	print(f"\nEARWIG -{' DEV -' if setting['devmode'] else ''} [PORT { 8000 if setting['port'] == 'default' else int(setting['port'])}] Running boot script...\n")
	
	exec(open(setting['_boot_']).read())
	
	print(f"\nEARWIG -{' DEV -' if setting['devmode'] else ''} [PORT { 8000 if setting['port'] == 'default' else int(setting['port'])}] Server started.\n")
	#run the server
	run_simple(setting["ip"], int(setting['port']), application)
	#closing msg
	print(f"\nEARWIG -{' DEV -' if setting['devmode'] else ''} [PORT { 8000 if setting['port'] == 'default' else int(setting['port'])}] Server closed.\n")