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
    return render_template('index.html',name=glowname())
#Notes
@app.route('/notes')
def notes():
    xyz=session['user']
    persons=list(notex.find({"user":xyz}))
    return render_template('index.html',result=persons,name=glowname())
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
    return render_template('trash.html',result=persons,name=glowname())
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
    return render_template('userinfo.html',result=persons,name=glowname())
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
    return render_template('remainder.html',result=persons,name=glowname())
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
@app.route('/password')
def password():
    return render_template('password.html')
#passwords maker
@app.route('/password_maker',methods=['POST'])
def password_maker():
    if request.method=='POST':
        length=request.form['length']
        length=int(length)
        password=''
        for i in range(length):
            password+=random.choice(string.ascii_letters+string.digits+string.punctuation)
            passw="Your Password: "+password
        return render_template('password.html',password=passw)
    return redirect(url_for('password'))
#yt Download Function
def ytdown(link):
    url = YouTube(link)
    video = url.streams.get_highest_resolution()
    path_to_download_folder = str(os.path.join(Path.home(), "E:\Google-Keep-Notes-Clone-By-MongoDB"))
    video.download(path_to_download_folder)
    flash('Downloaded Successfully')
#Youtube page
@app.route('/youtube')
def youtube():
    return render_template('youtube.html',name=glowname())
#Youtube Download Page
@app.route('/youtube-download',methods=['POST'])
def youtube_download():
    if request.method == 'POST':
        link = request.form['link']
        try:
            threading.Thread(target=ytdown(link)).start()
        except:
            flash('Download Failed')
        return render_template('youtube.html')
    return redirect(url_for('youtube'))
#Weather Page
@app.route('/weathers')
def weathers():
    return render_template('weather.html',name=glowname())
#Weather_Recognition
@app.route('/speechrecognize')
def speech_recognizer():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Hello "+glowname()+" which city's Weather Do you Want to Know ?")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            weather_data = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={text}&units=imperial&APPID={api_key}")
            weather = weather_data.json()['weather'][0]['main']
            temp = round(weather_data.json()['main']['temp'])
            tempx =round((temp-32)*5/9)
            speak(f"The weather is {weather} and the temperature is {tempx} degree Celsius in {text}")
            a="Weather in "+text+" is "+weather
            b="it is "+str(tempx)+"  °C"
            icon = weather_data.json()['weather'][0]['icon']+".png"
            return render_template('weather.html',weather=a,temp=b,icon=icon)
        except:
            speak("Sorry"+glowname()+" I couldn't recognize your voice. But Don't worry You can still ask me in manual mode ")
            return render_template('weather.html')
#get weather
@app.route('/weather',methods=['POST'])
def weather():
    if request.method == 'POST':
        city=request.form['city']
        weather_data = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=imperial&APPID={api_key}")
        weather = weather_data.json()['weather'][0]['main']
        temp = round(weather_data.json()['main']['temp'])
        tempx =round((temp-32)*5/9)
        a="Weather in "+city+" is "+weather
        b="it is "+str(tempx)+"  °C"
        icon = weather_data.json()['weather'][0]['icon']+".png"
        return render_template('weather.html',weather=a,temp=b,icon=icon)
#wikipedia image search
def get_wiki_image(search_term):
    try:
        result = wikipedia.search(search_term, results = 1)
        wikipedia.set_lang('en')
        wkpage = wikipedia.WikipediaPage(title = result[0])
        title = wkpage.title
        response  = requests.get(WIKI_REQUEST+title)
        json_data = json.loads(response.text)
        img_link = list(json_data['query']['pages'].values())[0]['original']['source']
        return img_link        
    except:
        return 0
#wikipedia
@app.route('/wiki')
def wiki():
    return render_template('wikipedia.html',name=glowname())
#wikipedia search
@app.route('/wikipedia',methods=['POST'])
def wikiz():
    if request.method == 'POST':
        topic=request.form['data']
        try:
            result = wikipedia.summary(topic, sentences=2)
            pic=get_wiki_image(topic)
            return render_template('wikipedia.html',data=result,pic=pic)
        except:
            flash('Sorry. I couldn\'t find the Result.Please Try Again')
            return render_template('wikipedia.html')
#About Page
@app.route('/About')
def about():
    return render_template('about.html')
#Logout
@app.route('/login')
def logout():
    session.pop('user',None)
    return render_template('login.html')
#qrcode making
def test(text,name):
    for text in text:
        email=text['email']
        password=text['password']
        newData=email+" "+password
        img =qrcode.make(newData)
        type(img)
        img.save(name+'.png')
#Scan Qrcode
@app.route('/qrcodescan')
def qrcodescan():
    cap=cv2.VideoCapture(0)
    detector=cv2.QRCodeDetector()
    while True:
        _,img=cap.read()
        data,one,_=detector.detectAndDecode(img)
        if data:
            a=data
            dataz1=a.split(' ')[0]
            dataz2=a.split(' ')[1]
            list={"email":dataz1,"password":dataz2}
            return render_template('qrlogin.html',data=list)
        cv2.imshow(' qrocode img',img)
        if cv2.waitKey(1)==ord('q'):
            break
        cv2.destroyAllWindows()
    return render_template('qrlogin.html')
#Qrcode
@app.route('/qrcode')
def qrcodee():
    name=session['user']
    picx='E:\Google-Keep-Notes-Clone-By-MongoDB\ '+name+'.png'
    return render_template('qrcode.html',pic=picx,name=glowname())
#Qrcode-Download
@app.route('/qrcode-download',methods=['GET','POST'])
def qrcodee1():
    if request.method=='POST':
        name=session['user']
        res=list(loginx.find({"email":name}))
        test(res,name)
        new='E:\ '+name+'.png'
        return redirect(url_for('qrcodee'))
    return render_template('qrcode.html',pic=new)
#speak
def speak(text):
    engine = pyttsx3.init()
    engine.setProperty("rate", 188)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.say(text)
    engine.runAndWait()
#Glowname
def glowname():
    namee=session['user']
    res=list(loginx.find({"email":namee}))
    for i in res:
        namek=i['name']
    return namek
app.run(debug=True)