from .main import db

class Query:
	@staticmethod
	def insert(db, table, obj):
		c = db.cursor()
		fieldNames = []
		fieldValues = []
		for key in obj:
			fieldNames.append(key),
			fieldValues.append(
				obj[key]
			),
		query = 'INSERT OR REPLACE INTO {table} ({fields}) VALUES ({values});'.format(
			table=table,
			fields=','.join(fieldNames),
			values=', '.join(list('?'*len(fieldNames))),
		)
		# print("SQL: " + query)
		c.execute(query, fieldValues)		