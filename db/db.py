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
        return self.conn;
    
    def closeConnection(self):
        if self.conn is not None:
            self.conn.close()
            print("Db connection closed")
            
    def readSql(self, command):
        try:
            cur = self.conn.cursor()
            cur.execute(command)
            value = cur.fetchall()
            cur.close()
            self.conn.commit()
            return value
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
            
    def executeSql(self, commands):
        try:
            cur = self.conn.cursor()
            for command in commands:
                cur.execute(command)
            cur.close()
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)

    def createTables(self):
        commands = (
            """
            CREATE TABLE IF NOT EXISTS Website(
                wid BIGSERIAL NOT NULL,
                url TEXT,
                PRIMARY KEY(wid)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS Forum(
                websiteId SERIAL NOT NULL references Website(wid) ON DELETE CASCADE,
                fid BIGSERIAL NOT NULL,
                title TEXT,
                PRIMARY KEY(fid)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS ForumTopic(
                forumId SERIAL NOT NULL references Forum(fid) ON DELETE CASCADE,
                tid BIGSERIAL NOT NULL,
                topic TEXT,
                PRIMARY KEY(tid)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS WebsiteUser(
                websiteId SERIAL NOT NULL references Website(wid) on DELETE CASCADE,
                uid BIGSERIAL NOT NULL,
                username TEXT,
                gender TEXT,
                age TEXT,
                maritalStatus TEXT,
                parentalStatus TEXT,
                PRIMARY KEY(uid)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS Post(
                topicId SERIAL NOT NULL references ForumTopic(tid) ON DELETE CASCADE,
                userId SERIAL NOT NULL references WebsiteUser(uid) ON DELETE CASCADE,
                postId BIGSERIAL NOT NULL,
                post TEXT, 
                posttime TIMESTAMP WITH TIME ZONE,
                PRIMARY KEY(topicId, userId, postId)
            )
            """)
        self.executeSql(commands)
        
    def deleteTables(self):
        commands = (
            """
            DROP TABLE IF EXISTS Post CASCADE
            """,
            """
            DROP TABLE IF EXISTS WebsiteUser CASCADE
            """,
            """
            DROP TABLE IF EXISTS ForumTopic CASCADE
            """,
            """
            DROP TABLE IF EXISTS Forum CASCADE
            """,
            """
            DROP TABLE IF EXISTS Website CASCADE
            """) 
        self.executeSql(commands)
        
    def insertWebsite(self, url):
        sql = """INSERT INTO Website(url)
                    VALUES(%s) RETURNING wid;"""
        website_id = None
        try:
            cur = self.conn.cursor()
            cur.execute(sql , (url,))
            website_id = cur.fetchone()[0]
            self.conn.commit()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print (error)
        return website_id

    def insertForum(self, websiteId, forumTitle):
        sql = """INSERT INTO Forum (websiteid, title)
                VALUES(%s, %s) RETURNING fid;"""
        forum_id = None
        try:
            cur = self.conn.cursor()
            cur.execute(sql, (websiteId, forumTitle,))
            forum_id = cur.fetchone()[0]
            self.conn.commit()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print (error)
        return forum_id
    
    def insertForumTopic(self, forumId, topicTitle):
        sql = """INSERT INTO ForumTopic (forumid, topic)
                VALUES(%s, %s) RETURNING tid;"""
        topic_id = None
        try:
            cur = self.conn.cursor()
            cur.execute(sql, (forumId, topicTitle,))
            topic_id = cur.fetchone()[0]
            self.conn.commit()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print (error)
        return topic_id
    
    def insertWebsiteUser(self, websiteId, userName):
        sql = """INSERT INTO WebsiteUser (websiteid, username)
                VALUES(%s, %s) RETURNING uid;"""
        user_id = None
        try:
            cur = self.conn.cursor()
            cur.execute(sql, (websiteId, userName,))
            user_id = cur.fetchone()[0]
            self.conn.commit()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print (error)
        return user_id
    
    def insertPost(self, topicId, userId, postText, postDate):
        sql = """INSERT INTO Post (topicid, userid, post, posttime)
                VALUES(%s, %s, %s, %s);"""
        try:
            cur = self.conn.cursor()
            cur.execute(sql, (topicId, userId, postText, postDate,))
            self.conn.commit()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print (error)
            
    def insertProcessedPost(self, postText, postTopic):
        sql = """INSERT INTO processedpost (post, topic)
                VALUES(%s, %s);"""
        try:
            cur = self.conn.cursor()
            cur.execute(sql, (postText, postTopic,))
            self.conn.commit()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print (error)
            
    def createProcessedTable(self, csvPath):
        #self.executeSql(tablecommand)
        #self.conn.commit()
                
        try:
            cur = self.conn.cursor()

            command1 = """drop table if exists processedpost"""
                        
            tablecommand = """
                CREATE TABLE IF NOT EXISTS processedpost(
                    post TEXT,
                    classification TEXT,
                    postid bigint,
                    userid bigint
                )
                """      
            cur.execute(command1)
            cur.execute(tablecommand)
            #cur.close()
            self.conn.commit()
                    
            #conn = psycopg2.connect("host=localhost dbname=postgres user=postgres")
            with open(csvPath, 'r') as f:
                # Notice that we don't need the `csv` module.
                next(f)  # Skip the header row.
                cur.copy_from(f, 'processedpost', sep=',')
            self.conn.commit()
            cur.close()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
         
        
    def selectWebsiteId(self, website):
        sql = """SELECT wid from Website where url=%s"""

        wid = None
        try:
            cur = self.conn.cursor()
            cur.execute(sql, (website,))
            f = cur.fetchone()
            if f is not None:
                wid = f[0]                
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print (error)
        return wid
    
    def selectForumId(self, forum, websiteId):
        sql = """SELECT fid from Forum where title=%s and websiteid=%s"""

        fid = None
        try:
            cur = self.conn.cursor()
            cur.execute(sql, (forum, websiteId,))
            f = cur.fetchone()
            if f is not None:
                fid = f[0]                
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print (error)
        return fid
    
    def selectTopicId(self, topic, forumId):
        sql = """SELECT tid from ForumTopic where topic=%s and forumid=%s"""

        tid = None
        try:
            cur = self.conn.cursor()
            cur.execute(sql, (topic, forumId,))
            f = cur.fetchone()
            if f is not None:
                tid = f[0]                
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print (error)
        return tid
    
    def selectUserId(self, userName, websiteId):
        sql = """SELECT uid from WebsiteUser where username=%s and websiteid=%s"""

        uid = None
        try:
            cur = self.conn.cursor()
            cur.execute(sql, (userName, websiteId,))
            f = cur.fetchone()
            if f is not None:
                uid = f[0]                
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print (error)
        return uid
