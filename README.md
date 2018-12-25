# ftp-flask
a simple FTP server made using flask

#### Setting up
+ Edit main.py, at bottom of the file, replace serve()'s arguments with your own IP/Port (use WSGI if need access outside of LAN; See [here](http://flask.pocoo.org/docs/1.0/deploying/) for more details)
+ Then make sure you installed **flask** and **colorama** library (if not install using "pip install flask colorama")
+ then run the python file

#### Troubleshooting
+ **The requested address is not valid in its context.** is caused by using an address that is not assigned to your network, check your current binding address is correct and try again
+ **Not able to access from other devices?** check if your firewall is blocking any inbound/outbound requests. if you are not able to access from an external network, check if you set up your WSGI server correctly

#### Changing ftp dirctory
+ Under ./static/ftpFiles/ is where the shared file will be stored
+ to change the file store location: Edit main.py look for change_dir() function and replace the optional argument "default_ftp_location" to your desire (This location must under "./static/")

##### TODO
+ Add ability to upload file 
+ Add ability to view file details
