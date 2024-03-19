#!/usr/bin/env python
# coding: utf-8

# In[70]:


#get_ipython().system('pip install pytesseract')


# In[71]:


#get_ipython().system('pip install opencv-python')


# In[87]:


#get_ipython().system('pip install rich')


# In[89]:


from rich.console import Console
from rich.markdown import Markdown


# In[91]:


import pytesseract
import os


# In[92]:


from PIL import Image


# In[93]:


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# In[118]:


def fileType(file_path):
    if (os.path.splitext(file_path)[-1].lower() == '.png'):
        detectCoordinatesImage(file_path)
    else:
        text_input = 'This is an edited tweet for testing'
        blurred_list = ['edited','testing'] #Received from ER model
        for word in blurred_list:
            replaced_word = '~~'+word+'~~'
            text_input = text_input.replace(word,replaced_word)
        console = Console()
        markdown = Markdown(text_input)
        console.print(markdown)


# In[119]:


global_dict_coordinates = {}
def detectCoordinatesImage(file_path):
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
    global_dict_coordinates = dict_coordinates
    blur_text(file_path,dict_coordinates)
    


# In[120]:


import cv2
import numpy as np
def blur_text(file_path, text_coordinates):
    # Load the image
    image = cv2.imread(file_path)
    
    # Iterate over each word and blur the specified region
    for word, coordinates in text_coordinates.items():
        for coord in coordinates:
            x, y, w, h = coord
            roi = image[y:y+h, x:x+w]
            blurred_roi = cv2.GaussianBlur(roi, (35, 35), sigmaX=30, sigmaY=30)  # Increase kernel size and sigma
            image[y:y+h, x:x+w] = blurred_roi
    
    cv2.imshow("Blurred Image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# In[121]:


file_path = r"C:\Users\shami_6wz\Desktop\Tweet_Demo.png"
fileType(file_path)


# In[122]:


#pip install nbconvert


# In[ ]:


#get_ipython().system('jupyter nbconvert --to script Blur_Text_Images.ipynb')


# In[ ]:




