#This file contains Helper functions for earwig.py

def check_forbidden(fileEx, forbiddenExtensions):
	if fileEx in forbiddenExtensions:
		return False
	return True

def FatalERROR(type, msg, linenum = "?"):
	if type == "settings":
		print(f"\nEARWIG - ! - [ERROR line:{linenum}] {msg}")
		print(f"FORCE EXITING [type {type}]: Fatal error.")
		exit()