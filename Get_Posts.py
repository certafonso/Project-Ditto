###################################################
# This script will download the necessary things  #
# to put on the machine learning models           #
###################################################

import instaloader
from instaloader import Profile


def DownloadPosts(Username):
    # Get instance
    L = instaloader.Instaloader()

    profile = Profile.from_username(L.context, Username)

    for post in profile.get_posts():  # Downloads all posts of username
        L.download_post(post, target=profile.username)

    return True


if __name__ == "__main__":
    DownloadPosts("certafonso")
