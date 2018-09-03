#!/usr/bin/python

import os
import sqlite3
import sys
import time

db = sqlite3.connect('/var/lib/zon-api/data.db')

if len(sys.argv) < 3:
    print('Usage: %s "Firstname Lastname" email@example.com' % sys.argv[0])
    print('\nLast keys:')
    query = 'SELECT * FROM client ORDER by reset DESC'
    for client in db.execute(query):
        print(u'{0}: "{2}" {3}'.format(*client).encode('utf8'))
    sys.exit(1)

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
