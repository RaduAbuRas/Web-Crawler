#Main processing module. It takes care of the whole process of saving a page offline

from bs4 import BeautifulSoup
from itertools import repeat
from validators import url as IsUrlValid
from requests import Session as requests_session

import Constants
import Utils

import os, sys
import concurrent.futures

# Contains a map with links at each level (root page is level 0) as such:
# 0: [root]
# 1: [link 1, link 2]
# 2: [link 3, link 6, link 7]
# This dictionary does not allow duplicates so that the same page isn't downloaded multiple times (e.g. home page is present on multiple pages)
linksDepthMap = {}

# Root folder of each page, this will contain all the sub pages including the root one
outputWebFolder = ''

# Used to prevent saving the links of the next level while parsing a page on the last level
totalDepth = 0;

requestsSession = requests_session()

def crawlWebsite(url, crawlDepth): 
    # The given URL should be the root
    linksDepthMap[0] = [url]
    
    # Compute the root output folder for each application run
    global outputWebFolder
    outputWebFolder = Utils.computeAlphaNumericalString(url)

    global totalDepth
    totalDepth = crawlDepth

    # Each link from each level is parsed and saved on a different thread
    # The application waits for each level to be completely finished before moving to the next one
    for currentDepthLevel in range(crawlDepth):
        # Get all the links at the current depth
        links = linksDepthMap[currentDepthLevel]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(crawlPage, links, repeat(currentDepthLevel, len(links)))
	
	# Close requests connection
    requestsSession.close()
    
    
def crawlPage(url, depthLevel):
    if not IsUrlValid(url):
        print('Invalid Link')
        return
        
    # Get page html source code
    pageSource = requestsSession.get(url)
    # Create beautifulsoup object fom html sorce code
    soup = BeautifulSoup(pageSource.text, 'html.parser')
    
    #Extract links to map for the next level (skip if currently at last level)
    if depthLevel + 1 < totalDepth:
        addLinksFromPageToMap(soup, depthLevel)

    # Alter <A Href> links with the values that will be saved on the disk in the next depth level
    alterAHtmlLinks(soup)

    # Save the page html on disk
    savePageOnDisk(soup, pageSource.url)
    

def linkExistsInMap(link):
    # Check all levels (e.g. home page can be found on all sub pages)
    for linkList in linksDepthMap.values():
        if link in linkList:
            return True

    return False

            
def savePageOnDisk(soup, url):
    # Get alpha numerical page title
    alphaNumUrl = Utils.computeAlphaNumericalString(url)

    # Create file
    outputFolder = Constants.kOutputFolder + Constants.kDirSeparator + outputWebFolder + Constants.kDirSeparator + alphaNumUrl
    htmlFileName = outputFolder + Constants.kDirSeparator + alphaNumUrl + Constants.kHtmlFileEnding
    os.makedirs(os.path.dirname(htmlFileName), exist_ok=True)
    
    # Save 
    srcFolder = outputFolder + Constants.kDirSeparator + alphaNumUrl + Constants.k_files
    if not os.path.exists(srcFolder):
        os.mkdir(srcFolder)
       
    # Download content from page and modify the link value to the saved file link
    downloadAndAlterPageContent(srcFolder, soup, Constants.kHtmlTagImg, Constants.kHtmlInnerSrc)
    downloadAndAlterPageContent(srcFolder, soup, Constants.kHtmlTagImg, Constants.kHtmlInnerDataSrc)
    downloadAndAlterPageContent(srcFolder, soup, Constants.kHtmlTagLink, Constants.kHtmlInnerHref)
    downloadAndAlterPageContent(srcFolder, soup, Constants.kHtmlTagScript, Constants.kHtmlInnerSrc)
    
    # Save html source code in the file
    with open(htmlFileName, "w", encoding="utf-8") as file:
        file.write(soup.prettify())
        file.close()
       
       
def addLinksFromPageToMap(soup, depthLevel):
    # Add non-duplicate links to the links depth map on the next level
    for link in soup.find_all('a', href=True):
        if not linkExistsInMap(link[Constants.kHtmlInnerHref]):
            linksDepthMap.setdefault(depthLevel + 1,[]).append(link[Constants.kHtmlInnerHref])

def alterAHtmlLinks(soup):
    # Get all <a href> links from the current page and modify their value to the new structure
    for link in soup.find_all('a', href=True):
        alphaNumTitle = Utils.computeAlphaNumericalString(link[Constants.kHtmlInnerHref])
        newVal = '..' + Constants.kDirSeparator + alphaNumTitle + Constants.kDirSeparator + alphaNumTitle + Constants.kHtmlFileEnding
        link[Constants.kHtmlInnerHref] = newVal


def downloadAndAlterPageContent(pagefolder, soup, tag, inner):
    for res in soup.findAll(tag):   # images, css, etc..
        try:
            fileName = os.path.basename(res[inner])
            # Res[inner] # may or may not exist 
            filePath = os.path.join(pagefolder, fileName)
            newResVal = os.path.basename(pagefolder) + Constants.kDirSeparator + fileName
            # Copy inner value before altering it
            fileToSave = res[inner]
            # Alter tag inner value to the locally saved content
            res[inner] = newResVal
            if not os.path.isfile(filePath): # Has not been downloaded
                with open(filePath, 'wb') as file:
                    fileBin = requestsSession.get(fileToSave)
                    file.write(fileBin.content)
        except Exception as exc:      
            print(exc, file=sys.stderr)
