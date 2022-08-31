import subprocess
import platform

def parse_EAR_to_string(filename: str) -> str:
	print(f"FILE: {filename}")
	output = ""
	platform_name = platform.system()
	if platform_name.startswith('Windows'):
		output = subprocess.getoutput(f'libs/ETE.exe {filename} \'debug:true,\'')
	elif platform_name.startswith('Linux'):
		output = subprocess.getoutput(f'libs/ETE {filename} \'debug:true,\'')
	return str(output)