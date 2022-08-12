# Earwig 0.10.1
**NOTE: This software is in a beta version, we cannot at this time ensure its stability.**

 Earwig is an http server that enables you serve _.py_ and _.ear_ source files alot like how _.php_ source files are served.

## How To Get Started (Basic)

 Earwig is easy to setup and get working with only a few steps:
1. Go into your __settings.txt__ file and change the default port to your desired port.
2. Make a new file with a __.py__ extension.
3. Now add that file as a route by adding a line to your __settings.txt__ following the format: _UrlRoute=filepathWithExtension_
4. Now run your server by entering the following into a terminal:
```cli
py earwig.py
```
If all was done correctly, you should be able to find your server hosted at [http://localhost:8000/](http://localhost:8000/) (Assuming you used port 8000)

## How Earwig Works (Abridged)

Earwig redirects the python stdout to the http response for incoming http requests.  In other words, anything that is __print()__ed in your earwig page files will be rendered/be the response for the requested url.

## Configuring Your Server Settings and Globals

Earwig server settings are configured in your _settings.EWS_ file.  A bare bones settings.EWS file might look like this:

```lua
/!/ Server Settings:

port=8000
ip=localhost
devmode=false

/!/ Json User Defined Settings:

hashedAuthParameters~["password", "securityQuestion"]
exampleDict~{"setting":"abc"}
startupMessage~"SERVER STARTED"
exampleNumber~-9.99
exampleBool~false

/!/ Init File:

@_boot_.py

/!/ Forbidden File Extensions:

!ear
!py
!db
!EWS

/!/ Startup Routes:

~=root.py
```

---

__NOTE__: The order in which you add settings to your _settings.EWS_ file does not matter.

### IP AND PORT

your server IP and Port can be defined by adding the following to your settings file:

```lua
port=8000
ip=localhost
```

localhost is the ip for a localy hosted server.

### DEVMODE

```lua
devmode=false
```

__IMPORTANT__: It is important that when you are deploying your server that _devmode_ is set to _false_.  _devmode_ can cause slowdowns (and potentialy security issues in future versions of earwig) if enabled in your deployed server.

_devmode_ allows for better python error checking when dealing with _.py_ and _.ear_ pages along with other debug features that arent fully implemented yet.  Dev mode also ensures a full recompile of your _.py_ and _.ear_ pages with every request.

### COMMENTS

`/!/` is the prefix for commented lines

### USER DEFINED SETTINGS/GLOBALS

```lua
settingName~["SomeJson":{"AlsoJson":0,"StillJson"}, "NotNotJson":-123.456]
AnotherSetting~"A string."
AThirdSetting~-3333.3333
AFourthSetting~123
AFithSetting~false
```

_~_ is used as the operator to assign custom settings.  Custom settings can be assigned to any valid json, float, string, integer, or boolean.

### BOOT FILE PATH

The boot file is a _.py_ script that is executed at the startup of your server.  To define the path to a boot file, use the _@_ prefix before your boot file path in your settings file.

Example:

```lua
@src/startup/boot.py
```

### FORBIDDEN EXTENSIONS

Forbidden extensions are defined with the prefix _!_.

Example:

```lua
!db
!py
!ear
```

Declaring extensions as forbidden will make it impossible for http clients to recieve the raw data from requested files with that extension.

### ROUTING

Routing is how you declare the url routes and their corresponding _.ear_ or _.py_ page file.  Its as easy as `urlroute/urlroute=filepath/file.py` or `urlroute/urlroute=filepath/file.ear`.

Example:

```lua
~=pages/root.py
about=pages/about.py
contact=pages/contact.ear
```

_~_ is used to declare the URL's root route.

`~=pages/root.py` means that `pages/root.py` will handle requests sent to `http://yourdns.com/`

`about=pages/about.py` means that `pages/about.py` will handle requests sent to `http://yourdns.com/about`

`contact=pages/contact.ear` means that `pages/contact.py` will handle requests sent to `http://yourdns.com/contact`

## Framework Globals and Accessables

These globals can be accessed in any _.py_ or _.ear_ page file as declared in the routes of your _settings.EWS_ file.

---

`R_get["requestAttribute"]`

R_get is a dictionary containing all parameters/attributes of the incoming GET request.

---

`R_post["requestAttribute"]`

R_post is a dictionary containing all parameters/attributes of the incoming POST request.

---

`_BASE_URL`

Provides the Root of the http URL.  Example _http://yourdns.com/_

---

`_FULL_URL`

Provides the full http URL with route.  Example _http://yourdns.com/pages/about_

---

`_PATH_URL`

Provides the path after the base of the page URL. Example _/pages/about_

---

`_ORIGIN`

Provides the address of the origin of the request (ie: the request client's ip).  Can be used to create blacklists dynamically.

---

`_COOKIES`

Provides a dictionary of all of the cookies from the incoming request.

---

`_MIME_TYPE`

The current mime type for the requested page.

## Framework Functions

These functions can be executed in any _.py_ or _.ear_ page file as declared in the routes of your _settings.EWS_ file.

---

`mime_type(mime:str):`

Change the response mime type.  Returns the mime type.

---

`set_headers(headerDict:dict = {})`

Set/add the headers for the response.  Returns the dictionary of all the headers.

---

`set_setting(_setting:str, _newvalue)`

Change/set a setting. returns the setting's new value.

---

`delete_setting(_setting:str) -> bool`

Deletes a setting. Returns true on success, False on failure.

---

`set_route(_route:str, _path:str)`

Sets a new or existing route dynamically.  Returns a tuple of ( **_route**, **_path** ).

---

`delete_route(_routeOrPath:str, _isRoute: bool = True) -> bool`

Deletes an existing route.  Returns true on success, fail on failure.

---

`append_setting(_setting:str, _appendvalue)`

Appends the *_appendvalue* to the value of the setting provided.  On failure returns false. On success returns the setting's new value.

---

`pop_setting(_setting, num:int = False)`

Performs a _.pop()_ on the value of the setting provided.

## Earwig HTML Renderer

```python3
print(
 eh("header", {}, [
   eh("title", {}, [
    "This is a test site."
   ])
  ])+
  eh("body", {}, [
   eh("p",{},[
    f"{z}"
   ], ind=z) for z in range(1, 6)
  ]
  ).push([
   eh("script",{},[
    """alert("Hello.")"""
   ],singleAttributes=["defer"])
  ])
)
```

The Earwig HTML Renderer allows you to easier tokenize certain elements and apply indexes to them with the _ind_ attribute.  This allows for easier server side procedural element generation, element sorting, and other useful features that are implemented into the _eh_ class. The above code will render the following HTML:

```html
<header>
 <title>This is a test site.</title>
</header>
<body>
 <p>1</p>
 <p>2</p>
 <p>3</p>
 <p>4</p>
 <p>5</p>
 <script defer>
  alert("Hello.")
 </script>
</body>
```

## Auth Tokens

### SYMETRIC AUTH TOKENS

Earwig provides an easy system to set up login tokens and credentials with just a class and a few functions.  With this system you can decide which login parameters are sensitive/hashed.  Auth tokens are both hashed then excrypted.

---

**_CONSTRUCTOR_**

`SymmetricAuthTokens(identifier:str, dbName:str="Accounts", accountTableName:str="Accounts", authTableName:str="symetricAuthTokens")`

The _SymmetricAuthTokens_ class is used as the main handler for your auth system.  You can initialize the class either in a _with_ statement, or call _.close()_ when no longer in use.  This will initialize the auth token table if not already existing.  Each of its constructor's parameters provide a level of control over your auth system:

 - __identifier__ : This is the column name/account parameter in the database that will act as the association between each account and tokens made by those accounts.  The best practice is to make this an account parameter that is not sensitive.
 
 - __dbName__ : This is the name of the _.db_ file that your auth system will connect to.
 
 - __accountTableName__ : This is the name of the table in your auth database that will hold all user accounts.
 
 - __authTableName__ : This is the name of the table in your auth database that will hold all created auth tokens.

---

**_INITIALIZING THE ACCOUNT SYSTEM_**

`.initAccountSystem(requiredParameters:tuple | list = [], authParameters:tuple | list = [], **kwargs:str) -> bool`

The _.initAccountSystem_ member function is used to initialize the account system.  To maximize performance, this should only be called in a _boot.py_ file.  This function will return true on success and false on failure.  The parameters you provide will determine how your account system will function:

 - __requiredParameters__ : The account parameters/database columns that you want to make required in order to successfully make an account.  On success, this will return _true_ and on failure this will return _false_.
 - __authParameters__ : All account parameters/database columns that you would like users to use to login to their account/recive an auth token.
 - __kwargs__ : All and every account parameter that you wish to store in the database/account table should be named as a key and their SQL type should be its value as a string.
