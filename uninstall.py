#!/usr/bin/python
#-*- coding: utf-8 -*-

import MySQLdb as mdb
import sys

_con = None
# Change those values and re-run the install script to create table in database
# Rememeber to change them also in record.py and install.py files
db_username = ''
db_password = ''

def mysql_connect():
	global _con
	if _con is None:
		try:
			_con = mdb.connect(
				user = db_username,
				passwd = db_password,
				host = 'localhost',
				db = 'time_recorder')
			return _con
		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0], e.args[1])
			sys.exit(1)

def uninstall(cursor):
	try:
		cursor.execute("""drop table if exists record""")
		_con.commit()
	except mdb.Error, e:
		if _con:
			_con.rollback()
	except mdb.Warning, e:
		print "Warning %d %s " % (e.args[0] , e.args[1])

cursor = mysql_connect().cursor(mdb.cursors.DictCursor)
uninstall(cursor)
_con.close()

os.remove('/etc/init/time_logger.conf')
os.unlink('/usr/local/bin/record')
