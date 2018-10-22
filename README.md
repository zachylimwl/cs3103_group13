# CS3103 Network Practice Project
This is a project done for a NUS School of Computing module, CS3103. Is it a Peer-To-Peer File Transfer Project.

## GROUP 13
* [Chan Jing Hui Benedict](https://github.com/Bendistocratic)
* [Lim Wei Ling Zachary](https://github.com/zachylimwl)
* [Sherina Toh Shi Pei](https://github.com/sherinatoh)
* [Wang Pengcheng](https://github.com/peng229)

### Instructions for running
1. Go to src: `cd src`
2. Start the tracker: `python3 Tracker.py`
3. Start the client: `python3 Peer.py`



---
####FILE CHUNKING MECHANISM
Currently, the files to be chunked and "torrented" are in the test_directory folder in this repo  

#####for complete files in the folder  
they will be processed to dictionary formatted below:  
res = {"checksum": checksum_string,  
          "number_of_chunks": 37  
          "file_name": file_name_string}  

#####for chunks  
naming convention: "file_name"_"chunk_number".chunk
e.g. script_3.chunk  

---
####ADVERTISING  
method: "advertise_to_tracker  
send a dictionary over to Tracker  
  
Informs tracker of files in directory, checksum of each file, owned  
        chunks of each file, source port of Peer [TO BE IMPLEMENTED]  
        {  
            "source_port": port_num [not implemented yet],  
            "files": [{"checksum": "checksum", "number_of_chunks": 1, "file_name": "f1"}, ...],  
            "chunks": [{"chunks": [1, 2, 3, 4, 5], "file_name": "f1"}, ...]  
            "message_type": "INFORM_AND_UPDATE",  
        }  

Tracker will maintain a list of such dictionaries (each entry is the information of one peer).  
  
---
####SENDING OF CHUNKS  
depending on the request sent from another peer that contains file_name, chunk_number  
- read the corresponding bytes from the file,  
- write to a new file and give it the custom extension .chunk  
- send over  
