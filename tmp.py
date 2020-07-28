import sqlite3 as sql

with sql.connect('database.db') as con:
    cursor = con.cursor()
    cursor.execute('''delete from Payments''')
    # print(cursor.fetchall())
    con.commit()
