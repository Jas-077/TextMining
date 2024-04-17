import pytesseract
import os
import cv2
import numpy as np
from PIL import Image
import flask
from flask import Flask



def blur_image(app, file_path,sensitive_words_img,filename):
    img = Image.open(file_path)
    data = pytesseract.image_to_data(img, output_type='dict')
    boxes = len(data['level'])
    sensitive_information_list = set(sensitive_words_img) #Fed to us by ER Model
        
    dict_coordinates = {}
    for i in range(boxes):
        if data['text'][i] != '':
            if data['text'][i] in sensitive_information_list:
                if data['text'][i] not in dict_coordinates:
                    dict_coordinates[data['text'][i]] = [[data['left'][i], data['top'][i], data['width'][i], data['height'][i]]]
                else:
                    dict_coordinates[data['text'][i]].append([data['left'][i], data['top'][i], data['width'][i], data['height'][i]])
    #print(dict_coordinates)

    image = cv2.imread(file_path)
    
    # Iterate over each word and blur the specified region
    for word, coordinates in dict_coordinates.items():
        for coord in coordinates:
            x, y, w, h = coord
            roi = image[y:y+h, x:x+w]
            blurred_roi = cv2.GaussianBlur(roi, (35, 35), sigmaX=30, sigmaY=30)  # Increase kernel size and sigma
            image[y:y+h, x:x+w] = blurred_roi
    
    #cv2.imshow("Blurred Image", image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    cv2.imwrite(os.path.join(app.config['EDITED_FOLDER'], filename), image) 
    


def blur_text(phrase,sensitive_wrd_lst):
    for word in sensitive_wrd_lst:
        replaced_word=""
        for c in word: 
            replaced_word += c + '\u0336'
        phrase = phrase.replace(word,replaced_word)
    return phrase


def blurring_sensitive_information(app,file_type,filename="",sensitive_words_img=[],sensitive_words_txt=[],inp_txt=""):
    if file_type == 'image':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) 
        blur_image(app,file_path,sensitive_words_img,filename)
    else:
        phrase = inp_txt
        print(phrase)
        #sensitive_wrd_lst = ['edited','testing'] #Received from ER model
        return blur_text(phrase,sensitive_words_txt)






