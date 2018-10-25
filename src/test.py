import os
import string
import hashlib
os.chdir('../test_directory')
dir = os.getcwd()
#print(dir)
# for f in os.walk(dir):
#     for filename in f[2]:
#         print(os.path.join(dir, filename))


# string = "file1.23.chunk"
# split = string.split(".")
# chunk_num = split[-2]
# filename = ".".join(split[:-2])
# print(filename)
CHUNK_SIZE = 1024
file_name = "file2.txt"
full_path = os.path.join(dir, file_name)
checksum = hashlib.md5(open(full_path, 'rb').read()).hexdigest()
file_size = os.stat(full_path).st_size
#print("size of file: " + str(file_size))
leftover_bytes = file_size % CHUNK_SIZE
if leftover_bytes == 0:
    number_of_chunks = int(file_size / CHUNK_SIZE)
else:
    number_of_chunks = int((file_size / CHUNK_SIZE) + 1)

#print(number_of_chunks)

def if_key_value_pair_exists(key, val, item):
    if key in item and val == item[key]:
        return True
    else:
        return False
arr = [ {'file_name': "file1",
        'chunks': [1, 3]}, {'file_name': "file2", 'chunks': [1,3,4]}]
key, val = 'file_name', "file1" 
for item in arr:
    if(if_key_value_pair_exists(key, val, item)):
        print("ok")

print("end")    
