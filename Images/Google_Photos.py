"""
This Script handles all the downloads from google photos
"""
from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import random
import sys
import requests
import json

def Setup_API():
    SCOPES = "https://www.googleapis.com/auth/photoslibrary.readonly"
    store = file.Storage("credentials.json")
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets("./Images/token.json", SCOPES)
        creds = tools.run_flow(flow, store)
    service = build("photoslibrary", "v1", http=creds.authorize(Http()))

    return service

def Get_Media_Items(page_token = None, one_page = False):
    """Get list of all Google Photos media items"""

    service = Setup_API()
    result = service.mediaItems().list(pageSize=100, pageToken = page_token).execute()
    items = result.get("mediaItems", [])

    if one_page: return items, result["nextPageToken"]
    else:
        try:
            return items + Get_Media_Items(page_token=result["nextPageToken"])
        except: return items

def Get_media_Items_From_Album(album_id, page_token = None):
    """Get list all of the photos in Google Photos album"""

    service = Setup_API()
    body = {"albumId": album_id, "pageSize": 100, "pageToken": page_token}
    result = service.mediaItems().search(body=body).execute()
    items = result.get("mediaItems", [])

    try:
        return items + Get_media_Items_From_Album(album_id, page_token=result["nextPageToken"])
    except: return items

def Add_to_Blacklist(items):
    """"Adds media ids to blacklist"""

    with open("./Images/Blacklist.txt","w") as Blacklist:
        for item in items:
            Blacklist.write(str(item)+"\n")

def Get_Albums(page_token = None):
    """Get list of all Google Photos albums"""

    service = Setup_API()
    results = service.albums().list(pageSize=50, pageToken=page_token, fields="nextPageToken,albums(id,title)").execute()
    items = results.get("albums", [])
    
    try:
        return items + Get_Albums(page_token=result["nextPageToken"])
    except: return items

def Filter_Albums(albums, keywords):
    """Gets albums that start with key words"""

    items = []

    for album in albums:
        if album["title"].startswith(keywords):
            items.append(album)
    
    return items

def Blacklist_Albums(Albums):
    """Adds all items off albums to the blacklist"""

    blacklist_items = []
    for album in Albums: blacklist_items += Get_media_Items_From_Album(album["id"])

    blacklist_ids = []
    for item in blacklist_items:
        print(item)
        blacklist_ids.append(item["id"])

    Add_to_Blacklist(blacklist_ids)

def Blacklist_from_keywords(keywords):
    """Adds albums that start with keywords to blacklist"""

    Albums = Filter_Albums(Get_Albums(), keywords)
    Blacklist_Albums(Albums)

def List_Valid_Photos():
    """Gets a list of all photos not in blacklist"""

    Blacklist = Import_Blacklist()

    items = Get_Media_Items()

    return Remove_Blacklisted(items, Blacklist)

def Remove_Blacklisted(photo_list, Blacklist):
    """Removes blacklisted photos from a list"""

    for item in photo_list:
        if item["id"] in Blacklist: photo_list.remove(item)

    return photo_list

def Import_Blacklist(path = "./Images/Blacklist.txt"):
    """Imports blacklist from file"""

    Blacklist = []
    with open(path,"r") as file:
        for line in file: Blacklist.append(line)

    return Blacklist

def Import_Valid_Photos(path = "./Images/Valid_photos.json"):
    """Imports valid photos from JSON file"""

    with open(path, "r") as photo_file:
        valid_photos = json.load(photo_file)

    return valid_photos

def Save_Valid_Photos():
    """Saves valid photos to json"""

    Save_Photos(List_Valid_Photos(), "./Images/Valid_photos.json")

def Save_Photos(photo_list, path):
    """Saves photos to a JSON file"""

    with open(path, "w") as f:
        json.dump(photo_list, f)

def Check_New_Photos(photofile = "./Images/Valid_photos.json"):
    """Checks if there is new photos in google photos and saves them to the json file"""

    next_page_token = None
    valid_photos = Import_Valid_Photos()
    new_valid_photos = []
    done = False
    items = []

    while not done:
        new_valid_photos += items
        items, next_page_token = Get_Media_Items(page_token=next_page_token, one_page=True)
        for i in range(0, len(items)):
            if items[i]["id"] != valid_photos[0]["id"]: # detects photos not in list
                new_valid_photos.append(items[i])
            else: #detects first photo of list
                done = True
                break

    blacklist = Import_Blacklist()

    if new_valid_photos != []:
        valid_photos = Remove_Blacklisted(new_valid_photos+valid_photos, blacklist)

        Save_Photos(valid_photos, photofile)

def Download_Photos(photos=[]):
    """Download photos from Google Photos"""

    output = []

    length = len(photos)
    for i, photo in enumerate(photos):
        sys.stdout.write('\r')
        sys.stdout.write('downloading: %s/%s' % (i+1, length))
        sys.stdout.flush()
        url = photo['baseUrl']
        r = requests.get(url)
        if r.status_code == 200:
            with open("./Images/" + photo['filename'], 'wb') as f:
                for chunk in r.iter_content(1024*2014):
                    f.write(chunk)
            output.append(photo['filename'])
        else:
            return 1
    sys.stdout.write('\n')
    sys.stdout.flush()
    return output

def Download_Random_Photo(photo_list):
    """Download random photo from a list"""

    photo = random.choice(photo_list)
    return Download_Photos([photo]), photo["id"]

Check_New_Photos()