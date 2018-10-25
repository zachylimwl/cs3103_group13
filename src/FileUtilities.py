import glob
import os
from constants import *

def create_chunk_file_name(file_name, chunk_number):
    return file_name + "_" + chunk_number + "." + CUSTOM_CHUNK_EXTENSION

def does_file_exist(file_name, directory):
    return os.path.isfile(os.path.join(directory, file_name))

def open_file(file_name, directory):
    return open(os.path.join(directory, file_name), "rb")

def remove_file_chunks(file_name, directory):
    file_chunk_path = os.path.join(directory, file_name + "_*" + CUSTOM_CHUNK_EXTENSION)
    for file_chunk in glob.glob(path):
        os.remove(file_chunk)
    return

def combine_chunks(file_name, total_chunks, directory):
    chunk_index = 1
    combined_file_name = os.path.join(directory, file_name)
    while(chunk_index <= total_chunks):
        chunk_file_name = create_chunk_file_name(file_name, chunk_index)
        chunk_file = os.path.join(directory, chunk_file)
        combined_file = open(combined_file_name)
        combined_file.write(chunk_file.read(CHUNK_SIZE))
        chunk_index += 1
    remove_file_chunks(file_name, directory)
    

