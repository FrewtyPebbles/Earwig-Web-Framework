# Earwig 0.9.1
**NOTE: This software is in a beta version, we cannot at this time ensure its stability.**

 Earwig is an http server that enables you serve _.py_ and _.ear_ source files alot like how _.php_ source files are served.
 ## How To Get Started (Basic)
 Earwig is easy to setup and get working with only a few steps:
1. Go into your __settings.txt__ file and change the default port to your desired port.
2. Make a new file with a __.py__ extension.
3. Now add that file as a route by adding a line to your __settings.txt__ following the format: _UrlRoute=filepathWithoutExtension_
4. Now run your server by entering the following into a terminal:
```shell
py earwig.py
```
If all was done correctly, you should be able to find your server hosted at [http://localhost:8000/](http://localhost:8000/) (Assuming you used port 8000)
## How Earwig Works (Abridged)
Earwig redirects the python stdout to the http response for incoming http requests.  In other words, anything that is __print()__ed in your earwig page files will be rendered/be the response for the requested url.
## Framework Constants and Globals

## Framework Functions

`def mime_type(mime:str):`

 - Change the response mime type.  Returns the mime type.

`def set_headers(headerDict:dict = {}):`

 - Set/add the headers for the response.  Returns the dictionary of all the headers.

`def set_setting(_setting:str, _newvalue):`

 - Change/set a setting. returns the setting's new value.

`def delete_setting(_setting:str) -> bool:`

 - Deletes a setting. Returns true on success, False on failure.

`def append_setting(_setting:str, _appendvalue):`

 - Appends to the value of the setting provided.  On failure returns false. On success returns the setting's new value.

`def pop_setting(_setting, num:int = False):`

 - Performs a _pop()_ on the value of the setting provided.
