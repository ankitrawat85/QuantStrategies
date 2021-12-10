from gevent.pywsgi import WSGIServer
from flaskr import app

http_server = WSGIServer(('192.168.43.210', 443), app, keyfile='key.pem', certfile='cert.pem')
#http_server = WSGIServer(('192.168.43.210', 80), app)
http_server.serve_forever()

'''
Find ip by ipconfig 
and then change above , in my case it is 192.168.43.210

http://192.168.43.210/env
http://192.168.43.210/helloj?name=das&format=json

#HTTPs
https://192.168.43.210/env
https://192.168.43.210/helloj?name=das&format=json

'''