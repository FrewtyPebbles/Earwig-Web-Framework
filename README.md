# Earwig (1.4.1)
>_IMPORTANT:_ __earwig.py__ USES http.server AND IS RISKY TO USE IN PRODUCTION.  FOR PRODUCTION USE __earwigFlask.py__.

 Earwig is an http server that enables you to use python as a server side scripting language.
 ## How To Get Started
 Earwig is easy to setup and get working with only a few steps:
1. Go into your __settings.txt__ file and change the default port to your desired port.
2. Make a new file with a __.ear__ extension.
3. Now add that file as a route by adding a line to your __settings.txt__ following the format: _UrlRoute=filepathWithoutExtension_
4. Now run your server by entering either of the following into a terminal:
```cmd
py earwig.py
```

```cmd
py earwigFlask.py
```
If all was done correctly, you should be able to find your server hosted at [http://localhost:8000/](http://localhost:8000/) (Assuming you used port 8000)

> Keep in mind the only pages that will load are ones specified as routes in __settings.txt__.  So if you specify the route _UrlRoute=filepathWithoutExtension_ and visit _http://localhost:8000/UrlRoute_ the server will load the page data from _filepathWithoutExtension.ear_.
```coffee
/!/ Server Settings:
port=8000
ip=default
devmode=true
/!/ Forbidden File Extensions
!ear
/!/ Startup Routes:
~=root
login=pages/login
```
 - _ _/!/ is a comment_ _
 - _ _~ specifies that the route URL will be at the base URL_ _
 - _ _! is for marking a file extension as non accessable by the browser's URL_ _
 - _ _/!/ is a comment_ _
 ##How To Write A .ear File
 Earwig is designed to function similar to PHP.  
 
 Example:
 ```python
 <?
import Includes.projectData as siteGlobals
print(
?>
<!DOCTYPE html>
<html lang="en">
  <header>
	<link href='index.css' rel='stylesheet'/>
  </header>
  <body>
<?
)
#render the project list
siteGlobals.renderProjectList()
print(
?>
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod 
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat
nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui
officia deserunt mollit anim id est laborum.
  </body>
</html>
<?
)
?>
```
Essentially any .html or strings that you print by wraping it in a python print() function inside earwig tags _<? ?>_ will be sent to the browser.
> GET AND POST: If you wish to reference data from get variables or post headers/body, you can do so by typing the **R_get["urlVariableName"]** and **R_post["headerorbodyparameter"]** like so.
