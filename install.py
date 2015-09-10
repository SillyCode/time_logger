#!/usr/bin/python
#-*- coding: utf-8 -*-

from __future__ import print_function
import MySQLdb as mdb
import shutil
import sys
import os

_con = None
# Change those values and re-run the install script to create table in database
# Rememeber to change them also in record.py and uninstall.py files
db_username = ''
db_password = ''

# TODO
# Define prequisits as mysql/mariadb and python. (check is services exist)
# Change the conf file to execute the global record file
# TODO
#- manually insert/update record or remove record by date
#- make method to calculate spend hours after any manual update

def mysql_connect():
	global _con
	global db_username
	global db_password
	if _con is None:
		try:
			_con = mdb.connect(
				user = db_username,
				passwd = db_password,
				host = 'localhost',
				db = 'time_recorder')
			return _con
		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0], e.args[1])
			sys.exit(1)

def install(cursor):
	try:
		cursor.execute("""drop table if exists `record`""")
		cursor.execute("""create table `record` (
			`record_id` int unsigned not null auto_increment,
			`start_time` timestamp DEFAULT '0000-00-00 00:00:00',
			`end_time` timestamp DEFAULT '0000-00-00 00:00:00',
			`seconds_spent` int(10)
			primary key(`record_id`))""") # record current time
		_con.commit()
	except mdb.Error, e:
		if _con:
			_con.rollback()
	except mdb.Warning, e:
		print "Warning %d %s " % (e.args[0] , e.args[1])

exit

# NOTE: possible overwrites files
# TODO: create unique filename in init
os.symlink(os.getcwd()+'/record.py','/usr/local/bin/record')
shutil.copyfile(os.getcwd()+"/time_logger.conf", '/etc/init/time_logger.conf'); # move conf file to run script on startup/shutdown

db_username = raw_input('Please provide a database user name for time_logging (can be modified later): ')
db_password = raw_input('Please provide a database user password for time_logging (can be modified later): ')
cursor = mysql_connect().cursor(mdb.cursors.DictCursor)
install(cursor)
_con.close()
