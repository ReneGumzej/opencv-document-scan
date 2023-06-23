import easyocr
import cv2
import sys
import numpy as np
from src.logger import logging
from src.exception import CustomException


def read_easyocr(document):
        try:
            logging.info("initialize easy OCR")
            reader = easyocr.Reader(['de'])
            logging.info("languages set german 'de'")
            text = reader.readtext(document,paragraph=True)
            logging.info("start reading text from incoming frame")
            for t in text:
                print(t[1])
                rect = cv2.rectangle(document,(int(t[0][0][0]),int(t[0][0][1])),(int(t[0][2][0]),int(t[0][2][1])),(0,0,255), 2)
            logging.info("reading completed")
            return list(t)
                
            
        except Exception as e:
             raise CustomException(e, sys)
        