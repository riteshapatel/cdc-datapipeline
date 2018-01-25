import psycopg2

from utils.config import readConfig


class Database (object):
    def __init__(self):
        self.params = readConfig(section='postgresql')
        self.openConnection()
    
    def __del__(self):
        self.closeConnection()

    def openConnection(self):
        self.conn = None
        try:
            self.conn = psycopg2.connect(**self.params)
        except:
            print("Could not connect to db")
        print("Connected to db")
        return self.conn
    
    def closeConnection(self):
        if self.conn is not None:
            self.conn.close()
            print("Db connection closed")

    def insertPost(self, post):
        sql = """INSERT INTO public.post(post) VALUES(%s) RETURNING postid;"""
        postid = None
        try:
            cur = self.conn.cursor()
            cur.execute(sql, (post,))
            postid = cur.fetchone()[0]
            self.conn.commit()
            cur.close() 
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)   
        return postid         
    
    def clearTable(self):
        sql = """DELETE FROM public.post"""
        print(sql)
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
            cur.close() 
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)        
        