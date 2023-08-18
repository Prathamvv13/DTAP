# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import subprocess

import pyautogui
import os
from apps.home import blueprint
from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
import threading
import time
import speech_recognition as sr

r = sr.Recognizer()

def recognize():
    with sr.Microphone() as source2:
        print("Recognising...\n")
        r.adjust_for_ambient_noise(source2, duration=0.2)
        audio = r.listen(source2)
        try:
            text = r.recognize_google(audio)
            return(str(text))
        except sr.UnknownValueError:
            print("Unable to recognize speech")
        except sr.RequestError as e:
            print("Error occurred during speech recognition:", str(e))

def detect_slideshow():
    while True:
        if "Slide Show" in pyautogui.getActiveWindowTitle():
            print("Switched to slideshow mode")
            while("Slide Show" in pyautogui.getActiveWindowTitle()):
                command = recognize()
                if "next" in command:
                    pyautogui.press("right")
                elif "previous" in command:
                    pyautogui.press("left")
                else:
                    pass
                time.sleep(1)
            print("Slideshow mode turned off")
        time.sleep(1)

def start_detecting_thread():
    detection_thread = threading.Thread(target=detect_slideshow)
    detection_thread.daemon = True
    detection_thread.start()

start_detecting_thread()


def powerpoint(file_path):
    powerpoint_path = "C:/Program Files/Microsoft Office/root/Office16/POWERPNT.EXE"
    # subprocess.Popen([powerpoint_path, "C:/Users/Asus/Desktop/python/app/test.pptx"])
    subprocess.Popen([powerpoint_path, file_path])
    pyautogui.sleep(2)
    pyautogui.press("f5")


@blueprint.route("/index")
@login_required
def index():
    files = display_file()
    return render_template("home/index.html", segment="index", files=files)


@blueprint.route("/<template>")
@login_required
def route_template(template):
    try:
        if not template.endswith(".html"):
            template += ".html"

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template("home/page-404.html"), 404

    except:
        return render_template("home/page-500.html"), 500


@blueprint.route("/reopen_presentation", methods=["POST"])
def reopen_slideshow():
    # file_path = "files" + 
    powerpoint(file_path)  
    files = display_file()
    return render_template("home/index.html", segment="index", files=files)


@blueprint.route("/open_presentation", methods=["POST"])
def open_slideshow():
    file = request.files["file_path"]
    if file:
        file.save(f"./files/{file.filename}")
        try:
            file_path = "./files/" + file.filename
            powerpoint(file_path)
            files = display_file()
            return render_template("home/index.html", segment="index", files=files)

        except Exception as e:
            return f"Error: {str(e)}"
    else:
        return "no file selected"


@blueprint.route("/display_filenames")
def display_file():
    files = os.listdir("files")
    # return files
    # logdir='' # path to your log directory
    logfiles = sorted([f for f in files])
    return logfiles


# Helper - Extract current page name from request
def get_segment(request):
    try:
        segment = request.path.split("/")[-1]

        if segment == "":
            segment = "index"

        return segment

    except:
        return None
