from pymongo import MongoClient
from bson.objectid import ObjectId
import cv2
from flask import *
from twilio.rest import Client
##Text to speech
import pyttsx3
from pyqrcode import QRCode
import speech_recognition as sr
import threading
import json
import plyer
import requests
#!For time related 
import sched
import time as time_module
import random
import wikipedia
import qrcode
import string
from pytube import YouTube
import os
from pathlib import Path
import png
from datetime import datetime
#Weather Api_Key
api_key = '30d4741c779ba94c470ca1f63045390a'
#Wiki Api Key
WIKI_REQUEST = 'http://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles='
client=MongoClient('localhost',27017)
db=client['keep']
loginx=db['login']
notex=db['note']
trashx=db['trash']
reminderx=db['reminder']
app = Flask(__name__,template_folder='temp')
app.secret_key='secret'
#speak
def speak(text):
    engine = pyttsx3.init()
    engine.setProperty("rate", 188)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.say(text)
    engine.runAndWait()
#Login
@app.route('/',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        session['user']=email
        userx=loginx.find_one({'email':email,'password':password})
        if userx:
            return redirect(url_for('notes'))
        else:
            flash('Invalid Username or Password')
            return redirect(url_for('login'))
    return render_template('login.html')
#Signup
@app.route('/signup',methods=['GET','POST'])
def index():
    if request.method=='POST':
        email=request.form['email']
        namex=request.form['name']
        phone=request.form['phone']
        password=request.form['password']
        session['user']=email
        name=session['user']
        name2=name.replace(".","")
        name3=session['user'].split('.')[0]
        try:
            zx={'name':namex,'phone':phone,'email':email,'password':password}
            loginx.insert_one(zx)
            return redirect(url_for('login'))
        except:
            flash('User Already Exists')
            speak('User Already Exists')
            return render_template('signup.html')
    return render_template('signup.html')
#Creating Note   
@app.route('/add',methods=['GET','POST'])
def create():
    if request.method=='POST':
        title=request.form['title']
        text=request.form['text']
       #current date and time
        now = datetime.now()
        name=session['user']
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        z={
            'title':title,
            "text":text,
            "time":dt_string,
            "user":name
        }
        res=notex.insert_one(z)
        idx=res.inserted_id
        notex.update_one(
            {'user':name},
            {'$push':{'notex':idx}}
        )
        return redirect(url_for('notes'))
    return render_template('index.html')
#Notes
@app.route('/notes')
def notes():
    xyz=session['user']
    persons=list(notex.find({"user":xyz}))
    return render_template('index.html',result=persons)
#Edit
@app.route('/edit/<id>',methods=['GET','POST'])
def update(id):
    if request.method=='POST':
        title=request.form['title']
        text=request.form['text']
        name=session['user']
        now = datetime.now()
        current_time =now.strftime("%d/%m/%Y %H:%M:%S")
        xyz="Edited in "+current_time
        z={
            "title":title,
            "text":text,
            "time":xyz,
            "user":name
        }
        notex.update_one({'_id':ObjectId(id)},{'$set':z})
        return redirect(url_for('notes'))
    else:
        person=notex.find_one({'_id':ObjectId(id)})
        return render_template('EDIT.html',result=person)
#Delete
@app.route('/delete/<id>')
def delete(id):
    trashx.insert_one(notex.find_one({'_id':ObjectId(id)}))
    notex.delete_one({'_id':ObjectId(id)})
    return redirect(url_for('notes'))
#Trash
@app.route('/trash')
def trash():
    xyz=session['user']
    persons=list(trashx.find({"user":xyz}))
    return render_template('trash.html',result=persons)
#Restore Trash
@app.route('/restore/<id>',methods=['GET','POST'])
def restore(id):
    notex.insert_one(trashx.find_one({'_id':ObjectId(id)}))
    trashx.delete_one({'_id':ObjectId(id)})
    return redirect(url_for('notes'))
#Delete trash
@app.route('/delete_trash/<id>',methods=['GET','POST'])
def delete_trash(id):
    trashx.delete_one({'_id':ObjectId(id)})
    return redirect(url_for('trash'))
#User Info
@app.route('/userinfo')
def userinfo():
    xyz=session['user']
    persons=list(loginx.find({"email":xyz}))
    return render_template('userinfo.html',result=persons)
#Edit User Info page
@app.route('/userEdit/<id>',methods=['POST'])
def userEdit(id):
    if request.method=='POST':
        namex=request.form['name']
        phone=request.form['phone']
        z={
            "name":namex,
            "phone":phone
        }
        name=session['user']
        loginx.update_one({'_id':ObjectId(id)},{'$set':z})
        return redirect(url_for('userinfo'))
    return render_template('userinfo.html')
#plyer notification 
def notification(msg):
    title="Task"
    plyer.notification.notify(title=title,message=msg,timeout=3)
    speak("You have a task to do Title :"+msg)
#convert time
def convert_time(time):
    time = time.split("T")
    time = time[0]+" "+time[1]
    return time
#whatsapp message
def send_whatsapp(time,msg,name):
    name=session['user']
    account_sid = 'ACd78722a228d0c57a16011c23a0900cdb'
    auth_token = '252e8647218849b525f85d4d8219a3b6'
    num=""
    namee=""
    persons=list(loginx.find({"email":name}))
    for person in persons:
        num=person['phone']
        namee=person['name']
    client = Client(account_sid, auth_token)
    from_whatsapp_number='whatsapp:+14155238886'
    to_whatsapp_number='whatsapp:+88'+num
    message="Hello "+namee+" ❤\n"+"You have a task to do at "+time+"\nTitle:"+msg
    client.messages.create(body=message,from_=from_whatsapp_number,to=to_whatsapp_number)
#Task
def time_set(time,msg,name):
    scheduler = sched.scheduler(time_module.time, time_module.sleep)
    t = time_module.strptime(time, '%Y-%m-%d %H:%M')
    t = time_module.mktime(t)
    scheduler_e = scheduler.enterabs(t, 1,notification,argument=(msg ,))
    scheduler_e = scheduler.enterabs(t, 1,send_whatsapp,argument=(time,msg,name ,))
    scheduler.run()
@app.route('/remainder',methods=['GET','POST'])
def remainder():
    if request.method=='POST':
        title=request.form['title']
        datetime=request.form['datetime']
        sad_date=datetime.replace("T"," ")
        name=session['user']
        z={
            'title':title,
            "datetime":sad_date,
            "user":name
        }
        try:
            res=reminderx.insert_one(z)
            idx=res.inserted_id
            reminderx.update_one(
            {'user':name},
            {'$push':{'reminderx':idx}}
            )
            return redirect(url_for('remainders'))
        finally:
            threading.Thread(target=time_set(sad_date,title,name)).start()
    return render_template('remainder.html')
#Task
@app.route('/remainders')
def remainders():
    name=session['user']
    persons=list(reminderx.find({"user":name}))
    return render_template('remainder.html',result=persons)
#Edit Task
@app.route('/edit_remainder/<id>',methods=['GET','POST'])
def edit_remainder(id):
    if request.method=='POST':
        title=request.form['title']
        namee=session['user']
        datetime=request.form['datetime']
        z={
            'title':title,
            "datetime":datetime,
            "user":namee
        }
        reminderx.update_one({'_id':ObjectId(id)},{'$set':z})
        return redirect(url_for('remainders'))
    else:
        todo=reminderx.find_one({'_id':ObjectId(id)})
        return render_template('edit_remainder.html',p=todo)
#Delete Task
@app.route('/delete_remainder/<id>',methods=['GET','POST'])
def delete_remainder(id):
    reminderx.delete_one({'_id':ObjectId(id)})
    return redirect(url_for('remainders'))
app.run(debug=True)