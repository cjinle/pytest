#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
google drive upload file
"""


from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# gauth = GoogleAuth()
# gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication

gauth = GoogleAuth()
drive = GoogleDrive(gauth)

file1 = drive.CreateFile({'title': 'Hello.txt'})  # Create GoogleDriveFile instance with title 'Hello.txt'
file1.SetContentString('Hello World!') # Set content of the file from given string
file1.Upload()