# ftp-flask
a simple FTP server made using flask

#### Setting up
+ Edit main.py, at bottom of the file, replace serve()'s arguments with your own IP/Port (use WSGI if need access outside of LAN; See [here](http://flask.pocoo.org/docs/1.0/deploying/) for more details)
+ Then make sure you installed **flask**, **colorama**, **magic** (if not install using "pip install flask colorama python-magic")
+ then run the python file

#### Changing ftp directory
+ Under ./static/ftpFiles/ is where the shared file will be stored by default
+ to change the file store location: Edit main.py look for serve() function and replace the optional argument "ftpDir" to your desire (This location must be under "./static/")

#### Troubleshooting
+ **The requested address is not valid in its context.** is caused by using an address that is not assigned to your network, check your current binding address is correct and try again
+ **Not able to access from other devices?** check if your firewall is blocking any inbound/outbound requests. if you are not able to access from an external network, check if you set up your WSGI server correctly
+ **ImportError: failed to find libmagic. Check your installation** is caused by incomplete python-magic installation, do "pip install libmagic FFMPEG" and try again, if problem persists try to download .whl file from [here](https://pip.aws.lolatravel.com/pip/dev/+simple/python-magic-bin) select the platform you needed and install. (Detailed install instructions can be found [here](https://stackoverflow.com/questions/27885397/how-do-i-install-a-python-package-with-a-whl-file))

##### TODO
+ Add ability to upload file 
+ <del>Add ability to view file details</del>
