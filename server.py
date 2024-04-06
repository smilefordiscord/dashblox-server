# import os
# import http.server
# import socketserver

# from http import HTTPStatus

# class Handler(http.server.SimpleHTTPRequestHandler):
#     def do_GET(self):
#         self.send_response(HTTPStatus.OK)
#         self.end_headers()
#         msg = 'Hello! you requested %s' % (self.path)
#         self.wfile.write(msg.encode())


# port = int(os.getenv('PORT', 80))
# print('Listening on port %s' % (port))
# httpd = socketserver.TCPServer(('', port), Handler)
# httpd.serve_forever()

import os
import io
import boto3
from flask import Flask, request

app = Flask(__name__)

test = os.environ.get('keyid')
print(test)

# client = boto3.Session(
    
# )

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('dashblox')

# testvalue = table.get_item(Key={'db': 'levelcode'})
# print(testvalue["Item"]["data"])

@app.route('/', methods=['POST'])
def index():
    if request.method == 'POST':
        requestdata = request.data.decode('UTF-8')
        # print(requestdata)
        item = table.get_item(Key={'db': requestdata})
        data = item["Item"]["data"]
        return data, 200
    else:
        return "Invalid method", 403

print("Starting server")

app.run(host='0.0.0.0', port=8080)