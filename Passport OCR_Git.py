from cv2 import cv2
import pytesseract

import pandas as pd
import numpy as np
import math
from matplotlib import pyplot as plt

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

#####################################

img = cv2.imread('images\Passport.png',0)
(height, width) = img.shape

#####################################

img_copy = img.copy()

img_canny = cv2.Canny(img_copy, 50, 100, apertureSize = 3)

img_hough = cv2.HoughLinesP(img_canny, 1, math.pi / 180, 100, minLineLength = 100, maxLineGap = 10)

(x, y, w, h) = (np.amin(img_hough, axis = 0)[0,0], np.amin(img_hough, axis = 0)[0,1],
np.amax(img_hough, axis = 0)[0,0] - np.amin(img_hough, axis = 0)[0,0],
np.amax(img_hough, axis = 0)[0,1] - np.amin(img_hough, axis = 0)[0,1])

img_roi = img_copy[y:y+h,x:x+w]

#####################################

img_roi = cv2.rotate(img_roi, cv2.ROTATE_90_COUNTERCLOCKWISE)

(height, width) = img_roi.shape

img_roi_copy = img_roi.copy()
dim_mrz = (x, y, w, h) = (1, round(height*0.9), width-3, round(height-(height*0.9))-2)
img_roi_copy = cv2.rectangle(img_roi_copy, (x, y), (x + w ,y + h),(0,0,0),2)

img_mrz = img_roi[y:y+h, x:x+w]
img_mrz =cv2.GaussianBlur(img_mrz, (3,3), 0)
ret, img_mrz = cv2.threshold(img_mrz,127,255,cv2.THRESH_TOZERO)

mrz = pytesseract.image_to_string(img_mrz, config = '--psm 12')
mrz = [line for line in mrz.split('\n') if len(line)>10]

if mrz[0][0:2] == 'P<':
    lastname = mrz[0].split('<')[1][3:]
else:
    lastname = mrz[0].split('<')[0][5:]

firstname = [i for i in mrz[0].split('<') if (i).isspace() == 0 and len(i) > 0][1]

pp_no = mrz[1][:9]

###################################

img_roi_copy = img_roi.copy()
dim_lastname_chi = (x, y, w, h) = (455, 1210, 120, 70)
img_roi_copy = cv2.rectangle(img_roi_copy, (x, y), (x + w ,y + h),(0,0,0))

img_lastname_chi = img_roi[y:y+h, x:x+w]
img_lastname_chi = cv2.GaussianBlur(img_lastname_chi, (3,3), 0)
ret, img_lastname_chi = cv2.threshold(img_lastname_chi,127,255,cv2.THRESH_TOZERO)

lastname_chi = pytesseract.image_to_string(img_lastname_chi, lang = 'chi_sim', config = '--psm 7')
lastname_chi = lastname_chi.split('\n')[0]

dim_firstname_chi = (x, y, w, h) = (455, 1300, 120, 70)
img_roi_copy = cv2.rectangle(img_roi_copy, (x, y), (x + w ,y + h),(0,0,0))

img_firstname_chi = img_roi[y:y+h, x:x+w]
img_firstname_chi =cv2.GaussianBlur(img_firstname_chi, (3,3), 0)
ret, img_firstname_chi = cv2.threshold(img_firstname_chi,127,255,cv2.THRESH_TOZERO)

firstname_chi = pytesseract.image_to_string(img_firstname_chi, lang = 'chi_sim', config = '--psm 7')
firstname_chi = firstname_chi.split('\n')[0]

passport_dict = {'Passport No.': pp_no,
                 'First Name': firstname,
                 'Last Name': lastname,
                 'First Name (汉字)': firstname_chi,
                 'Last Name (汉字)': lastname_chi}

output = pd.DataFrame(columns = ['Passport No.','First Name','Last Name','First Name (汉字)','Last Name (汉字)'])
output = output.append(passport_dict, ignore_index = True)

output.to_excel("output.xlsx", index = False)