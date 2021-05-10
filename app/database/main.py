import sqlite3
import os
import shutil

def dict_factory(cursor, row):
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d

if not os.path.isfile(os.getcwd() + "/storage.db"):
	shutil.copy(os.getcwd() + "/storage.db.sample", os.getcwd() + "/storage.db")

db = sqlite3.connect('storage.db', check_same_thread=False)
db.row_factory = dict_factory
