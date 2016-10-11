import sys
from socket import socket,AF_INET,SOCK_STREAM
from urlparse import urlparse

class Downloader():

    def __init__(self):
        self.host = ""
        self.port = 80
        self.filename = ""
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.header_connect = ""
        self.header = ""
        self.leftover = ""
        self.conlength = 0
        self.path = ""

    def connect(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        print "Connecting to server"

    # send request to server
    def send_header(self):
        self.header_connect = "GET " + self.connect_path + " HTTP/1.1\r\n" + "Host: " + self.host + "\r\n\r\n"
        self.socket.send(self.header_connect)

    # extract content length from the header then cut it from the actual data
    def receive(self):
        buffer = ""
        while True:
            rcv = self.socket.recv(8096)
            if not rcv: break
            buffer += rcv

            if "\r\n\r\n" in buffer:
                self.get_header(buffer)
                if "Content-Length" in self.header:
                    self.get_contentlength()
                break

        print "Received header"

        if self.conlength != 0:
            with open(self.filename, 'w') as f:
                f.write(self.leftover)
                size = len(self.leftover)
                while size < self.conlength:
                    atad = self.socket.recv(8096)
                    size += len(atad)
                    f.write(atad)

        else:
            with open(self.filename, 'w') as f:
                f.write(self.leftover)
                while True:
                    buff = self.socket.recv(8096)
                    if not buffer:
                        break
                    f.write(buff)

        f.close()
        print "Data saved"
        self.socket.close()
        sys.exit()





        print "Socket closed"

    def get_header(self, sth):
        self.header, self.leftover = sth.split("\r\n\r\n")

    def get_contentlength(self):
        splitted = self.header.split("\r\n")
        for each in splitted:
            if "Content-Length" in each:
                word, num = each.split(" ")
                self.conlength = int(num)

    def DocEx(self, input):
        self.filename = input[2]
        url = input[-1] # url:port
        url_component = urlparse(url)
        self.connect_path = url_component.path
        self.host = url_component.hostname
        if url_component.port != None:
            self.port = int(url_component.port)
        self.connect()
        self.send_header()
        self.receive()

if __name__ == '__main__':
    input = sys.argv
    download = Downloader()
    download.DocEx(input)