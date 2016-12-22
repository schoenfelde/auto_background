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

#Configuration settings
client_id = reddit.config['CLIENT_ID']
client_secret = reddit.config['CLIENT_SECRET']

def purgeImages(directory,amountToKeep):
    '''
    Purge any images from the picture director that
    are over the amount we decide to keep
    '''

    print(directory)
    images = os.listdir(r"" + directory)
    print(len(images))
    #if we have more than our purge amount
    #then we continue with the purge 
    if len(images) > amountToKeep:
        os.remove(os.path.join(directory, images[-1]))
        purgeImages(directory,amountToKeep)

def setBackground():
    '''
    Currently works on windows 10 as 
    means to set your desktop background 
    permanently and immediately
    will choose a random image in your directory
    '''

    pic_dir = os.path.join(os.getcwd(), 'pictures')
    images = os.listdir(pic_dir)
    count = random.randint(0,len(images))
    img = os.path.join(pic_dir,images[count])
    SPI_SETDESKWALLPAPER = 20
    print(img)
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, img, 3)

#regex pattern for URL matching
imgurUrlPattern = re.compile(r'(http://i.imgur.com/(.*))(\?.*)?')
redditUrlPattern = re.compile(r'(https://i.redd.it/(.*))(\?.*)?')

def downloadImage(imageUrl, localFileName):
    '''
    Download the image
    '''

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
    '''
    get immages from the subreddit input 
    that will be used as background images
    '''

    #connect to the reddit api
    r = praw.Reddit(user_agent='Change Background Script',client_id=client_id,client_secret=client_secret)

    #using PRAW, order by hot and only look at the top 10
    for submission in r.subreddit(subreddit).hot(limit=100):
        # Check for all the cases where we will skip a submission:
        print(submission.url)
        if "imgur.com/" not in submission.url and "redd" not in submission.url:
            print("Skipping because imgur or redd not in submission.url")
            continue # skip non-imgur submissions

        if submission.score < 10:
            print("Skipping because the submission score is under 10")
            continue # skip submissions that haven't even reached 100 (thought this should be rare if we're collecting the "hot" submission)

        if len(glob('reddit_%s_*' % (submission.id))) > 0:
            print("this is already downloaded, do not download again")
            continue # we've already downloaded files for this reddit submission

        if 'redd' in submission.url:
            #download reddit hosted images
            try:
                mo = redditUrlPattern.search(submission.url)
                imgurFilename = mo.group(2)
                localFileName = 'reddit_%s_%s_album_None_imgur_%s' % (subreddit, submission.id, imgurFilename)
                downloadImage(submission.url,localFileName)
            except:
                print('error getting reddit search regex')

        if 'http://imgur.com/a/' in submission.url:
            # This is an album submission.
            print("this is an album submission")
            albumId = submission.url[len('http://imgur.com/a/'):]
            htmlSource = requests.get(submission.url).text
            soup = BeautifulSoup(htmlSource,"html.parser")

            matches = soup.select('.album-view-image-link a')

            for match in matches:
                print("imgur match: " + match)

                imageUrl = match['href']

                if '?' in imageUrl:
                    imageFile = imageUrl[imageUrl.rfind('/') + 1:imageUrl.rfind('?')]
                else:
                    imageFile = imageUrl[imageUrl.rfind('/') + 1:]
                localFileName = 'reddit_%s_%s_album_%s_imgur_%s' % (subreddit, submission.id, albumId, imageFile)
                downloadImage('http:' + match['href'], localFileName)

        elif 'http://i.imgur.com/' in submission.url:
            # The URL is a direct link to the image.
            print("direct link")
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
                #Printing the submission url, gives us insight on where we are failing to improve the process
                print('Could not parse the beautiful soup')
                print(submission.url)
        else:
            print("Could not parse the link")


if __name__ == '__main__':
    '''
    If this program is the main program call
    all of the functions to get the images, 
    set the background, and purge old images
    '''

    print("***********************************")
    print("Beginning Change Background ")
    print("***********************************")

    #Do not stop processing if you cannot access reddit
    #Still choose a new background
    try:
        getImageFromReddit('wallpapers')
    except:
        print('Error getting the image from Reddit')
    try:
        purgeImages(os.path.join(os.getcwd(), 'pictures'), 50)
    except:
        print('Error purgin images')

    setBackground()
    print("DONE")