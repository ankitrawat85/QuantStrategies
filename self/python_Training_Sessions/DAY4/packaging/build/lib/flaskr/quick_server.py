from flask import Flask 

#https://flask.palletsprojects.com/en/2.0.x/api/
#Flask(import_name, 
#static_url_path=None, static_folder='static', template_folder='templates',
#
#static_host=None, host_matching=False, subdomain_matching=False, 
#instance_path=None, instance_relative_config=False, root_path=None)

#Server pov 
#Static content - html, js, css - static_folder
    # prefix of URL endpoint - 'static' - configured by static_url_path
    # http://localhost:5000/static/hello.txt Flask would serve hello.txt from static_folder
#Dynamic content - templates - template_folder


#app = Flask(__name__)
from flaskr import app

@app.route("/")  #http://localhost:5000/
def home():
    return """
    <html> <head><title>My Webserver</title>
    <style>
    .some {
        color: red;
    }
    </style></head>
    <body>
    <h1 id="some" class="some">Hello there!!</h1>
    <h1 id="some2" class="some">Hello Again!!</h1>
    </body></html>
    """

#Flask serves from http://localhost:5000/static/favicon.ico
#Browser asks from http://localhost:5000/favicon.ico
#3 ways to solve - notify browser to ask from http://localhost:5000/static/favicon.ico
#(html header change)
#OR flask handles http://localhost:5000/favicon.ico but redirects to http://localhost:5000/static/favicon.ico
#OR 
#Invalidate cache by manually giving http://localhost:5000/favicon.ico

@app.route("/favicon.ico") #http://localhost:5000/favicon.ico
def favicon():
    return app.send_static_file('favicon.ico')

from flask import request, render_template 
import os
@app.route("/env", methods=['GET', 'POST']) #http://localhost:5000/env
def env():
    if request.method == 'POST':
        #name="envp"
        envp = request.form.get('envp', 'all').upper() #request.form is dict 
        env_dict = os.environ
        if os.environ.get(envp, "notfound") != "notfound":
            env_dict = {envp : os.environ.get(envp, "notfound") }
        return render_template('env.html', envs=env_dict) #keyword based arg goes to template as variable
    else:
        return """
    <html> <head><title>Debug</title>
    </head>
    <body>
    <form action="/env" method="post">
    Give Env Var: <input type="text" name="envp" value="ALL" />
    <br /> <br />
    <input type="submit"  value="Submit" />
    </form>
    </body></html>        
        """
        
#GET PARARMS 
    #URL PARAMS - http://localhost:5000/helloj?name=das&format=json 
    #PATH PARAMS - http://localhost:5000/helloj/das/json
#POST/BODY PARAMS
# Content-Type = 'application/json' , body contains json string '{"name" : "das"}'
from flask import jsonify, make_response 

@app.route("/helloj", methods=['GET', 'POST']) #GET URL PARAMS 
@app.route("/helloj/<string:name>/<string:format>") #PATH PARAMS
def helloj(name="ABC", format="json"):   # PATH params would be passed here 
    #connect to DB using sqlalchemy and get age - HOMEWORK
    db = [ dict(name="das", age=40), dict(name="abc", age=30)]
    #GET URL PARAMS 
    if request.method == 'GET':
        fname = request.args.get("name", name)   #request.args si dict 
        fformat = request.args.get("format", format) 
    elif request.method == 'POST':
        if 'Content-Type' in request.headers:
            if request.headers['Content-Type'].lower() in ['text/json', 'application/json']:
                fname = request.json.get('name', name) # request.json is dict
                fformat = 'json' 
            elif request.headers['Content-Type'].lower() in ['text/xml', 'application/xml']:
                #HOMEWORK- handle xml content type 
                #use xml.etree.ElementTree and parse request.data 
                fname = name 
                fformat = format 
            else:
                #HOMEWORK - handle error 
                fname = name 
                fformat = format 
        else:
            #HOMEWORK - handle error 
            fname = name 
            fformat = format
    else:
        #HOMEWORK - handle error 
        fname = name 
        fformat = format
    #Search age 
    age = None 
    for emp in db:
        if emp['name'].lower() == fname.lower():
            age = emp['age']
    #Send output 
    if fformat.lower() == 'json':
        if age is not None:
            success = dict(name=fname, age=age)
            resp = jsonify(success)
            resp.status_code = 200
        else:
            error = dict(name=fname, details="Not found")
            resp = jsonify(error)
            resp.status_code = 500
        return resp
    elif fformat.lower() == 'xml':
        #HOMEWORK - handle when age is None 
        tmp = render_template('output.xml', name=fname, age=age)
        resp = make_response(tmp)
        resp.headers['Content-Type'] = 'application/xml'
        resp.status_code = 200 
        return resp 
    else:
        #HOMEWORK - handle error 
        return "HOMEWORK"

'''
#client code 
url1 = "http://localhost:5000/helloj?name=das&format=json"
url2 = "http://localhost:5000/helloj/das/json"
url3 = "http://localhost:5000/helloj/das/xml"
url4 = "http://localhost:5000/helloj/dasss/json"
import requests
r1 = requests.get(url1)
r1.json()

r2 = requests.get(url2)
r2.json()

r4 = requests.get(url4)
r4.json()
#XML
r3 = requests.get(url3)
import xml.etree.ElementTree as ET 
root = ET.fromstring(r3.text)
print(root)

url_post = "http://localhost:5000/helloj"
headers = {'Content-Type': 'application/json'}
import json 
obj = dict(name="das")
url_r = requests.post(url_post, data=json.dumps(obj), headers=headers)
url_r.json()
'''

        

if __name__ == '__main__':
    # http://localhost:5000
    #run(host=None, port=None, debug=None, load_dotenv=True, **options)
    #This dev server, generally we bind to ip/port or https during deployment 
    app.run()