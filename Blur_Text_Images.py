#!/usr/bin/env python
# coding: utf-8

# In[15]:


from rich.console import Console
from rich.markdown import Markdown
import pytesseract
import os
import cv2
import numpy as np
from PIL import Image


# In[16]:


def blur_image(file_path):
    img = Image.open(file_path)
    data = pytesseract.image_to_data(img, output_type='dict')
    boxes = len(data['level'])
    sensitive_information_list = set() #Fed to us by ER Model
    sensitive_information_list.add('edited')
    sensitive_information_list.add('testing')
        
    dict_coordinates = {}
    for i in range(boxes):
        if data['text'][i] != '':
            if data['text'][i] in sensitive_information_list:
                if data['text'][i] not in dict_coordinates:
                    dict_coordinates[data['text'][i]] = [[data['left'][i], data['top'][i], data['width'][i], data['height'][i]]]
                else:
                    dict_coordinates[data['text'][i]].append([data['left'][i], data['top'][i], data['width'][i], data['height'][i]])
    print(dict_coordinates)

    image = cv2.imread(file_path)
    
    # Iterate over each word and blur the specified region
    for word, coordinates in dict_coordinates.items():
        for coord in coordinates:
            x, y, w, h = coord
            roi = image[y:y+h, x:x+w]
            blurred_roi = cv2.GaussianBlur(roi, (35, 35), sigmaX=30, sigmaY=30)  # Increase kernel size and sigma
            image[y:y+h, x:x+w] = blurred_roi
    
    cv2.imshow("Blurred Image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    


# In[20]:


def blur_text(phrase,sensitive_wrd_lst):
    for word in sensitive_wrd_lst:
            replaced_word = '~~'+word+'~~'
            phrase = phrase.replace(word,replaced_word)
    console = Console()
    markdown = Markdown(phrase)
    console.print(markdown)


# In[21]:


def blurring_sensitive_information(file_type):
    if file_type == 'image':
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        file_path = r"C:\Users\shami_6wz\Desktop\Tweet_Demo.png" #-> file path for testing
        blur_image(file_path)
    else:
        phrase = 'This is an edited tweet for testing'
        sensitive_wrd_lst = ['edited','testing'] #Received from ER model
        blur_text(phrase,sensitive_wrd_lst)


# In[22]:


blurring_sensitive_information('text')


# In[124]:


get_ipython().system('jupyter nbconvert --to script Blur_Text_Images.ipynb')


# In[ ]:




