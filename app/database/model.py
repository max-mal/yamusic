import json
from .main import db
from .query import Query

class Model:
	def __init__(self, obj={}, fetched = False):	
		self._is_loaded = fetched		
		for key, value in obj.items():
			setattr(self, key, value)
		if not self._is_loaded:
			self.load()

		self.defaultAttributes()
		self.boot()

	def defaultAttributes(self):
		pass

	def load(self):
		if (not hasattr(self, 'id')):
			return

		found = self.__class__.query(' where id = ?', [self.id])
		if (len(found) == 0):
			return

		fetchedDict = found[0].toDict()

		for key in fetchedDict:
			if (not hasattr(self, key)):
				setattr(self, key, fetchedDict[key])

	def boot(self):
		pass

	def getTable(self):
		return '__table__'

	def toDict(self):
		obj = {}
		for attribute in self.__dict__.keys():
			if attribute[:1] != '_':
				value = getattr(self, attribute)
				if not callable(value):		           
				   obj[attribute] = value
		return obj

	def store(self, commit=True):
		Query.insert(db, self.getTable(), self.toDict())
		if (commit):
			db.commit()

	def afterFetch(self):
		pass
	
	@classmethod
	def query(cls, query = '', params = []):
		example = cls()
		c = db.cursor()
		data = []		
		for row in c.execute("SELECT * FROM {table} {query};".format(table=example.getTable(), query=query), params):						
			c = cls(row, fetched=True)
			c.afterFetch()
			data.append(c)

		return data

	def __str__(self):
		return json.dumps(self.toDict(), ensure_ascii=False)

