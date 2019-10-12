#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Use text editor to edit the script and type in valid Instagram username/password

from InstagramAPI import InstagramAPI
import urllib.request


def getTotalFollowers(api, user_id):
    """
    Returns the list of followers of the user.
    It should be equivalent of calling api.getTotalFollowers from InstagramAPI
    """

    followers = []
    next_max_id = True
    while next_max_id:
        # first iteration hack
        if next_max_id is True:
            next_max_id = ''

        _ = api.getUserFollowers(user_id, maxid=next_max_id)
        followers.extend(api.LastJson.get('users', []))
        next_max_id = api.LastJson.get('next_max_id', '')
    return followers


if __name__ == "__main__":
    api = InstagramAPI("certafonso", "password")
    api.login()

    # user_id = '1461295173'
    user_id = api.username_id

    # List of all followers
    followers = getTotalFollowers(api, user_id)
    print(followers)
    print('Number of followers:', len(followers))

    followers_usernames = []
    for follower in range(0, len(followers)):
        followers_usernames.append(followers[follower]['username'])
        urllib.request.urlretrieve(followers[follower]['profile_pic_url'], '/Users/admin/Downloads/' + followers_usernames[follower] + '.jpg')

    print(followers_usernames)
