import sqlite3
from multiprocessing.connection import Connection

connection = sqlite3.Connection('example.db')

cursor = connection.cursor()

cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS employees(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME TEXT NOT NULL,
    POSITION TEXT NOT NULL,
    DEPARTAMENT TEXT NOT NULL,
    SALARY REAL
    )
    
    '''
)
connection.commit()


query = '''
INSERT INTO EMPLOYEES (NAME,POSITION,DEPARTAMENT,SALARY) VALUES(?,?,?,?)

'''

cursor.execute(query,('john','software engineer','it',7000.00))
connection.commit()


cursor.execute('SELECT * FROM EMPLOYEES ')

connection.commit()

rows = cursor.fetchall()

for row in rows:
    print(row)


print("UPDATED INFO\n\n")

update_query='''
UPDATE EMPLOYEES SET SALARY = ? WHERE ID = ?
'''

cursor.execute(update_query,(75000,1))

connection.commit()


cursor.execute('SELECT * FROM EMPLOYEES ')

connection.commit()

rows = cursor.fetchall()

for row in rows:
    print(row)