import sqlite3

db = '/home/deekras/PythonEnv/PlayOutside/schools.db'

def get_db_connection():
    conn = sqlite3.connect(db)
    conn.text_factory = str
    return conn

code = 'z15154'
def o():
    conn = get_db_connection()
    statement = statement = """SELECT  latitude, longitude  FROM schools
                    WHERE url_code == '{}' """.format(code)
    row = conn.execute(statement)
    row = row.fetchone()
    print list(row)
    lat, lng = list(row)[0], list(row)[1]
    return lat,lng
 
o()