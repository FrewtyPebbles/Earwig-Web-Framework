# Earwig 0.9.1
**NOTE: This software is in a beta version, we cannot at this time ensure its stability.**

 Earwig is an http server that enables you to use python as a server side scripting language.
 ## How To Get Started
 Earwig is easy to setup and get working with only a few steps:
1. Go into your __settings.txt__ file and change the default port to your desired port.
2. Make a new file with a __.py__ extension.
3. Now add that file as a route by adding a line to your __settings.txt__ following the format: _UrlRoute=filepathWithoutExtension_
4. Now run your server by entering the following into a terminal:
```shell
py earwig.py
```
If all was done correctly, you should be able to find your server hosted at [http://localhost:8000/](http://localhost:8000/) (Assuming you used port 8000)