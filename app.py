from pymongo import MongoClient
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
reminder=db['reminder']
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
#Notes
@app.route('/notes')
def notes():
    xyz=session['user']
    persons=list(notex.find({"user":xyz}))
    return render_template('index.html',result=persons)
#Note   
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
app.run(debug=True)