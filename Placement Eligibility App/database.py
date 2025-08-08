import mysql.connector

class Database:
    def __init__(self,host,user,password,database):
        self.conn=mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor=self.conn.cursor(dictionary=True)
    
    def fetch_all_students(self):
        self.cursor.execute('select * from students')
        return self.cursor.fetchall()
    
    def close(self):
        self.cursor.close()
        self.conn.close()