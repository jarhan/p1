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
        # fileON = os.path.abspath(str(self.filename))
        path = os.path.realpath(__file__).split(__file__)[0]
        # print path + self.filename
        return os.path.isfile(path + self.filename + self.masur)
        # print exist


    def connect(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        print "Connecting to server"

    # send request to server
    def make_request(self):
        self.header_connect = "GET " + self.connect_path + " HTTP/1.1\r\n" + "Host: " + self.host + "\r\n\r\n"
        self.socket.send(self.header_connect)

    def make_resume(self):
        print self.curr_bytes
        print self.Oconlength
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
                print self.header
                self.conlength = int(forCheck[0])
                self.lastMod = forCheck[1]
                self.ETag = forCheck[2]
                info = '{}: {}\r\n{}: {}\r\n{}: {}\r\n'.format('Content-Length', self.conlength, 'Last-Modified', self.lastMod, 'ETag', self.ETag)
                break

        print "Received header"

        # print self.conlength

        # header with Content-Length
        if self.conlength != 0:
            print 'hehe'
            with open(self.filename + self.masur, 'wb+') as f, open("info.txt", 'w') as dw:
                f.write(self.leftover)
                size = len(self.leftover)
                dw.write(info)
                while size < self.conlength:
                    # print "eiei"
                    atad = self.socket.recv(8096)
                    size += len(atad)
                    f.write(atad)
                    # print size
                    dw.write('{}\r\n'.format(size))

        # header without Content-Length
        else:
            print 'hoho'
            with open(self.filename + self.masur, 'wb+') as f, open("info.txt", 'w') as dw:
                f.write(self.leftover)
                dw.write(info)
                while True:
                    # print "eiei", self.conlength
                    buff = self.socket.recv(8096)
                    if not buff:
                        break
                    f.write(buff)

        os.renames(self.filename + self.masur, self.filename)

        f.close()
        print "Data saved"
        self.socket.close()
        sys.exit()

        print "Socket closed"

    def resume(self):
        print "KAO RESUME NA KA"
        buffer = ""
        while True:
            rcv = self.socket.recv(8096)
            if not rcv: break
            buffer += rcv

            if "\r\n\r\n" in buffer:
                self.get_header(buffer)
                forCheck = self.get_fromHeader(self.header)
                print self.header
                self.Oconlength = int(forCheck[0])
                self.OlastMod = forCheck[1]
                self.OETag = forCheck[2]
                # print '{}: {}\r\n{}: {}\r\n{}: {}\r\n'.format('Content-Length', self.conlength, 'Last-Modified', self.lastMod, 'ETag', self.ETag)
                break

        print "yuu nii laew"

        with open(self.filename + self.masur, 'a') as ad, open("info.txt", 'a') as ndw:
            print "kaow pa wa"
            nsize = self.curr_bytes
            # print nsize
            # print self.curr_bytes + self.Oconlength
            # print self.conlength
            # print self.Oconlength
            # total = self.curr_bytes + self
            while nsize < self.curr_bytes + self.Oconlength:
                print "laew nii la"
                # print "eiei"
                atad = self.socket.recv(8096)
                # print atad
                nsize += len(atad)
                ad.write(atad)
                # print size
                ndw.write('{}\r\n'.format(nsize))


        os.renames(self.filename + self.masur, self.filename)

        ad.close()
        print "Data saved"
        self.socket.close()
        sys.exit()

        print "Socket closed"



        # pass

    # for checking that file modified or not
    def check_similar(self):
        # print self.filename + self.masur
        with open("info.txt", 'r') as rd:
            read = rd.read()
            self.curr_bytes = int(read.split("\r\n")[-2])
            # sth = rd.read().split("\r\n")
            # print sth
            # print "Current-bytes: " + self.curr_bytes
            print rd.read()
            old = self.get_fromHeader(read)
            print old
            self.Oconlength = old[0]
            self.OlastMod = old[1]
            self.OETag = old[2]
            # print "Content-Length: " + self.Oconlength
            # print self.OETag,"+", self.OlastMod,"+", self.Oconlength
            # print self.ETag,"+", self.lastMod,"+", self.conlength
        return self.Oconlength == self.conlength and self.OlastMod == self.lastMod and self.OETag == self.ETag



    def get_header(self, sth):
        self.header, self.leftover = sth.split("\r\n\r\n")

    def get_fromHeader(self, header):
        splitted = header.split("\r\n")
        cl = ''
        lm = ''
        et = ''
        for each in splitted:
            # print each
            # if "Content-Length" in each:
            #     word, num = each.split(" ")
            #     # print 'num: ', num
            #     self.conlength = int(num)
            # if "Last-Modified" in each:
            #     word, self.lastMod = each.split(": ")
            # if "ETag" in each:
            #     word, self.ETag = each.split(" ")
            if "Content-Length" in each:
                word, cl = each.split(" ")
                # print cl
                # print 'num: ', num
                # self.conlength = int(num)
            if "Last-Modified" in each:
                word, lm = each.split(": ")
            if "ETag" in each:
                word, et = each.split(" ")
        return cl, lm, et

        # return '{}: {}\r\n{}: {}\r\n{}: {}\r\n'.format('Content-Length', self.conlength, 'ETag', self.ETag, 'Last-Modified', self.lastMod)

        # return vari
                # self.conlength = int(num)

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
            print "Check similarity"
            if not self.check_similar():
                # can resume immediately
                print str(not self.check_similar())+"ror"
                self.make_resume()
                self.resume()
            else:
                # something changed
                print self.check_similar()
                self.download()


            # resume
        else:
            self.make_request()
            # restart
            self.download()
        # self.download()

if __name__ == '__main__':
    input = sys.argv
    download = Downloader()
    download.DocEx(input)