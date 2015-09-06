#!/usr/bin/python
#-*- coding: utf-8 -*-

import MySQLdb as mdb
import calendar
import datetime
import getopt
import time
import re
import sys

_con = None
# Change those values and re-run the install script to create table in database
# Rememeber to change them also in install.py and uninstall.py files
db_username = ''
db_password = ''

def mysql_connect():
	#print 'connecting to database'
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

def record(cursor):
	print 'recording'

	ts = int(time.time())
	stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') # format time to timestamp
	try:
		cursor.execute('select count(*) as count from `record`')
		_con.commit()
		row = cursor.fetchone()

		if row['count'] >= 0: #table exists
			if row['count'] > 0: #table has at least one record
				cursor.execute('select `record_id`,`start_time` from `record` order by `record_id` desc limit 1')
				_con.commit()
				row = cursor.fetchone()

				current_date = time.strftime("%Y-%m-%d")
				retrieved_date = str(row['start_time'].date())

				if retrieved_date == current_date:
					#print 'match' #update the end_time
					cursor.execute('update `record` set `end_time` = %s where `record_id` = %s and `end_time` = "0000-00-00 00:00:00"', (stamp, row['record_id']))
					cursor.execute('update `record` set `seconds_spent` = (select UNIX_TIMESTAMP(`end_time`)-UNIX_TIMESTAMP(`start_time`)) where `record_id` = %s', row['record_id']);
					_con.commit()
				else:
					#print 'not match' #insert new record updating the start_time
					cursor.execute('insert into `record` (`start_time`) values (%s)', (stamp))
					_con.commit()
			else: #table has not records
				print 'clean table'
				cursor.execute('insert into `record` (`start_time`) values (%s)', (stamp))
				_con.commit()
		else:
			raise Exception('Table record not exists','run install script')
	except mdb.Error, e:
		print e.args
		if _con:
			_con.rollback()

def working_days():
	days = 0
	now = datetime.date.today()
	cal = calendar.Calendar()
	for week in cal.monthdayscalendar(now.year, now.month):
		for i, day in enumerate(week):
			if day == 0 or i == 4 or i == 5: # if Fri or Sat
				continue
			days += 1
	print "Wroking days this month: " + str(days)
	print "Working hours required this month: " + str(days * 9) # 9 working hours
cursor = mysql_connect().cursor(mdb.cursors.DictCursor)

try:
	optlist, args = getopt.getopt(sys.argv[1:], 'lts', ['list', 'log', 'last', 'table'])
	if not optlist: # no options specified
		record(cursor)
	else:
		for opt, arg in optlist:
			if opt in ('-l', '--log'):
				cursor.execute("""
						select count(1) as days,
						sum(`seconds_spent`) as spent
					from `record`
					where month(`start_time`) = month(curdate())
				""")
				_con.commit()
				row = cursor.fetchone()
				working_days() # Calculate working days in a month

				cursor.execute("""
						select TIME_TO_SEC(timediff(curtime(), time(`start_time`))) as `time`
					from `record`
					where `end_time` = '0000-00-00 00:00:00'
					order by `record_id` desc limit 1
				""")
				_con.commit()
				date = cursor.fetchone()
				today_hours = 0.0
				if date:
					today_hours = float(date['time']/3600.00) # Today's working hours
				working_hours = float(row['spent']/3600) + today_hours # Working hours until including today
				print ("Hours spent this month: %.2f" % working_hours)
				print "Working hours up including current day: " + str(9 * row['days']) + "\n"
				if working_hours > (9*row['days']):
					print "\033[92m" # Color stdout output GREEN
					print ("You are %.2f hours AHEAD" % (working_hours - (9 * row['days'])))
				elif working_hours < (9*row['days']):
					print "\033[91m" # Color stdout output RED
					print ("You are %.2f hours BEHIND" % ((9 * row['days']) - working_hours))
				else:
					print ("You are spot on working hours")
			elif opt in ('-t', '--table'):
				cursor.execute('select `start_time`, `end_time`, `seconds_spent` as hours_spent from `record` where month(`start_time`) = month(curdate())')
				_con.commit()
				row = cursor.fetchone()

				if cursor.rowcount > 0:
					string = "Start Date\t\tEnd Date\t\tHours Spent"
					underline = "-"
					print (string)
					print (underline * (len(string) + 26))
					while row is not None:
						if row['hours_spent'] == None:
							row['hours_spent'] = 0
						print ("%s\t|%s\t|%.2f" % (row['start_time'], row['end_time'], float(row['hours_spent'])/3600))
						row = cursor.fetchone()
			elif opt in ('--last'):
				ans = raw_input('Are you sure you want to delete the last record [y/n]: ')
				if ans in ('y', 'Y'):
					cursor.execute('delete from `record` order by `record_id` desc limit 1')
					_con.commit()
					print "Last record was deleted"
				else:
					print "Action aborted"
			else:
				print "Type record.py -h for help"

except getopt.GetoptError:
	print "Time logger manual:\n"
	print "-l| --log to view summary of working hours log"
	print "-t| --table to view all records in database"
	print "--last to remove the last time record"
	sys.exit(1)

_con.close()
