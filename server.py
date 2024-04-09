import psycopg2
import time
from flask import Flask, request
import json
from json.encoder import JSONEncoder
import os
from flask import Flask, request

app = Flask(__name__)

secret = os.environ.get('secret')

conn = psycopg2.connect(
    host=os.environ.get('host'),
    port="5432",
    dbname=os.environ.get('dbname'),
    user=os.environ.get('user'),
    password=secret,
)

@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        return "hello :)", 200
    else:
        return "Invalid method", 403

@app.route('/execute', methods=['POST'])
def execute():
    if request.method == 'POST':
        data = request.get_json()
        if data["secret"] != secret:
            return "Invalid secret", 403
        
        cursor = conn.cursor()
        try:
            cursor.execute(data["request"])
            returnLevels =  JSONEncoder().encode(cursor.fetchall())
            cursor.close()
            return returnLevels, 200
        except:
            cursor.close()
            return "Request failed", 404
    else:
        return "Invalid method", 403

@app.route('/last-key', methods=['POST'])
def getLastkey():
    if request.method == 'POST':
        data = request.get_json()
        if data["secret"] != secret:
            return "Invalid secret", 403
        
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM public.levels ORDER BY id DESC LIMIT 1")
            returnLevels =  JSONEncoder().encode(cursor.fetchone())
            
            cursor.close()
            return returnLevels, 200
        except:
            cursor.close()
            return "Request failed", 404
    else:
        return "Invalid method", 403

@app.route('/get-key', methods=['POST'])
def getkey():
    if request.method == 'POST':
        data = request.get_json()
        if data["secret"] != secret:
            return "Invalid secret", 403
        
        cursor = conn.cursor()
        try:
            id: int = 17
            cursor.execute("SELECT * FROM public.levels WHERE id = %(id)s", {'id':id})
            returnLevels =  JSONEncoder().encode(cursor.fetchone())

            cursor.close()
            return returnLevels, 200
        except:
            cursor.close()
            return "Request failed", 404
    else:
        return "Invalid method", 403

@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        data = request.get_json()
        if data["secret"] != secret:
            return "Invalid secret", 403
        
        cursor = conn.cursor()
        try:
            
            col = data["attribute"]
            substring = data["query"]
            rated = data["rated"]
            if rated == True:
                cursor.execute("SELECT * FROM public.levels WHERE %(col)s ILIKE %(sub)s AND difficulty > 0", {"col":col, "sub": '%'+substring+'%'})
            else:
                cursor.execute("SELECT * FROM public.levels WHERE %(col)s ILIKE %(sub)s", {"col":col, "sub": '%'+substring+'%'})
            
            returnLevels = []
            for item in cursor:
                returnLevels.append(JSONEncoder().encode(item))

            cursor.close()
            return returnLevels, 200
        except:
            cursor.close()
            return "Request failed", 404
    else:
        return "Invalid method", 403

@app.route('/add-level', methods=['POST'])
def addlevel():
    if request.method == 'POST':
        cursor = conn.cursor()

        data = request.get_json()
        if data["secret"] != secret:
            cursor.close()
            return "Invalid secret", 403
        
        title = data["title"]
        desc = data["desc"]
        lvldata = data["data"]
        owner = data["owner"]
        difficulty = data["difficulty"]
        timestamp = data["timestamp"]
        cursor.execute("INSERT INTO public.levels (title, description, data, owner, difficulty, rating, timestamp) VALUES (%(title)s, %(desc)s, %(data)s, %(owner)s, %(difficulty)s, %(rating)s, %(timestamp)s);", {"title":title,"desc":desc,"data":lvldata,"owner":owner,"difficulty":difficulty,"rating":0,"timestamp":timestamp})
        
        conn.commit()
        cursor.close()
        return "OK", 200
    else:
        return "Invalid method", 403

@app.route('/remove-level', methods=['POST'])
def removeLevel():
    if request.method == 'POST':
        data = request.get_json()
        if data["secret"] != secret:
            return "Invalid secret", 403
        
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM public.levels WHERE id = %(id)s;", {"id":data["id"]})
            conn.commit()
            cursor.close()
            return "OK", 200
        except:
            cursor.close()
            return "Request failed", 404
    else:
        return "Invalid method", 403

@app.route('/glro', methods=['POST'])
def glro():
    if request.method == 'POST':
        data = request.get_json()
        
        if data["secret"] != secret:
            return "Invalid secret", 403
        
        cursor = conn.cursor()
        try:
            rated = data["rated"]
            if rated == True:
                cursor.execute("SELECT * FROM public.levels WHERE id <= %(id)s AND difficulty > 0 ORDER BY id DESC LIMIT %(length)s", {"id":data["id"],"length":data["length"]})
            else:
                cursor.execute("SELECT * FROM public.levels WHERE id <= %(id)s ORDER BY id DESC LIMIT %(length)s", {"id":data["id"],"length":data["length"]})
            
            returnLevels = []
            for item in cursor:
                returnLevels.append(JSONEncoder().encode(item))
            
            cursor.close()
            return returnLevels, 200
        except:
            cursor.close()
            return "Request failed", 404
    else:
        return "Invalid method", 403

print("Starting server")

app.run(host='0.0.0.0', port=8080)