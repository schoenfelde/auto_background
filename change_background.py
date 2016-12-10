#!/usr/bin/python3
from requests import get
import requests.auth
import reddit
from glob import glob
from bs4 import BeautifulSoup
import praw
import re, os
import ctypes
import random

#keep track of our wallpaper loop
count = 0

#Configuration settings
client_id = reddit.config['CLIENT_ID']
client_secret = reddit.config['CLIENT_SECRET']
redirect_uri = reddit.config['REDIRECT_URI']
code = reddit.config['RESPONSE_TYPE']
#Goals: get picture from reddit.com/r/earthporn
#       set picture as background on a timer

def purgeImages(directory,amountToKeep):
    print(directory)
    #images = sorted(os.listdir(r"" + directory), key=os.path.getctime)
    images = os.listdir(r"" + directory)
    print(len(images))
    if len(images) > amountToKeep:
        os.remove(os.path.join(directory, images[-1]))
        purgeImages(directory,amountToKeep)

def setBackground():
    pic_dir = os.path.join(os.getcwd(), 'pictures')
    images = os.listdir(pic_dir)
    count = random.randint(0,9)
    img = os.path.join(pic_dir,images[count])
    SPI_SETDESKWALLPAPER = 20
    print(img)
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, img, 3)

imgurUrlPattern = re.compile(r'(http://i.imgur.com/(.*))(\?.*)?')
def downloadImage(imageUrl, localFileName):
    response = requests.get(imageUrl)
    if not os.path.exists('pictures'):
        os.makedirs('pictures')
    if response.status_code == 200:
        folder = 'pictures'
        image_path = os.path.join(os.getcwd(),'pictures',localFileName)
        print('Downloading %s...' % (localFileName))
        with open(image_path, 'wb') as fo:
            for chunk in response.iter_content(4096):
                fo.write(chunk)

def getImageFromReddit(subreddit):
    r = praw.Reddit(user_agent='Change Background Script',client_id=client_id,client_secret=client_secret)
    for submission in r.subreddit(subreddit).hot(limit=100):
        # Check for all the cases where we will skip a submission:
        print(submission.url)
        if "imgur.com/" not in submission.url:
            continue # skip non-imgur submissions
        if submission.score < 10:
            continue # skip submissions that haven't even reached 100 (thought this should be rare if we're collecting the "hot" submission)
        if len(glob('reddit_%s_*' % (submission.id))) > 0:
            continue # we've already downloaded files for this reddit submission
        if 'http://imgur.com/a/' in submission.url:
            # This is an album submission.
            albumId = submission.url[len('http://imgur.com/a/'):]
            htmlSource = requests.get(submission.url).text
            soup = BeautifulSoup(htmlSource)

            matches = soup.select('.album-view-image-link a')

            for match in matches:

                imageUrl = match['href']

                if '?' in imageUrl:
                    imageFile = imageUrl[imageUrl.rfind('/') + 1:imageUrl.rfind('?')]
                else:
                    imageFile = imageUrl[imageUrl.rfind('/') + 1:]
                localFileName = 'reddit_%s_%s_album_%s_imgur_%s' % (subreddit, submission.id, albumId, imageFile)
                downloadImage('http:' + match['href'], localFileName)

        elif 'http://i.imgur.com/' in submission.url:
            # The URL is a direct link to the image.
            mo = imgurUrlPattern.search(submission.url) # using regex here instead of BeautifulSoup because we are pasing a url, not html
            imgurFilename = mo.group(2)
            if '?' in imgurFilename:
                # The regex doesn't catch a "?" at the end of the filename, so we remove it here.
                imgurFilename = imgurFilename[:imgurFilename.find('?')]

            localFileName = 'reddit_%s_%s_album_None_imgur_%s' % (subreddit, submission.id, imgurFilename)
            downloadImage(submission.url, localFileName)

        elif 'http://imgur.com/' in submission.url:
            # This is an Imgur page with a single image.
            htmlSource = requests.get(submission.url).text # download the image's page
            soup = BeautifulSoup(htmlSource, "html.parser")
            try:
                imageUrl = soup.select('.image a')[0]['href']
                if imageUrl.startswith('//'):
                    # if no schema is supplied in the url, prepend 'http:' to it
                    imageUrl = 'http:' + imageUrl
                imageId = imageUrl[imageUrl.rfind('/') + 1:imageUrl.rfind('.')]

                if '?' in imageUrl:
                    imageFile = imageUrl[imageUrl.rfind('/') + 1:imageUrl.rfind('?')]
                else:
                    imageFile = imageUrl[imageUrl.rfind('/') + 1:]

                localFileName = 'reddit_%s_%s_album_None_imgur_%s' % (subreddit, submission.id, imageFile)
                downloadImage(imageUrl, localFileName)
            except:
                print(soup)
                print(submission.url)

getImageFromReddit('wallpapers')
purgeImages(os.path.join(os.getcwd(), 'pictures'), 50)
setBackground()