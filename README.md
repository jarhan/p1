# data_com
Data Com Project 1

To run this program, go to the directory of this program by terminal, then:

./srget -o [saved_file_name] [Address]

where saved_file_name is your desired file's name to download and address including http.

This program works with http only. And the program would report the program status continously such as connecting to server, starting download file or starting resume download.

If the download is not finished/got canceled, it will save as .LYdownload and extra file info.txt

* If you want to resume the download in the future, please DO NOT DELETE those two files
If the file has been damgaged, inluding the extra files indicating above, it will print out on screen and restart the download

To resume the download, run the program similar to the first time you run it

This program does not support chunk-encoding transfer

If the file has been updated, it will be printed out on screen
