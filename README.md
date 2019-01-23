# fileshare-flask
A simple file sharing program based on HTTP using flask

#### Setting up
+ Edit main.py, at bottom of the file, replace serve()'s arguments with your own IP/Port (use WSGI if need access outside of LAN; See [here](http://flask.pocoo.org/docs/1.0/deploying/) for more details)
+ Make sure you have installed **flask**, **colorama**, **magic** (if not install using "pip install flask colorama python-magic-bin") linux user install magic by "pip install python-magic"
+ Then run the python file main.py

#### Changing file sharing directory
+ Under ./static/ftpFiles/ is where the shared file will be stored by default
+ to change the file store location: Edit main.py look for serve() function and replace the optional argument "ftpDir" to your desire (This location must be under "./static/")

#### Troubleshooting
+ **The requested address is not valid in its context.** is caused by using an address that is not assigned to your network, check your current binding address is correct and try again
+ **Not able to access from other devices?** check if your firewall is blocking any inbound/outbound requests. if you are not able to access from an external network, check if you set up your WSGI server correctly
+ **ImportError: failed to find libmagic. Check your installation** is caused by incomplete python-magic installation, do "pip install libmagic FFMPEG" and try again, if problem persists try to download .whl file from [here](https://pip.aws.lolatravel.com/pip/dev/+simple/python-magic-bin) select the platform you needed and install. (Detailed install instructions can be found [here](https://stackoverflow.com/questions/27885397/how-do-i-install-a-python-package-with-a-whl-file))

#### API
##### Listing Dirctories
+ send POST request to the path you want to list. If the path exists the remote will return a JSON contains  
{"FILENAME": ["FileURLPath", IsTheFileADirectory]} **FILENAME** and **FileURLPath** is string and **IsTheFileADirectory** is a boolean  
##### Get File Details
+ send POST request to /ShowFileDetail with JSON that contains {"FILENAME": "", "PATH": ""}. The server will return JSON that contains a list of file properties if the file exists.  
JSON response example:  
{  
"file_name": "Helloworld.py",  
"file_ext": ".py",  
"file_path": "/pythonfiles/",  
"last_mod": Wed Dec 26 18:10:00 2018',  
"created": Wed Dec 26 18:06:00 2018',  
"file_size": 50492,  
"file_content_type": "Python Script",  
"full_detail": "Python script, ASCII text executable, with CRLF line terminators",  
"location": "/pythonfiles/Helloworld.py"  
}  
file_size: in **bytes**, last_mod and created date may not be accurate
##### Uploading files
+ Uploading files by sending a POST request to /Upload with a url parameter dst (dst must be a directory and encoded) with file stream 
+ **Post to URL look like this: "/Upload?dst=%2F"** where %2F is encoded form of "/"

##### TODO
+ Add Permission
+ <del>Add ability to upload file </del>
+ <del>Code cleanup/Refactor</del>
+ <del>Add comments</del>
+ <del>Add file listing API</del>
+ <del>Add ability to view file details</del>

#### UI Preview
![UIPreviewMainSmall](https://i.imgur.com/n0z58ym.png)
![UIPreviewFileDetailsSmall](https://i.imgur.com/MUF0QxG.png)
