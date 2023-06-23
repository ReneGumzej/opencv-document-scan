import os 
from src import PATH

def check_log_space(path):
    print("checking log directory memory space")
    size = 0
    for file in os.scandir(path):
        size += os.stat(file).st_size

    size_in_megabyte = size / 1000000
    print(f"current memory space of folder logs is {size_in_megabyte:.2f} MB")
    return size_in_megabyte

def delete_log_files(size,path):
    max_log_size = 100.0
    if size > max_log_size:
        print(f"size of logifles are over {max_log_size}MB. Start deleting logfiles")
        for file in os.scandir(path):
            os.remove(file)
        print("logfiles deleted")