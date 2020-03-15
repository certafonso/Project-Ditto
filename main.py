import Images.Google_Photos as Google_Photos
import Images.Image_Processing as Image_Processing
from Captions.Generate_Caption import generate_caption
import Email_Controller
import instaloader
from instaloader import Profile
import time
import os

def DownloadPosts(Username):
    """Download Instagram Posts"""

    # Get instance
    L = instaloader.Instaloader()

    profile = Profile.from_username(L.context, Username)

    for post in profile.get_posts():  # Downloads all posts of username
        if not L.download_post(post, target=profile.username):
            break

    return True

def DeleteFile(path):
    """Deletes a file"""

    if os.path.exists(path):
        os.remove(path)

def LoadConfig(config_path = "./Config.json"):
    return Google_Photos.Import_JSON(config_path)

def SaveConfig(config, config_path = "./Config.json"):
    return Google_Photos.Save_JSON(config, config_path)

def NotifyError(function, ex):
    """Sends an email when an exception occurs"""

    msg = "\n{t} \n{ex}".format(t = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), ex = ex)

    Email_Controller.SendEmail(config["Control Email"]["username"],
                               config["Control Email"]["password"], 
                               config["Control Email"]["receiver"],
                               "Error in {function}".format(function=function),
                               msg)

def NotifyCommand(command):
    """Sends an email when a command is executed"""

    msg = "\n{t} \n".format(t = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))

    msg += "Command id: {id}\n".format(id = command["id"])

    msg += "Type: {typ}\n".format(typ = command["Type"])

    if command["Type"] == "post": msg += "Post id: {id}\n".format(id = command["PostID"])

    msg += "Command: {com}\n".format(com=command["Command"])

    msg += "Argument: {arg}\n".format(arg=command["Argument"])

    Email_Controller.SendEmail(config["Control Email"]["username"],
                               config["Control Email"]["password"], 
                               config["Control Email"]["receiver"],
                               "Executed {com}".format(com=command["Command"]),
                               msg)

def UpdateData():
    """Will update data from all sources"""

    try:
        DownloadPosts(config["Origin"]["username"])
        Image_Processing.ProcessNewData("./{username}".format(username=config["Origin"]["username"]))
        Google_Photos.Check_New_Albums(keywords=config["Google Photos"]["Keywords"])
        Google_Photos.Check_New_Photos()
    except Exception as ex:
        NotifyError("UpdateData", ex)

def CreatePost():
    """Downloads a random photo, edits it and creates captions for a post (this function doesn't handle errors)"""

    img = Google_Photos.Download_Random_Photo(Google_Photos.Import_JSON("./Images/Valid_photos.json"))
    print("img",img)
    post = {
        "PostID": len(Google_Photos.Import_JSON("./PostHistory.json")),
        "Caption":{
            "Options": generate_caption(),
            "Choice": None
        },
        "Image":{
            "Id": img[1],
            "Original": img[0][0],
            "Edited": img[0][0] + "_edited.jpg"
        },
        "Date Generated": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "Published": False,
        "Date Published": None
    }

    Image_Processing.EditImage(post["Image"]["Original"])

    AddToPostHistory(post)

    return post

def SendPost(post):
    """Sends a post by email"""

    try:
        sub = "Project Ditto Post {id}".format(id = post["PostID"])

        msg = "\r\nDate Generated: {date} \r\n".format(date = post["Date Generated"])

        if post["Published"]: msg += "Date Published: {date} \r\n".format(date = post["Date Published"])
        else: msg += "Not Published \r\n"

        msg += "Caption Options (Choosed {choice}): \r\n".format(choice = post["Caption"]["Choice"])
        for i in range(0, len(post["Caption"]["Options"])):
            msg += "\r\n{n}: \"{Caption}\"".format(n = i, Caption = post["Caption"]["Options"][i])

        msg += "\r\n Reply \"Publish [choice]\" to publish"
        msg += "\r\n Reply \"Newphoto\" to get a new photo"
        msg += "\r\n Reply \"Morecaptions\" to get more captions"

        try:
            Email_Controller.SendWithAttachment(config["Control Email"]["username"],
                                    config["Control Email"]["password"], 
                                    config["Control Email"]["receiver"],
                                    sub,
                                    msg,
                                    post["Image"]["Edited"])
        except:
            Email_Controller.SendEmail(config["Control Email"]["username"],
                                    config["Control Email"]["password"], 
                                    config["Control Email"]["receiver"],
                                    sub,
                                    msg)
    except Exception as ex:
        NotifyError("SendPost", ex)

def AddToPostHistory(post):
    """Adds a post to the PostHistory.json file"""

    History = Google_Photos.Import_JSON("./PostHistory.json")

    History.append(post)

    Google_Photos.Save_JSON(History, "./PostHistory.json")

def PublishPost(postid, choice):
    """Changes post in PostHistory.json to be published"""

    History = Google_Photos.Import_JSON("./PostHistory.json")

    if History[postid]["Published"]:
        NotifyError("PublishPost", "The post was already published")
    else:
        History[postid]["Published"] = True
        History[postid]["Date Published"] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        History[postid]["Caption"]["Choice"] = choice

        DeleteFile(History[postid]["Image"]["Original"])
        DeleteFile(History[postid]["Image"]["Edited"])
        
        Google_Photos.Save_JSON(History, "./PostHistory.json")

def ChangePhoto(postid):
    """Changes the photo of an existing post"""

    History = Google_Photos.Import_JSON("./PostHistory.json")

    if History[postid]["Published"]:
        NotifyError("ChangePhoto", "The post you're trying to change was already published")
    else:
        DeleteFile(History[postid]["Image"]["Original"])
        DeleteFile(History[postid]["Image"]["Edited"])
    
        img = Google_Photos.Download_Random_Photo(Google_Photos.Import_JSON("./Images/Valid_photos.json"))

        History[postid]["Image"] = {
                "Id": img[1],
                "Original": img[0][0],
                "Edited": img[0][0] + "_edited.jpg"
            }

        Image_Processing.EditImage(History[postid]["Image"]["Original"])   
        
        Google_Photos.Save_JSON(History, "./PostHistory.json")

        SendPost(History[postid])

def AddCaptions(postid):
    """Generates new captions for a post"""

    History = Google_Photos.Import_JSON("./PostHistory.json")

    if History[postid]["Published"]:
        NotifyError("ChangePhoto", "The post you're trying to change was already published")
    else:
        History[postid]["Caption"]["Options"] += generate_caption()
        
        Google_Photos.Save_JSON(History, "./PostHistory.json")

        SendPost(History[postid])

def ForcePost():
    """Creates a new post and sends it"""

    History = Google_Photos.Import_JSON("./PostHistory.json")

    if History[-1]["Published"]: # if last post was published creates a new one
        post = CreatePost()
    else: # if not, resends last one
        post = History[-1]

    SendPost(post)

    config["Times"]["Next Post"] = t + config["Times"]["Post period"]

def CheckCommands():
    """Executes new commands. Returns the executed command"""

    CommandLog = Google_Photos.Import_JSON("CommandLog.json")

    mail = Email_Controller.GetLastMail(config["Control Email"]["username"], config["Control Email"]["password"])

    if int(mail["id"]) == CommandLog[-1]["id"]: # there are no new commands
        return None

    elif config["Control Email"]["receiver"] in mail["from"]: # last mail was sent by the right email
        if "Re: Project Ditto Post" in mail["subject"]: #mail concerns a post
            body = mail["body"].split()

            command = { # commands concerning posts have command as first word of body and argument as second word
                "id": int(mail["id"]),
                "Type": "post",
                "Command": body[0],
                "Argument": body[1],
                "PostID": int(mail["subject"][-1])
            }
            if command["Command"] == "Publish": 
                PublishPost(command["PostID"], command["Argument"])

            elif command["Command"] == "Newphoto":
                ChangePhoto(command["PostID"])

            elif command["Command"] == "Morecaptions":
                AddCaptions(command["PostID"])

            else:
                NotifyError("CheckCommands", "Unknown command: {command}".format(command = command["Command"]))

        else:
            body = mail["body"].split()

            command = { # general commands command as subject and argument as body
                "id": int(mail["id"]),
                "Type": "general",
                "Command": mail["subject"].split()[0],
                "Argument": None
            }
            try: command["Argument"] = mail["body"].split()[0]
            except: pass
            
            if command["Command"] == "Lastpost":
                Last_post = Google_Photos.Import_JSON("./PostHistory.json")[-1]
                SendPost(Last_post)

            elif command["Command"] == "Forcepost":
                ForcePost()

        CommandLog.append(command)

        Google_Photos.Save_JSON(CommandLog, "CommandLog.json")
        return command
        
    else: 
        return None

if __name__ == "__main__":
    config = LoadConfig()
    
    while True:
        t = time.time()

        command = CheckCommands()

        if command != None: NotifyCommand(command)

        if t >= config["Times"]["Next Update"]: # if time is right updates data
            UpdateData()

            config["Times"]["Next Update"] = t + config["Times"]["Update period"]

        if t >= config["Times"]["Next Post"]: # if time is right creates a new post
            ForcePost()

        SaveConfig(config)

        time.sleep(1)
            
