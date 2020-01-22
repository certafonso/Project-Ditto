"""
This Script handles all the downloads from google photos
"""
from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

def Setup_API():
    SCOPES = "https://www.googleapis.com/auth/photoslibrary.readonly"
    store = file.Storage("credentials.json")
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets("./Images/token.json", SCOPES)
        creds = tools.run_flow(flow, store)
    service = build("photoslibrary", "v1", http=creds.authorize(Http()))

    return service

def Get_Media_Items(page_token = None):
    """Get list of all Google Photos media items"""

    service = Setup_API()
    result = service.mediaItems().list(pageSize=100, pageToken = page_token).execute()
    items = result.get("mediaItems", [])

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

    Blacklist = []
    with open("./Images/Blacklist.txt","r") as file:
        for line in file: Blacklist.append(line)

    items = Get_Media_Items()

    for item in items:
        if item["id"] in Blacklist: items.remove(item)

    return items


if __name__=="__main__":

    a = open("a.txt","w")

    for item in List_Valid_Photos():
        a.write(item["id"])
