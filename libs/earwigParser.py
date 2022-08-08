import subprocess

def parse_EAR_to_string(filename: str) -> str:
	print(f"FILE: {filename}")
	output = subprocess.getoutput(f'earwigParser {filename}')
	return str(output)