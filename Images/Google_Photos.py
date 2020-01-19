"""
Shows basic usage of the Photos v1 API.

Creates a Photos v1 API service and prints the names and ids of the last 10 albums
the user has access to.
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

def get_media_items(page_token = None):
    """Get list of all Google Photos media items"""

    service = Setup_API()
    result = service.mediaItems().list(pageSize=100, pageToken = page_token).execute()
    items = result.get("mediaItems", [])

    try:
        return items + get_media_items(page_token=result["nextPageToken"])
    except: return items

def get_media_items_from_album(album_id, page_token = None):
    """Get list all of the photos in Google Photos album"""

    service = Setup_API()
    body = {"albumId": album_id, "pageSize": 100, "pageToken": page_token}
    result = service.mediaItems().search(body=body).execute()
    items = result.get("mediaItems", [])

    try:
        return items + get_media_items_from_album(album_id, page_token=result["nextPageToken"])
    except: return items

def Add_to_Blacklist(items):
    with open("./Images/Blacklist.txt","w") as Blacklist:
        for item in items:
            Blacklist.write(str(item)+"\n")

def List_Albums(page_token = None):
    service = Setup_API()
    results = service.albums().list(pageSize=50, pageToken=page_token).execute()
    items = results.get("albums", [])
    if not items:
        print("No albums found.")
    else:
        print("Albums:")
        for item in items:
            print("{0} ({1})".format(item["title"], item["id"]))
    
    try: List_Albums(page_token=results[nextPageToken])
    except:pass

def Blacklist_Albums(Albums):
    blacklist_items = []
    for album in Albums: blacklist_items.append(get_media_items_from_album(album))

    Add_to_Blacklist(Blacklist_Albums)