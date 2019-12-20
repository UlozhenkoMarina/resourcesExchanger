import shutil
import webbrowser

from b2sdk.account_info import InMemoryAccountInfo
from b2sdk.download_dest import DownloadDestLocalFile
from flask import Flask, render_template
from flask import request
import psycopg2
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from dao import Dao as d
from b2sdk.api import *
import os

info = InMemoryAccountInfo()
b2_api = B2Api(info)
application_key_id = '00784d151921'
application_key = '0000922b1a2e4e70ddf1535759681e3b770535b1eb'
b2_api.authorize_account("production", application_key_id, application_key)
bucket = b2_api.get_bucket_by_name("resourcesExchanger")
author = " "

conn = psycopg2.connect(host="localhost", database="resourcesExchanger", user="postgres", password="tiger")

app = Flask(__name__)
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    users = d.getUsers(conn=conn)
    print(users)
    if username in users:
        print(users[username])
        print(hash(password))
        print(password)
        if int(users[str(username)]) == mhash(password) % 2147483647:
            return True
    return False


def mhash(pas):
    a = len(pas) * len(pas) + len(pas)
    for i in range(0, len(pas)):
        a += ord(pas[i])
    return a


@app.route("/read/<title>/<data>", methods=['GET'])
def read(title, data):
    print(data)
    file = open("./static/" + title, 'w')
    b2_file_name = title
    local_file_name = './static/' + title
    download_dest = DownloadDestLocalFile(local_file_name)
    bucket.download_file_by_name(b2_file_name, download_dest)
    chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    webbrowser.get(chrome_path).open("./static/" + title)
    return render_template("resourceSearchPost.html", res=data)


@app.route("/resourcesSearch", methods=['GET'])
def resourcesSearchGet():
    return render_template("resourceSearch.html")


@app.route("/resourcesSearch", methods=['POST'])
def resourcesSearch():
    r = request.form['search']
    res = ""
    res1 = d.getResourcesTitles(conn, r)
    for i in res1:
        res += ";" + i
    return render_template("resourceSearchPost.html", res=res1)


@app.route("/addResource", methods=['POST'])
def handleFileUpload():
    if (not d.isResourceInDb(conn, request.form['file'])):
        if 'file' in request.files:
            photo = request.files['file']
            print(photo.filename)
            extension = photo.filename.split(".")[-1]
            photo.save("./static/" + request.form['title'] + "." + extension)
            bucket.upload_local_file(local_file="./static/" + request.form['title'] + "." + extension,
                                     file_name=request.form['title'] + "." + extension,
                                     file_infos={"mood": "smile"},
                                     )
            os.remove("./static/" + request.form['title'] + "." + extension)
            global author
            print("keywords")
            print(request.form['keywords'])
            i = ""
            keywords = ""
            for j in request.form['keywords']:
                keywords += i
            d.addResource(conn, request.form['title'] + "." + extension, request.form['keywords'], author)
        return render_template("startPage.html")
    else:
        return render_template("addResource.html", error="Choose unique title fo your file")


@app.route("/addResource", methods=['GET'])
def addResourceGet():
    return render_template("addResource.html")


@app.route("/login", methods=['POST'])
def loginPost():
    login = request.form['Login']
    password = request.form['Password']
    if verify_password(login, password):
        global auth
        auth.__setattr__(login, password)
        global author
        author = login
        return render_template("actionChoise.html")
    else:
        return render_template("LogIn.html", error="Username or password is incorrect")


@app.route("/login", methods=['GET'])
def loginGet():
    return render_template("LogIn.html")


@app.route("/createAccount", methods=['POST'])
def createAccountPost():
    if (not d.isAuthorInDb(conn, request.form['Login'])):
        print("CREATE")
        login = request.form['Login']
        password = request.form['Password']
        d.addUser(conn=conn, username=login, password=mhash(password) % 2147483647)
        return render_template("startPage.html")
    else:
        render_template("createAccount.html", error="User with such already exist")


@app.route("/createAccount", methods=['GET'])
def createAccountGet():
    return render_template("createAccount.html")


@app.route("/")
def startPage():
    d.create(conn)
    return render_template("startPage.html")


if __name__ == '__main__':
    app.run()
