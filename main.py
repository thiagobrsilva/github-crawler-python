"""
Script to connect to GitHub website and copy some information about users called followed,
and users that follow those first users, called followers.
"""

import urllib.request
import os.path
from bs4 import BeautifulSoup
from requests import session
from model.item import Person, Follower, Detail

# Download settings
path_file = os.path.dirname(os.path.abspath(__file__))+"/downloads/"
users_file = ""

user_list = []

# Find "users" of this languages
lang_list = ["java", "python", "node"]

# Limit of users -> followed and followers
max_user = 2

# Main function, connect to github page that shows users with most followers for each language
def start():

    for item in lang_list:
        aux_url = r"https://github.com/search?o=desc&q=" + item + "&s=followers&type=Users"

        # Create a file for every language defined in lang_list
        aux_path = path_file + item + "_userList.txt"

        if (os.path.exists(path_file)==False):
            os.mkdir(path_file)

        try:
            users_file = open(aux_path, "w")
            users_file.write("Followed_username;Followed_image;Followed_repositories;Followed_stars;Follower_username;Follower_image;Follower_repositories;Follower_stars"+"\n")

        except IOError as e:
            print("[Error] Create file:" + format(e.errno, e.strerror))

        response = session().get(aux_url)

        parse_users(response, item, users_file)

        # Clear user_list to receive users from the next language
        user_list.clear()


# Generate a file with users name and download profile image
def parse_users(response, lang, users_file):

    soup = BeautifulSoup(response.content, "html.parser")
    images = soup.find_all("img", {"class": "avatar"})

    i = 0
    for image in images:

        # limit of users
        if (i==max_user):
            break

        # create a person with information from github. Removing @ from username
        person = Person()
        person.username = image.get("alt")
        person.username = person.username.replace("@", "")
        person.image = image.get("src")

        if (os.path.exists(path_file)==False):
            os.mkdir(path_file)

        # Download user profile image
        try:
            aux_image_file = path_file + r"images/" + lang + "_followed_" + person.username + ".jpg"
            f = open(aux_image_file, 'wb')
            f.write(urllib.request.urlopen(person.image).read())
            f.close()
        except IOError as e:
            print("[Error] Download image file:" + format(e.errno, e.strerror))

        # Add username to user_list
        user_list.append(person.username)

        i += 1

    parse_followers(lang, user_list, users_file, aux_image_file)


# Look for followers inside user_list
def parse_followers(lang, list, users_file, user_image):
    for item in user_list:
        aux_url = r"https://github.com/" + item + "?tab=followers"

        response = session().get(aux_url)

        soup = BeautifulSoup(response.content, "html.parser")
        images = soup.find_all("img", {"class": "avatar"})

        i=0
        for image in images:
            aux_class = image.get("class")

            # Testing if the class name is only avatar, because in some cases the class value is avatar ****
            if (len(aux_class)==1):

                # limit of users
                if (i == max_user):
                    break

                follower = Follower()
                follower.followed = item
                follower.username = image.get("alt")
                follower.username = follower.username.replace("@", "")
                follower.image = image.get("src")
                follower.link = "https://github.com/" + follower.username

                # download profile image
                try:
                    aux_img = lang + "_" +follower.followed + "_follower_" + follower.username + ".jpg"
                    f = open(path_file + r"/images/" + aux_img, 'wb')
                    f.write(urllib.request.urlopen(follower.image).read())
                    f.close()
                except IOError as e:
                    print("[Error] Download image file error:" + format(e.errno, e.strerror))

                detail_followed = get_details(follower.followed)
                detail_follower = get_details(follower.username)
                # file with users
                try:
                    users_file.write(
                        follower.followed + ";" + user_image + ";" + str(detail_followed.repositories) + ";" + str(detail_followed.stars) + ";" +
                        follower.username + ";" + aux_img + ";" + str(detail_follower.repositories) + ";" + str(detail_follower.stars) +"\n")
                except IOError as e:
                    print("[Error] Write text file:" + format(e.errno, e.strerror))

                i += 1

# Number of repositories and stars
def get_details(user):
    det = Detail()
    aux_url = r"https://github.com/" + user
    response = session().get(aux_url)
    soup = BeautifulSoup(response.content, "html.parser")

    for link in soup.findAll('a'):
        link_href = link.get("href")

        if (link_href=="/" + user + "?tab=repositories"):
            sp = link.findNext('span', attrs={'class':'counter'})
            aux_rep = sp.contents[0]
            aux_rep = aux_rep.replace(" ","")
            aux_rep = aux_rep.replace("\n", "")
            det.repositories = aux_rep

        if (link_href == "/" + user + "?tab=stars"):
            sp = link.findNext('span', attrs={'class': 'counter'})
            aux_star = sp.contents[0]
            aux_star = aux_star.replace(" ", "")
            aux_star = aux_star.replace("\n", "")
            det.stars = aux_star

    return det

if __name__ == "__main__":
    start()