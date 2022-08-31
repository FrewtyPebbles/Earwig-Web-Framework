import json
import sqlite3
from cryptography.fernet import Fernet
import hashlib

ACCOUNT_MANAGER_VERSION = "0.1.0"

# TODO
"""
	#	Implement support for other sql dialects

"""
# END TODO

class SymmetricAuthTokens(object):
	"""


		Brief:
		
			Object for handling auth-tokens and login-logout functionality.
	

		Verbose:
	
			Uses asymmetric encryption and SHA-512 hashing to ensure that tokens and login credentials are secure and protected against leaks.  Tokens use an identifier and token pair system to match client tokens to their respected keys with a hashed identifier that is on both the client and database.
		\n\n\n
		"""
	def __init__(self, identifier:str, dbName:str="Accounts", accountTableName:str="Accounts", authTableName:str="symetricAuthTokens"):
		"""


		Brief:

			Creates connection to the database, creates auth-token table if non existant, and takes in the account table name.
		

		Arguments:

			-  identifier: str
			
		Acts as a hashed identifier, used to find a key match for a token in the database when 'SymmetricAuthTokens.checkLogin' is invoked.
			

			-  dbName:str = "Accounts"
			
		The name of the '.db' (without extension) that will be used to store account and auth token data.
			

			-  accountTableName:str = "Accounts"
			
		The name of the table to be created in the 'dbName.db' that will contain account info.
			

			-  authTableName:str = "symetricAuthTokens"
			
		The name of the table to be created in the 'dbName.db' that will contain auth tokens.
		\n\n\n
		"""
		self.con = sqlite3.connect(f'{dbName}.db')
		self.cur = self.con.cursor()
		self.identifier = identifier
		self.tableName = authTableName
		self.accountTableName = accountTableName
		self.hashGen = hashlib.sha512()
		self.authParameters = []
		SQLStatement = f'''CREATE TABLE IF NOT EXISTS {authTableName}
			(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, {identifier} TEXT, tokenKey TEXT, tokenString TEXT, dateCreated DATETIME)'''
		self.cur.execute(SQLStatement)
		self.cur.execute(f"DELETE FROM {authTableName} WHERE dateCreated < DATE('now','-1 day')")
		self.con.commit()

	def login(self, authID:str, accNotFoundMSG:str="Account not found", **kwargs:str) -> dict:
		"""
		 - kwargs should be ONLY the parameters you wish to use to login.

		 - authID should be a non sensitive account login parameter that will act as an identifier for the auth token stored on the server.

		 - accNotFoundMSG is the error message returned in json when an account is not found.
		"""
		key = Fernet.generate_key().decode()
		f = Fernet(key)
		tokenStringToEncrypt = ""
		accTableConditions = ""
		preparedValues = []
		for key, val in kwargs.items():
			accTableConditions += f" {key} = ? AND"
			tokenStringToEncrypt += val
			preparedValues.append(val)
		self.hashGen.update(tokenStringToEncrypt.encode('ascii'))
		tokenStringToEncrypt = self.hashGen.hexdigest()
		encryptedStr = f.encrypt(tokenStringToEncrypt.encode('ascii'))
		SQLstatement = f"INSERT INTO {self.tableName}({self.identifier}, tokenKey, tokenString, dateCreated) VALUES (?, ?, ?, DATE('now'))"
		self.hashGen.update(authID.encode('ascii'))
		authID = self.hashGen.hexdigest()
		self.cur.execute(SQLstatement, (authID, key, tokenStringToEncrypt,))
		authJson = {
			"authToken": encryptedStr.decode(),
			"authID": authID,
			"error":"none"
		}
		#clean up old tokens
		self.cur.execute(f"DELETE FROM {self.tableName} WHERE dateCreated < DATE('now','-1 day')")
		self.con.commit()
		#Check if account exists
		SQLstatement = f'''SELECT count(id) FROM {self.accountTableName} WHERE'''
		SQLstatement += accTableConditions
		SQLstatement += f" 1 = 1"
		self.cur.execute(SQLstatement, preparedValues)
		if self.cur.fetchone()[0] == 1:
			return authJson
		else:
			return {"error":accNotFoundMSG}

	def checkLogin(self, authToken:str, authID:str) -> bool:
		'''
		 -- Returns true on successful token, returns false on failure.
		'''
		self.cur.execute(f"DELETE FROM {self.tableName} WHERE dateCreated < DATE('now','-1 day')")
		self.con.commit()
		SQLstatement = f"SELECT tokenKey, tokenString FROM {self.tableName} WHERE {self.identifier} = ?"
		self.cur.execute(SQLstatement, (authID,))
		for row in self.cur:
			f = Fernet(row[0].encode("ascii"))
			decryptedToken = ""
			try:
				decryptedToken = f.decrypt(authToken.encode("ascii")).decode()
			except:
				return False
			return decryptedToken == row[1]
		return False

	def logout(self, authToken:str, authID:str) -> bool:
		"""
		 -- Used to logout accounts/delete tokens from the database.
		"""
		self.cur.execute(f"DELETE FROM {self.tableName} WHERE dateCreated < DATE('now','-1 day')")
		self.con.commit()
		try:
			SQLstatement = f"DELETE FROM {self.tableName} WHERE {self.identifier} = ?"
			self.cur.execute(SQLstatement, (authID,))
			return True
		except:
			return False

	def configAccountSystem(self, authParameters:tuple | list):
		'''
		 -- must be used in place of initAccountSystem() after it has been called once.
		'''
		self.authParameters = authParameters

	def initAccountSystem(self, requiredParameters:tuple | list = [], authParameters:tuple | list = [], **kwargs:str) -> bool:
		'''
		 -- Should only be called once.  Afterwords replace with configAccountSystem()

		 - requiredParameters should contain keys from kwargs/account parameters which you wish to make required.

		 - kwargs should contain key value pairs of account parameters/data you wish to associate with an account.
		'''
		self.authParameters = authParameters
		SQLStatement = f'''CREATE TABLE IF NOT EXISTS {self.accountTableName}
			(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, '''
		print(f"\n----\nEARWIGAUTH - [SQLITE] Creating AUTH table:\n\t\"{self.accountTableName}\" PARAMETERS ( - Parameter: SQL Data type)\n")
		for key, value in kwargs.items():
			print(f" - {key}: {value}\n")
			if key in requiredParameters:
				SQLStatement += f"{key} {value}, "
			else:
				SQLStatement += f"{key} {value} DEFAULT \"Not provided\", "
		SQLStatement += "dateCreated DATETIME)"
		try:
			self.cur.execute(SQLStatement)
			self.con.commit()
			return True
		except:
			return False

	def addAccount(self, **kwargs:str) -> bool:
		'''
		 - authParameters should contain any sensitive account parameters such as passwords that should be hashed in the database.

		 - kwargs should include any (including login) parameters associated with the account system created using initAccountSystem().
		'''
		SQLStatement = f'''CREATE TABLE IF NOT EXISTS {self.accountTableName}
			(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, '''
		parametersToInsert = ""
		valuesToInsert = []
		preparations = ""
		for key, val in kwargs.items():
			SQLStatement += f"{key} text, "
			parametersToInsert += f"{key}, "
			preparations += "?, "
			if val in self.authParameters:
				self.hashGen.update(val)
				valuesToInsert.append(self.hashGen.hexdigest())
			else:
				valuesToInsert.append(val)
		SQLStatement += "dateCreated DATETIME)"
		try:
			self.cur.execute(SQLStatement)
		except:
			return False
		SQLStatement = f'''INSERT INTO {self.accountTableName}('''
		SQLStatement += parametersToInsert
		SQLStatement += ''' dateCreated) VALUES ('''
		SQLStatement += preparations
		SQLStatement += '''DATE('now'))'''
		try:
			self.cur.execute(SQLStatement, valuesToInsert)
			self.con.commit()
			return True
		except:
			return False

	def removeAccount(self, **kwargs:str) -> bool:
		"""
		 - authParameters should contain a tuple/list of any parameters that were hashed/sensitive when addAccount() was invoked.  In other words, if one of your parameters in kwargs was included in addAccount()'s authParameters parameter, you must include its value in this method's authParameters parameter.

		 - kwargs should be the parameters used to find the account in the account database which you wish to remove.
		"""
		SQLStatement = f"DELETE FROM {self.accountTableName} WHERE "
		preparedParameters = []
		for key, val in kwargs.items():
			SQLStatement += f"{key} = ? AND "
			if val in self.authParameters:
				self.hashGen.update(val)
				preparedParameters.append(self.hashGen.hexdigest())
			else:
				preparedParameters.append(val)
		SQLStatement += "1 = 1"
		try:
			self.cur.execute(SQLStatement, preparedParameters)
			self.con.commit()
			return True
		except:
			return False
	def close(self):
		self.con.close()
	def __enter__(self):
		return self
	def __exit__(self, exc_type, exc_value, exc_traceback):
		self.con.close()


""" EXAMPLE CODE:
with SymmetricAuthTokens("username", dbName='test') as accountManager:
	accountManager.initAccountSystem(username = "varchar(30)", password = "varchar(30)")
	accountManager.addAccount(username = "Bert", password = "123abc")
	print(json.dumps(accountManager.loginUser("Bert", username = "Bert", password = "123abc")))#returns token and identifier as dict
	print(accountManager.checkLogin("Bert's identifier hash", "Bert's token hash"))#validates login and returns true or false
"""