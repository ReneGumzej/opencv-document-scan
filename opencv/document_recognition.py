import cv2 
import sys
from src.logger import logging
from src.exception import CustomException
import numpy as np
from OCR.letter_recognition import read_easyocr
from time import sleep




class DocumentRecognition:

    def __init__(self, frame_width=980, frame_height=1200):
        self.frame_width = frame_width
        self.frame_height = frame_height
        
    
    def _preprocess_image(self, frame):
        logging.info("Start to preprocess incoming frame")
        kernel = np.ones((5,5))

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur_frame = cv2.GaussianBlur(gray_frame, (5,5), 1)
        canny_frame = cv2.Canny(blur_frame, 150, 100)
        dial_frame = cv2.dilate(canny_frame, kernel, iterations=2)
        threshold_frame = cv2.erode(dial_frame, kernel, iterations=1)
        logging.info("Preprocessing completed")
        return threshold_frame
    

    def _scan_document(self,frame):
        logging.info("Start to scan the incoming frame")
        cornerarray = np.array([])
        max_area = 0
        logging.info("trying to find any contours")
        contours, hierarchy = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        logging.info("processing contours")
        for point in contours:
            area = cv2.contourArea(point)
            if area > 8000:
                #drw = cv2.drawContours(copy,point,-1, (0,255,0), 5) #draws a box arround the document
                perimeter = cv2.arcLength(point, True)
                approximation_of_cornerpoints = cv2.approxPolyDP(point, 0.02*perimeter,True)
                if area > max_area and len(approximation_of_cornerpoints) == 4:
                    cornerarray = approximation_of_cornerpoints
                    max_area = area
        corner_points_frame = cv2.drawContours(self.frame_copy,cornerarray,-1, (0,255,0), 8) # draws dots on corners
        logging.info(f"found contours with area:{max_area} and cornerpoints {cornerarray}")
        return cornerarray, corner_points_frame

    def _reorder(self, points):
        logging.info("Start to reoder the cornerpoints")
        points = points.reshape((4,2))
        new_points = np.zeros((4,1,2), np.int32)
        add = points.sum(1)
        new_points[0] = points[np.argmin(add)]
        new_points[3] = points[np.argmax(add)]
        diff = np.diff(points, axis=1)
        new_points[1] = points[np.argmin(diff)]
        new_points[2] = points[np.argmax(diff)]
        logging.info("reordering completed")
        return new_points
    

    def _warp_document(self, frame,corner_coordinates):
        logging.info("warp incoming frame with corner coordinates")
        corner_coordinates = self._reorder(corner_coordinates)
        image_points = np.float32(corner_coordinates)
        rotated_points = np.float32([[0,0],[self.frame_width,0],[0,self.frame_height],[self.frame_width,self.frame_height]])
        matrix = cv2.getPerspectiveTransform(image_points, rotated_points)
        output_image = cv2.warpPerspective(frame, matrix,(self.frame_width,self.frame_height))
        logging.info("warping completed")
        return output_image
    
    

    def document_sharpening(self,document):
        logging.info("Start to sharpen the incoming frame")
        kernel = np.array([[0, -1, 0],
                        [-1, 5, -1],
                        [0, -1, 0]])
        sharp = cv2.filter2D(document, -1, kernel)
        logging.info("sharpening completed")
        return sharp

    def run_webcam(self, src):
        self.webcam = cv2.VideoCapture(src)
        self.webcam.set(3, self.frame_width)
        self.webcam.set(4, self.frame_height)
        self.webcam.set(10, 0)
        recording = True
        counter = 0
        logging.info("Start to initializing the webcam")
        try:
            while recording:
                
                ret, frame = self.webcam.read()
                #frame_resize = cv2.resize(frame,(self.frame_width, self.frame_height))
                self.frame_copy = frame.copy()
                threshold_frame = self._preprocess_image(frame)
                cornerarray, corner_points_frame = self._scan_document(threshold_frame)

                if cornerarray.size != 0:
                    
                    output_image = self._warp_document(self.frame_copy,cornerarray)
                    sharp = self.document_sharpening(output_image)
                    read_easyocr(sharp)
                    cv2.imshow("Document-Scan-Sharp", sharp)
                    #cv2.imshow("Document-Scan", output_image)

                  
                    #cv2.imwrite(f"assets/document.jpg", sharp)
                
                cv2.imshow("Frame", corner_points_frame)
    
                if cv2.waitKey(1) == ord('q'):
                    break
            logging.info("Webcam session closed")    

        except Exception as e:
            raise CustomException(e,sys)


