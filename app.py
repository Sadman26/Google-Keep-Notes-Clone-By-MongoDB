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