import cv2
import pytesseract
from pytesseract import Output

def ocr(img_path):
    img = cv2.imread(img_path)
    #cv2.imshow("Image", img) 
    d = pytesseract.image_to_data(img, output_type=Output.DICT)

    n_boxes = len(d['text'])
    all_txt = []
    for i in range(n_boxes):
        all_txt.append(d['text'][i])
        if int(d['conf'][i]) > 60:
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    #cv2.imshow("Image", img) 
    #cv2.waitKey(0) 
    print("Found words: ",all_txt)
    return all_txt