#!/usr/bin/python
# -*- coding: utf-8 -*-

import psycopg2
import sys


con = None


     
con = psycopg2.connect(database='test2') 
cur = con.cursor()
cur.execute('SELECT version()')          
ver = cur.fetchone()
print ver 
con.close()   

   

# except psycopg2.DatabaseError, e:
#     print 'Error %s' % e    
#     sys.exit(1)
    
    
# finally:
    
#     if con:
#         con.close()

# con = psycopg2.connect(database='test2') 
# cur = con.cursor()
# cur.execute("CREATE TABLE pg_equipment (\
#     equip_id serial PRIMARY KEY,\
#     type varchar (50) NOT NULL,\
#     color varchar (25) NOT NULL,\
#     location varchar(25) check (location in \
#         ('north', 'south', 'west', 'east', 'northeast', 'southeast', 'southwest', 'northwest')),\
#     install_date date);")
# print 'table'
# con.commit()
# con.close()

con = psycopg2.connect(database='test2') 
cur = con.cursor()
cur.execute("ALTER TABLE pg_equipment ADD COLUMN functioning bool;")
con.close()

query = "INSERT INTO pg_equipment (equip_id, type, color, location, install_date) VALUES (%s,%s,%s,%s,%s)"
new_data = (123, "full", "red", "east", '1/12/56')
select_query = "SELECT * FROM pg_equipment"

con = psycopg2.connect(database='test2') 
cur = con.cursor()
cur.execute(select_query)
rows = cur.fetchall()

for row in rows:
    print row
# cur.execute(query, new_data)
# con.commit()
