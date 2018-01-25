from datetime import datetime

import json
from db.db import Database 
from parser.dataparser import DataParser

def main():
    db = Database() 

    data = json.load(open('posts.json'))
    print('Clearing data...')
    db.clearTable()
    
    if (len(data) > 0):
        for obj in data:
            post = obj["post"]
            db.insertPost(post)

        parser = DataParser()
        parser.getDataFromDB('SELECT postid, post FROM public.post order by postid limit 5')

if __name__ == '__main__':
    main()