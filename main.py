from opencv.document_recognition import DocumentRecognition
from src.utils import check_log_space, delete_log_files
from src import PATH
import multiprocessing as mp
import os
from OCR.letter_recognition import read_easyocr


if __name__ == "__main__":
    scanner = DocumentRecognition()
    size = check_log_space(PATH)
    delete_log_files(size, PATH)
    #document = scanner.run_webcam()

    with mp.Pool(os.cpu_count()) as p:
        p.map(scanner.run_webcam, [0])
    
