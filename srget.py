import sys
from socket import socket,AF_INET,SOCK_STREAM
from urlparse import urlparse
import os

class Downloader():

    def __init__(self):
        self.host = ""
        self.port = 80
        self.filename = ""
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.header_connect = ""
        self.resume_request = ""
        self.header = ""
        self.leftover = ""
        self.curr_bytes = 0
        self.path = ""

        self.lastMod = ""
        self.conlength = 0
        self.ETag = ""

        self.OlastMod = ""
        self.Oconlength = 0
        self.OETag = ""

        self.masur = ".LYdownload"

    # check boolean show that file is already exited or not
    def check_filepath(self):
        path = os.path.realpath(__file__).split(__file__)[0]
        return os.path.isfile(path + self.filename + self.masur)

    def connect(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        print "Connecting to server"

    # send request to server
    def make_request(self):
        self.header_connect = "GET " + self.connect_path + " HTTP/1.1\r\n" + "Host: " + self.host + "\r\n\r\n"
        self.socket.send(self.header_connect)

    def make_resume(self):
        self.resume_request = "GET " + self.connect_path + " HTTP/1.1\r\n" + "Host: " + self.host + "\r\nRange: bytes=" + str(self.curr_bytes) + "-" + str(self.Oconlength) + "\r\n\r\n"
        self.socket.send(self.resume_request)

    # extract content length from the header then cut it from the actual data
    def download(self):
        buffer = ""
        while True:
            rcv = self.socket.recv(8096)
            if not rcv: break
            buffer += rcv

            if "\r\n\r\n" in buffer:
                self.get_header(buffer)
                forCheck = self.get_fromHeader(self.header)
                self.conlength = int(forCheck[0])
                self.lastMod = forCheck[1]
                self.ETag = forCheck[2]
                info = '{}: {}\r\n{}: {}\r\n{}: {}\r\n'.format('Content-Length', self.conlength, 'Last-Modified', self.lastMod, 'ETag', self.ETag)
                break

        print "Received header"

        # header with Content-Length
        if self.conlength != 0:
            with open(self.filename + self.masur, 'wb+') as f, open("info.txt", 'w') as dw:
                f.write(self.leftover)
                size = len(self.leftover)
                dw.write(info)
                while size < self.conlength:
                    atad = self.socket.recv(8096)
                    size += len(atad)
                    f.write(atad)
                    dw.write('{}\r\n'.format(size))

        # header without Content-Length
        else:
            with open(self.filename + self.masur, 'wb+') as f, open("info.txt", 'w') as dw:
                f.write(self.leftover)
                dw.write(info)
                while True:
                    buff = self.socket.recv(8096)
                    if not buff:
                        break
                    f.write(buff)

        os.renames(self.filename + self.masur, self.filename)

        f.close()
        os.remove("info.txt")
        print "Data saved"
        self.socket.close()
        sys.exit()

        print "Socket closed"

    def resume(self):
        buffer = ""
        while True:
            rcv = self.socket.recv(8096)
            if not rcv: break
            buffer += rcv

            if "\r\n\r\n" in buffer:
                self.get_header(buffer)
                forCheck = self.get_fromHeader(self.header)
                self.Oconlength = int(forCheck[0])
                self.OlastMod = forCheck[1]
                self.OETag = forCheck[2]
                break

        with open(self.filename + self.masur, 'a') as ad, open("info.txt", 'a') as ndw:
            nsize = self.curr_bytes
            while nsize < self.curr_bytes + self.Oconlength:
                atad = self.socket.recv(8096)
                nsize += len(atad)
                ad.write(atad)
                ndw.write('{}\r\n'.format(nsize))


        os.renames(self.filename + self.masur, self.filename)

        ad.close()
        os.remove("info.txt")
        print "Data saved"
        self.socket.close()
        sys.exit()

        print "Socket closed"

    # for checking that file modified or not
    def check_similar(self):
        with open("info.txt", 'r') as rd:
            read = rd.read()
            self.curr_bytes = int(read.split("\r\n")[-2])
            old = self.get_fromHeader(read)
            self.Oconlength = old[0]
            self.OlastMod = old[1]
            self.OETag = old[2]
        return self.Oconlength == self.conlength and self.OlastMod == self.lastMod and self.OETag == self.ETag

    def get_header(self, sth):
        self.header, self.leftover = sth.split("\r\n\r\n")

    def get_fromHeader(self, header):
        splitted = header.split("\r\n")
        cl = ''
        lm = ''
        et = ''
        for each in splitted:
            if "Content-Length" in each:
                word, cl = each.split(" ")
            if "Last-Modified" in each:
                word, lm = each.split(": ")
            if "ETag" in each:
                word, et = each.split(" ")
        return cl, lm, et

    def DocEx(self, input):
        self.filename = input[2]
        url = input[-1] # url:port
        url_component = urlparse(url)
        self.connect_path = url_component.path
        self.host = url_component.hostname
        if url_component.port != None:
            self.port = int(url_component.port)
        self.connect()
        if self.check_filepath():
            if not self.check_similar():
                # can resume immediately
                self.make_resume()
                self.resume()
            else:
                # something changed
                print "File is unable to resume. The program will re-download file for you."
                self.make_request()
                self.download()
            # resume
        else:
            # start downloading
            self.make_request()
            self.download()

if __name__ == '__main__':
    input = sys.argv
    download = Downloader()
    download.DocEx(input)