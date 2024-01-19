#!/usr/bin/python
# display sqlite database

import sqlite3
from datetime import datetime as dt
import json
import fileinput

sqlite_file = '/home/freebox/temperature/weatherstation.sqlite'    # name of the sqlite database file
table_name = 'data'   # name of the table to be created

# test read back from database
conn = sqlite3.connect(sqlite_file)
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute("SELECT * FROM {tn} ".\
        format(tn=table_name))
rows = c.fetchall()
for row in rows:
    print(row)
conn.close()