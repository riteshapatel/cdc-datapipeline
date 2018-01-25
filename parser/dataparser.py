# Copyright (c) 2017 by Mosaic ATM, Inc.  All rights reserved. 
# This file has been developed by Mosaic ATM under U.S. Federal  
# Government funding via CDC contract 200-2017-M-96110.  These 
# SBIR data are furnished with SBIR rights under Contract 
# No. 200-2017-M-96110.  For a period of 4 years, unless extended 
# in accordance with FAR 27.409(h), after acceptance of all items 
# to be delivered under this contract, the Government will use 
# these data for Government purposes only, and they shall not be 
# disclosed outside the Government (including disclosure for 
# procurement purposes) during such period without permission of 
# the Contractor, except that, subject to the foregoing use and 
# disclosure prohibitions, these data may be disclosed for use 
# by support Contractors.  After the protection period, the 
# Government has a paid-up license to use, and to authorize 
# others to use on its behalf, these data for Government 
# purposes, but is relieved of all disclosure prohibitions and 
# assumes no liability for unauthorized use of these data by 
# third parties.  This notice shall be affixed to any 
# reproductions of these data, in whole or in part.

from utils.config import readConfig
from pycorenlp import StanfordCoreNLP

import time
import psycopg2
import subprocess 
import json
import os, signal, glob

nlp = StanfordCoreNLP('http://localhost:9000')

class DataParser (object):
    def __init__(self):
        """
        Reads database config and opens a connection to database
        """
        self.start_time = time.time()
        self.params = readConfig(section='postgresql')
        self.openConnection()

        # start servers
        self.startServers()
        print('Starting servers...')
        time.sleep(25)
        print('Servers started successfully')

    def __del__(self):
        """
        clears connection
        """
        self.closeConnection()

    def openConnection(self):
        """
        opens a connection
        @return {Connection} database connection
        """
        self.conn = None
        try:
            self.conn = psycopg2.connect(**self.params)
        except:
            print("Could not connect to db")
        print("Connected to db")
        return self.conn
    
    def closeConnection(self):
        """
        closes connection if open
        """
        if self.conn is not None:
            self.conn.close()
            print("Db connection closed")    

    def startServers(self):
        """
        starts semafor and corenlp servers from respective directories, these servers will be
        destroyed by calling stopServers upon completion of data processing
        """
        projdir = os.getcwd()
        print(projdir)

        os.chdir('parser/corenlp')
        cwd = os.getcwd()
        print(cwd)
        self.nlp = subprocess.Popen('nohup java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000', shell=True, close_fds=True)

        os.chdir('../semafor')
        cwd = os.getcwd()
        print(cwd)

        self.semafor = subprocess.Popen('nohup java -Xms4g -Xmx4g -cp target/Semafor-3.0-alpha-04.jar edu.cmu.cs.lti.ark.fn.SemaforSocketServer model-dir:../models/semafor_malt_model_20121129 port:5000', shell=True, close_fds=True)
        os.chdir(projdir)

    def stopServers(self):
        """
        kills semafor and nlp servers
        """
        self.nlp.kill()
        self.semafor.kill()

    def getJson(self, row):
        """
        Feeds conll output to Semafor server and retrieves JSON in return. Updates database
        record with returned JSON.
        @param {Record} - row to be processed
        """
        postid = row[0]

        # feeds conll output and persists JSON in a local file. Must be streamed to a file, 
        # as the JSON returned by semafor is framed parse JSON per line which must be converted
        # into array of JSON objects
        conllfilename = '/tmp/conll/conll_' + repr(postid)
        jsonfile = open('/tmp/conll/' + repr(postid) + '.json', 'w')
        if os.path.exists(conllfilename):
            process = subprocess.Popen('cat ' + conllfilename + ' | nc localhost 5000', shell=True, stdout=jsonfile)
            process.wait()
            process.kill()     

        # read persisted JSON from local file system and append it to parsed array as a JSON
        # object.
        parsed = []
        with open('/tmp/conll/' + repr(postid) + '.json', 'r') as f:
            for line in f:
              parsed.append(json.loads(line.strip()))  
        f.close()

        # update curosr to persist JSON returned by semafor server. parsed array must be cast
        # as a JSONB during the update
        updcursor = self.conn.cursor()
        updcursor.execute('UPDATE public.semafor_test SET parsed_json = CAST(%s as JSONB) WHERE postid=%s', (json.dumps(parsed), postid))
        updated_rows = updcursor.rowcount 
        updcursor.close()

    def createConllFormat(self, row):
        """
        Creates a conll format file from a text file. Process uses CoreNLP and Semafor customized script.
        This file will be saved in a temporary location. 
        """
        # print post
        postid = row[0]
        post = row[1]
        
        # create files in a temporary location
        inputfile = '/tmp/txt/' + repr(postid) + '.txt'
        outputfile = '/tmp/out/' + repr(postid) + '.out'

        # opens a text file and adds a post read from the database
        file = open(inputfile, 'w')
        file.write(post)
        file.close()

        # replace linebreaks in a file
        with open(inputfile, 'r') as tmpfile:
            data = tmpfile.read().replace('\n', '')
        
        # tokenize as a json 
        json = nlp.annotate(data, properties = {
            'annotators': 'tokenize,ssplit',
            'outputFormat': 'json'
        })

        # create split text output 
        f = open(outputfile, 'w+')

        # print sentences on a separate line from json 
        for l in json['sentences']:
            start_offset = l['tokens'][0]['characterOffsetBegin']
            end_offset = l['tokens'][-1]['characterOffsetEnd']
            out_str = data[start_offset:end_offset]
            f.write(out_str + '\n')

        f.close()   
       
        # conll conversion (uses customized script in Semafor processor). 
        if os.path.exists(outputfile):
            process = subprocess.Popen('sh parser/semafor/bin/convertConll.sh ' + outputfile + ' /tmp/conll ' + repr(postid), shell=True)
            process.wait()
            process.kill()

    def prepareDirs(self):
        """
        creates temporary directories to hold various files created for parsing
        """
        # create temporary directory to hold text files 
        if not os.path.exists('/tmp/txt'):
            os.makedirs('/tmp/txt')

        if not os.path.exists('/tmp/out'):
            os.makedirs('/tmp/out')
                
        if not os.path.exists('/tmp/conll'):
            os.makedirs('/tmp/conll')

    def removeOlderFiles(self):
        """
        clear temporary directories before each run
        """
        filelist = glob.glob(os.path.join('/tmp/txt', '*.txt'))
        for f in filelist:
            os.remove(f)
        
        filelist = glob.glob(os.path.join('/tmp/out', '*.out'))
        for f in filelist:
            os.remove(f)

        filelist = glob.glob(os.path.join('/tmp/conll/*'))
        for f in filelist:
            os.remove(f)                

    def getDataFromDB(self, command):
        """
        read data from database (look into using server side cursors for larger datasets)
        """
        cursor = self.conn.cursor()
        rows_count = cursor.execute(command)

        # prepare temporary directions (if present clear content before each run)
        self.prepareDirs()  
        self.removeOlderFiles()

        # if valid cursor
        while True:
            rows = cursor.fetchall()
            # if no data return
            if not rows:
                break
            # loop rows
            for row in rows:
                # create a text file from post and save it in a temporary location 
                self.createConllFormat(row)
                self.getJson(row)

        # commit connection
        self.conn.commit()

        # calculate elapsed time
        elapsed_time = time.time() - self.start_time
        strtime = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        print('Processing time for 5 records: ' + strtime)

        # stop servers
        self.stopServers()