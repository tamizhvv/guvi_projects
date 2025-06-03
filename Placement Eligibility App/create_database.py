import mysql.connector

connection=mysql.connector.connect(
    host='localhost',
    user='root',
    password='root'
)

cursor=connection.cursor()

cursor.execute(
    'create database if not exists placement_app'
)

print('Database created successfully')

cursor.close()
connection.close()