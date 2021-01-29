#  coding: utf-8 
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        #print ("Got a request of: %s\n" % self.data.decode("utf-8"))

        split_data = self.data.decode("utf-8").split('\r\n')
        first_line = split_data[0].split(' ')

        # 405, Method not allow
        if ( (first_line[0] == "POST") or (first_line[0] == "PUT") or (first_line[0] == "DELETE" ) ):
            self.request.sendall(bytearray("HTTP/1.0 405 Method Not Allowed",'utf-8'))
            return 0

        # https://stackoverflow.com/questions/9382045/send-a-file-through-sockets-in-python by Aaron Digulla
        else:
            corrected_path = 0
            root = "www"
            address = first_line[1]
            url = root + address
            BASEURL = "http://127.0.0.1:8080" + address

            if ( address[len(address)-1] == '/' ):
                url = url + "index.html"

            url_split = url.split(".")
            if ( len(url_split) == 1 ):
                url = url + "/index.html"
                BASEURL = BASEURL + "/"
                corrected_path = 1
            elif ( len(url_split) == 2 ):
                # only support css and html
                if ( not ( (url_split[1] == "css") or (url_split[1] == "html") ) ):
                    self.request.sendall(bytearray("HTTP/1.0 404 Not Found\r\n",'utf-8'))
                    return 0
            else:
                self.request.sendall(bytearray("HTTP/1.0 404 Not Found\r\n",'utf-8'))
                return 0

            try:
                f = open(url, "r")
            except:
                self.request.sendall(bytearray("HTTP/1.0 404 Not Found\r\n",'utf-8'))
                return 0

            content_type = "Content-Type: text/html\r\n"
            if ( (url.split("."))[1] == "css" ):
                content_type = "Content-Type: text/css\r\n"

            if (corrected_path == 0):
                self.request.sendall(bytearray("HTTP/1.0 200 OK\r\n",'utf-8'))
            elif (corrected_path == 1):
                self.request.sendall(bytearray("HTTP/1.0 301 Moved Permanently\r\n",'utf-8'))
                self.request.sendall(bytearray("Location: " + BASEURL + "\r\n",'utf-8'))
            self.request.sendall(bytearray(content_type,'utf-8'))
            
            l = f.read(1024)
            while (l):
                self.request.send( bytearray(l,'utf-8') )
                l = f.read(1024)

            f.close()
            return 0

        self.request.sendall(bytearray("HTTP/1.0 404 Not Found\r\n",'utf-8'))
        #self.request.sendall(bytearray("OK",'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
