import psycopg2
import time
from flask import Flask, request
import json
from json.encoder import JSONEncoder
from flask import Flask, request
import logging
import os
from psycopg2 import sql

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

secret = os.environ.get('secret')
conn = psycopg2.connect(
    host=os.environ.get('host2'),
    port="25060",
    dbname=os.environ.get('dbname2'),
    user=os.environ.get('user2'),
    password=os.environ.get('password2'),
    sslmode="require"
)

def logInfo(text):
    print(text)

def logWarn(text):
    print("\033[93m {}\033[00m".format(text))

@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        return "hello :)", 200
    else:
        return "Invalid method", 403

#TODO: this needs to die
@app.route('/execute', methods=['POST'])
def execute():
    if request.method != 'POST':
        logWarn("/execute 403")
        return "Invalid method", 403
    
    data = request.get_json()
    if data is None:
        return "Invalid", 403
    if data["secret"] != secret:
        return "Invalid secret", 403
    
    sql = data["request"]

    cursor = conn.cursor()
    try:
        returnLevels = {}
        try:
            cursor.execute(sql)
            returnLevels =  JSONEncoder().encode(cursor.fetchall())
        except:
            returnLevels = ""
        conn.commit()
        cursor.close()
        logInfo("/execute 200 - " + sql)
        return returnLevels, 200
    except:
        conn.commit()
        cursor.close()
        logWarn("/execute 500 - " + sql)
        return "Request failed", 500

@app.route('/add-level', methods=['POST'])
def addlevel():
    if request.method != 'POST':
        logWarn("/add-level 403")
        return "Invalid method", 403
    
    data = request.get_json()
    if data is None:
        return "Invalid", 403
    if data["secret"] != secret:
        cursor.close()
        return "Invalid secret", 403
        
    cursor = conn.cursor()

    try:
        title = data["title"]
        desc = data["desc"]
        lvldata = data["data"]
        owner = data["owner"]
        difficulty = data["difficulty"]
        timestamp = data["timestamp"]
        cursor.execute("INSERT INTO public.levels (title, description, data, owner, difficulty, rating, timestamp) VALUES (%(title)s, %(desc)s, %(data)s, %(owner)s, %(difficulty)s, %(rating)s, %(timestamp)s);", {"title":title,"desc":desc,"data":lvldata,"owner":owner,"difficulty":difficulty,"rating":0,"timestamp":timestamp})
        
        conn.commit()
        cursor.close()
        logInfo("/add-level 200")
        return "OK", 200
    except:
        cursor.close()
        logWarn("/add-level 500")
        return "Upload failed", 500

@app.route('/db2-maxlvl', methods=['POST'])
def db2get():
    if request.method != 'POST':
        return "Invalid method", 403
    
    data = request.get_json()
    if data == None:
        return "Invalid", 403
    if data["secret"] != secret:
        return "Invalid secret", 403
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM public.levels ORDER BY id DESC LIMIT 1")
        returnLevels =  JSONEncoder().encode(cursor.fetchone())
        cursor.close()
        logInfo("/db2-maxlvl 200")
        return returnLevels, 200
    except:
        cursor.close()
        logWarn("/db2-maxlvl 500")
        return "Request failed", 500

@app.route('/db2-search', methods=['POST'])
def db2search():
    if request.method != 'POST':
        return "Invalid method", 403
    
    data = request.get_json()
    if data is None:
        return "Invalid", 403
    if data.get("secret") != secret:
        return "Invalid secret", 403
    
    searchText = f"%{data['searchText']}%"
    sortType = data["sortType"]
    max = data["max"]

    cursor = conn.cursor()
    try:
        if max > 0:
            query = sql.SQL("""
                SELECT * FROM public.levels 
                WHERE {0} < %s AND title ILIKE %s 
                ORDER BY {0} DESC 
                LIMIT 10
            """).format(sql.Identifier(sortType))
            
            cursor.execute(query, (max, searchText))
        else:
            query = sql.SQL("""
                SELECT * FROM public.levels 
                WHERE title ILIKE %s 
                ORDER BY {} DESC 
                LIMIT 10
            """).format(sql.Identifier(sortType))
            
            cursor.execute(query, (searchText,))

        returnLevels = JSONEncoder().encode(cursor.fetchall())
        cursor.close()
        logInfo("/db2-search 200 - " + searchText)
        return returnLevels, 200
    except:
        cursor.close()
        logWarn("/db2-search 500")
        return "Request failed", 500

@app.route('/db2-recent', methods=['POST'])
def db2recent():
    if request.method != 'POST':
        return "Invalid method", 403
    
    data = request.get_json()
    if data is None:
        return "Invalid", 403
    if data.get("secret") != secret:
        return "Invalid secret", 403
    
    max = data["max"]

    cursor = conn.cursor()
    try:
        if max > 0:
            query = sql.SQL("""
                SELECT * FROM public.levels 
                WHERE id < %s 
                ORDER BY id DESC 
                LIMIT 10
            """)
            cursor.execute(query, (max, ))
        else:
            query = sql.SQL("""
                SELECT * FROM public.levels 
                ORDER BY id DESC 
                LIMIT 10
            """)
            cursor.execute(query)

        returnLevels = JSONEncoder().encode(cursor.fetchall())
        cursor.close()
        logInfo("/db2-recent 200")
        return returnLevels, 200
    except:
        cursor.close()
        logWarn("/db2-recent 500")
        return "Request failed", 500

print("Starting server")

app.run(host='0.0.0.0', port=8080)