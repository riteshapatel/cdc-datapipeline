from datetime import datetime

import json
import jsonlines
from db.db import Database 
from parser.dataparser import DataParser

def main():
    db = Database() 

    # data = json.load(open('posts.json'))
    print('Clearing data...')
    #db.clearTable()
    
    # if (len(data) > 0):
    #     for obj in data:
    #         post = obj["post"]
    #         db.insertPost(post)

    print(str(datetime.now()))
    db = Database()
    with jsonlines.open('smaller.jl') as reader:
        for obj in reader:
            website = obj.get("website")
            date = obj.get("date")
            if date is not None:
                if 'PM 0' in date:
                    date = date.replace('PM 0', 'PM +0')
                elif 'AM 0' in date:
                    date = date.replace('AM 0', 'AM +0')
            forum = obj.get("forum")
            user = obj.get("user")
            title = obj.get("title")
            post = obj.get("post")
            wid = db.selectWebsiteId(website)
            if wid is None:
                wid = db.insertWebsite(website)
            fid = db.selectForumId(forum, wid)
            if fid is None:
                fid = db.insertForum(wid, forum)
            tid = db.selectTopicId(title, fid)
            if tid is None:
                tid = db.insertForumTopic(fid, title)
            uid = db.selectUserId(user, wid)
            if uid is None:
                uid = db.insertWebsiteUser(wid, user)
            db.insertPost(tid, uid, post, date)

    print(str(datetime.now()))
    
    parser = DataParser()
    parser.getDataFromDB('SELECT postid, post FROM public.post order by postid limit 5')

if __name__ == '__main__':
    main()