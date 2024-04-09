import flask
from flask import Flask,render_template,request
import cv2
import numpy as np
import os
from werkzeug.utils import secure_filename
from ocr import *
from Blur_Text_Images import *
from recommend import * 
from sensitive_info import *
from distil_model import *
import json

app = Flask(__name__)
UPLOAD_FOLDER = 'static/inp_img'
EDITED_FOLDER = 'static/op_img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['EDITED_FOLDER'] = EDITED_FOLDER

def identify_sensitive(all_words,txt):
    #return all_words,txt.split(' ')
    all_words =[word  for word in all_words if word!=""]
    print(all_words)
    dictImg = detect_sensitive_info(' '.join(all_words))
    dictText = detect_sensitive_info(txt)
    for entity, entity_type in dictImg['named_entities']:
        dictImg.setdefault(entity_type, []).append(entity)
    dictImg.pop('named_entities')
    
    for entity, entity_type in dictText['named_entities']:
        dictText.setdefault(entity_type, []).append(entity)
    dictText.pop('named_entities')
    
    print(dictImg)
    print(dictText)

    return dictImg,dictText

def identify_offensive(all_words,txt):
    all_words =[word  for word in all_words if word!=""]
    label_img = distil_model(' '.join(all_words))
    label_txt = distil_model(txt) 
    return label_img.item(), label_txt.item()

@app.route("/")
def hello_world():
    return render_template("index.html")

@app.route("/extract", methods=['POST'])
def extract_words(): 
    #print(request.form)
    imgfile = request.files['imagefile']
    txt = request.form['txt']
    all_words=[]
    img_exists,txt_exists = 0,0
    sensitive_exists, offensive_exists = 0,0
    img_present,txt_present=0,0
    recommended_rem_offensive = ""
    recommended=""
    sense_text=""
    offensive_image_label, offensive_text_label =2,2
    if imgfile:
        imgfile.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(imgfile.filename)))
        all_words = ocr(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(imgfile.filename)))
    sensitive_words_img,sensitive_words_txt = identify_sensitive(all_words,txt)
    offensive_image_label, offensive_text_label = identify_offensive(all_words,txt)
    #offensive_image_label, offensive_text_label = 2,1
    print(offensive_image_label,offensive_text_label)
    if imgfile:
        img_present = 1
        sensitive_words_img_all = [word for sublist in sensitive_words_img.values() for value in sublist for word in value.split()]
    if txt:
        txt_present= 1
        sensitive_words_txt_all = [word for sublist in sensitive_words_txt.values() for value in sublist for word in value.split()]
        #print(sensitive_words_txt_all)
    if imgfile and len(sensitive_words_img_all)>0:
        img_exists =1
        #print(sensitive_words_img_all)
        blurring_sensitive_information(app,'image',filename=secure_filename(imgfile.filename),sensitive_words_img=sensitive_words_img_all)
        sensitive_exists =1
    if txt and len(sensitive_words_txt_all)>0: 
        txt_exists = 1
        sense_text = blurring_sensitive_information(app,'text',sensitive_words_txt=sensitive_words_txt_all,inp_txt=txt)
        #print(sense_text)
        recommended = recommend(f'Return the sentence "{txt}" after removing the words and numbers {sensitive_words_txt_all} but keep the context and meaning of the sentence the same.')
        print(recommended)
        sensitive_exists =1
    
    if (txt and offensive_text_label !=2 )  or (imgfile and offensive_image_label !=2): 
        offensive_exists = 1
    
    if txt and offensive_text_label == 1: 
        recommended_rem_offensive = recommend(f'Return the sentence "{txt}" after removing the offensive words but keep the context and meaning of the sentence the same.')
        print(recommended_rem_offensive) 
    print(offensive_exists)
    to_render = {
        "img_present":img_present,
        "txt_present": txt_present,
        "img_sen":img_exists,
        "txt_sen":txt_exists,
        "sensitive_exists": sensitive_exists,
        "offensive_exists": offensive_exists,
        "sense_text":sense_text,
        "filename":secure_filename(imgfile.filename),
        "recommended_text":recommended,
        "offensive_image_label": offensive_image_label,
        "offensive_text_label": offensive_text_label,
        "recommended_rem_offensive": recommended_rem_offensive,
        "original_text": txt,
        "sensitive_words_img": sensitive_words_img,
        "sensitive_words_txt": sensitive_words_txt
    }
    return render_template("display.html",to_render = to_render)

@app.route("/final", methods=['POST'])
def submission(): 
    #print(request.form)
    new_entry={"txt":"",
               "img_path":""}
    if "txt" in request.form.keys() :
        txt = request.form['txt']
        new_entry["txt"]=txt
    else: 
        txt = ""
    if "img" in request.form.keys() :  
        img_path = request.form['img']
        new_entry["img_path"] = img_path.strip()
    else: 
        img_path = ""
    print("In Submission function")
    print(txt)
    print(img_path)
    
    f = open('database.json')

    data = json.load(f)
    
    if len(data)==0 : 
        data["1"]=new_entry
    else: 
        keys = [int(key) for key in data.keys()]
        max_key = max(keys)
        data[f"{max_key+1}"]=new_entry
    
    with open("database.json", "w") as outfile: 
        json.dump(data, outfile)
    return render_template("all_posts.html",data = data)


if __name__ == '__main__':
    app.run(debug=True)