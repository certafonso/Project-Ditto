#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Use text editor to edit the script and type in valid Instagram username/password

from InstagramAPI import InstagramAPI

api = InstagramAPI("certafonso", "KriFryofGoa3")
if (api.login()):
    api.getTotalSelfUserFeed()  # get self user feed
    UserFeed = api.LastJson
    print(UserFeed)
    print("Login succes!")
else:
    print("Can't login!")
