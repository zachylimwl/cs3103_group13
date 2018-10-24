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
res = {}
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
res["checksum"] = checksum
res["number_of_chunks"] = number_of_chunks
res["file_name"] = file_name
#print(res)

ch = "file_teset_1.chunk"
string = ch.split(".")
arr = string[0].rsplit('_', 1)
print(arr)