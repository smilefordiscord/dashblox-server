import os
import io
import boto3
from boto3.dynamodb.conditions import Attr
from flask import Flask, request
import decimal

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
            requestdata = request.get_data().decode('UTF-8')
            item = table.get_item(Key={'id': decimal.Decimal(requestdata)})
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
            searchquery = request.data.decode('UTF-8')
            response = table.scan(FilterExpression=Attr('title').contains(searchquery))
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

        response = table.update_item(
            Key={'id': 0},
            UpdateExpression="ADD #cnt :val",
            ExpressionAttributeNames={'#cnt': 'count'},
            ExpressionAttributeValues={':val': 1},
            ReturnValues="UPDATED_NEW"
        )
        
        newLevelId = response['Attributes']['count']
        
        data = request.get_json()

        response = table.put_item(
            Item={
                'id': newLevelId,
                'title': data["title"],
                'data': data["data"],
                'rating': 0,
                'timestamp': data["timestamp"],
            }
        )
        
        return "OK", 200
    else:
        return "Invalid method", 403

print("Starting server")

app.run(host='0.0.0.0', port=8080)