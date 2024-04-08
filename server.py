import json.tool
import os
import io
import boto3
from boto3.dynamodb.conditions import Attr
from flask import Flask, request
import decimal
import json

app = Flask(__name__)

keyid = os.environ.get('keyid')
secret = os.environ.get('secret')
region = "us-west-2"

client = boto3.Session(
    aws_access_key_id=keyid,
    aws_secret_access_key=secret,
    region_name=region
)

dynamodb = client.resource('dynamodb')
table = dynamodb.Table('levels')

@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        return "hello :)", 200
    else:
        return "Invalid method", 403

@app.route('/get-key', methods=['POST'])
def getkey():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            if data["secret"] != secret:
                return "Invalid secret", 403
            
            item = table.get_item(Key={'id': decimal.Decimal(data["key"])})
            data = item["Item"]
            
            return data, 200
        except:
            return "Request failed", 404
    else:
        return "Invalid method", 403

@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            if data["secret"] != secret:
                return "Invalid secret", 403
            
            response = None

            if data["condition"] == "eq":
                response = table.scan(FilterExpression=Attr(data["attribute"]).eq(data["query"]))
            elif data["condition"] == "cont":
                response = table.scan(FilterExpression=Attr(data["attribute"]).contains(data["query"]))
            
            if response == None:
                return "No item", 403
            
            data = response['Items']
            
            while 'LastEvaluatedKey' in response:
                response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                data.extend(response['Items'])
            
            return data, 200
        except:
            return "Request failed", 404
    else:
        return "Invalid method", 403

@app.route('/add-level', methods=['POST'])
def addlevel():
    if request.method == 'POST':

        data = request.get_json()
        
        if data["secret"] != secret:
            return "Invalid secret", 403
        
        response = table.update_item(
            Key={'id': 0},
            UpdateExpression="ADD #cnt :val",
            ExpressionAttributeNames={'#cnt': 'count'},
            ExpressionAttributeValues={':val': 1},
            ReturnValues="UPDATED_NEW"
        )
        
        newLevelId = response['Attributes']['count']
        
        response = table.put_item(
            Item={
                'id': newLevelId,
                'title': data["title"],
                'data': data["data"],
                'owner': data["owner"],
                'timestamp': data["timestamp"],
                'rating': 0,
            }
        )
        
        return "OK", 200
    else:
        return "Invalid method", 403

@app.route('/remove-level', methods=['POST'])
def removeLevel():
    if request.method == 'POST':
        data = request.get_json()
        
        if data["secret"] != secret:
            return "Invalid secret", 403

        response = table.delete_item(
            Key={'id': data["id"]},
            ConditionExpression="attribute_exists (id)",
        )

        return "OK", 200
    else:
        return "Invalid method", 403

@app.route('/glro', methods=['POST'])
def glro():
    if request.method == 'POST':
        data = request.get_json()
        
        if data["secret"] != secret:
            return "Invalid secret", 403
        
        levels = []
        
        i = 0
        
        # while len(levels) < 10 or decimal.Decimal(data["key"]) - i < 1:
        while i < 10:
            try:
                item = table.get_item(Key={'id': decimal.Decimal(data["key"]) - i})
                data = json.loads(item["Item"])
                levels = levels.append(data)
                i += 1
            except:
                i += 1
        
        levels = json.dumps(levels)
        
        return levels, 200
    else:
        return "Invalid method", 403

print("Starting server")

app.run(host='0.0.0.0', port=8080)