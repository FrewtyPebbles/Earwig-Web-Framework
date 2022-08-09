#earwig HTML Constructor


class eh(object):
	def __init__(self, element:str, attributes:dict, scope:list, ind:int=0, singleAttributes:list|tuple = []):
		self.element = element
		self.attributes = attributes
		self.scope = scope
		self.index = ind
		self.singleAttributes = singleAttributes
	def __str__(self) -> str:
		retStr = f"<{self.element}"
		for attr, val in self.attributes.items():
			retStr = f"{retStr} {attr}=\"{val}\""
		for attr in self.singleAttributes:
			retStr = f"{retStr} {attr}"
		retStr = f"{retStr}>"
		for elem in self.scope:
			retStr = f"{retStr}{elem}"
		retStr = f"{retStr}</{self.element}>"
		return retStr
	def __format__(self, __format_spec: str) -> str:
		retStr = f"<{self.element}"
		for attr, val in self.attributes.items():
			retStr = f"{retStr} {attr}=\"{val}\""
		for attr in self.singleAttributes:
			retStr = f"{retStr} {attr}"
		retStr = f"{retStr}>"
		for elem in self.scope:
			retStr = f"{retStr}{elem}"
		retStr = f"{retStr}</{self.element}>"
		return retStr
	def sort_ascending_index(self):
		newScope = dict(zip([elem.index for elem in self.scope], self.scope))
		try:
			self.scope = [newScope[i] for i in range(len(newScope))]
		except:
			self.scope = []
			newIndexes = list(newScope.keys())
			newIndexes.sort()
			for i in newIndexes:
					self.scope.append(newScope[i])
		return self
	def sort_descending_index(self):
		newScope = dict(zip([elem.index for elem in self.scope], self.scope))
		try:
			self.scope = [newScope[i] for i in range(len(newScope))]
			self.scope.reverse()
		except:
			self.scope = []
			newIndexes = list(newScope.keys())
			newIndexes.sort()
			for i in newIndexes:
				self.scope.append(newScope[i])
			self.scope.reverse()
		return self
	def push(self, elements:list|tuple):
		self.scope += elements
		return self
	def __add__(self, other):
			return f"{self}{other}"
	def __radd__(self, other):
			return f"{other}{self}"

'''EXAMPLE CODE
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
			"""alert("Hello lol.")"""
		],singleAttributes=["defer"])
	])
	)
'''