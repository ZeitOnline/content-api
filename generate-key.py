#!/usr/bin/python

import os
import sqlite3
import sys
import time

if len(sys.argv) < 3:
    raise ValueError('Usage: %s "Firstnam Lastname" email@example.com' % sys.argv[0])

db = sqlite3.connect('/var/lib/zon-api/data.db')
api_key = str(os.urandom(26).encode('hex'))
tier = 'free'
name = sys.argv[1]
email = sys.argv[2]
requests = 0
reset = int(time.time())
query = 'INSERT INTO client VALUES (?, ?, ?, ?, ?, ?)'
db.execute(query, (api_key, tier, name, email, requests, reset))
db.commit()
db.close()
print api_key
