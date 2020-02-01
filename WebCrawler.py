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

def crawl_website(url, crawl_depth): 
    # The given URL should be the root
    linksDepthMap[0] = [url]
    
    # Compute the root output folder for each application run
    global outputWebFolder
    outputWebFolder = Utils.compute_alpha_numerical_string(url)

    global totalDepth
    totalDepth = crawl_depth

    # Each link from each level is parsed and saved on a different thread
    # The application waits for each level to be completely finished before moving to the next one
    for current_depth_level in range(crawl_depth):
        # Get all the links at the current depth
        links = linksDepthMap[current_depth_level]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(crawl_page, links, repeat(current_depth_level, len(links)))
	
	# Close requests connection
    requestsSession.close()
    
    
def crawl_page(url, depth_level):
    if not IsUrlValid(url):
        print('Invalid Link')
        return
        
    # Get page html source code
    page_source = requestsSession.get(url)
    # Create beautifulsoup object fom html sorce code
    soup = BeautifulSoup(page_source.text, 'html.parser')
    
    #Extract links to map for the next level (skip if currently at last level)
    if depth_level + 1 < totalDepth:
        add_links_from_page_to_map(soup, depth_level)

    # Alter <A Href> links with the values that will be saved on the disk in the next depth level
    alter_a_html_links(soup)

    # Save the page html on disk
    save_page_on_disk(soup, page_source.url)
    

def link_exists_in_map(link):
    # Check all levels (e.g. home page can be found on all sub pages)
    for link_list in linksDepthMap.values():
        if link in link_list:
            return True

    return False

            
def save_page_on_disk(soup, url):
    # Get alpha numerical page title
    alpha_num_url = Utils.compute_alpha_numerical_string(url)

    # Create file
    output_folder = Constants.koutput_folder + Constants.kDirSeparator + outputWebFolder + Constants.kDirSeparator + alpha_num_url
    html_file_name = output_folder + Constants.kDirSeparator + alpha_num_url + Constants.kHtmlFileEnding
    os.makedirs(os.path.dirname(html_file_name), exist_ok=True)
    
    # Save 
    src_folder = output_folder + Constants.kDirSeparator + alpha_num_url + Constants.k_files
    if not os.path.exists(src_folder):
        os.mkdir(src_folder)
       
    # Download content from page and modify the link value to the saved file link
    download_and_alter_page_content(src_folder, soup, Constants.kHtmlTagImg, Constants.kHtmlInnerSrc)
    download_and_alter_page_content(src_folder, soup, Constants.kHtmlTagImg, Constants.kHtmlInnerDataSrc)
    download_and_alter_page_content(src_folder, soup, Constants.kHtmlTagLink, Constants.kHtmlInnerHref)
    download_and_alter_page_content(src_folder, soup, Constants.kHtmlTagScript, Constants.kHtmlInnerSrc)
    
    # Save html source code in the file
    with open(html_file_name, "w", encoding="utf-8") as file:
        file.write(soup.prettify())
        file.close()
       
       
def add_links_from_page_to_map(soup, depth_level):
    # Add non-duplicate links to the links depth map on the next level
    for link in soup.find_all('a', href=True):
        if not link_exists_in_map(link[Constants.kHtmlInnerHref]):
            linksDepthMap.setdefault(depth_level + 1,[]).append(link[Constants.kHtmlInnerHref])

def alter_a_html_links(soup):
    # Get all <a href> links from the current page and modify their value to the new structure
    for link in soup.find_all('a', href=True):
        alpha_num_title = Utils.compute_alpha_numerical_string(link[Constants.kHtmlInnerHref])
        new_val = '..' + Constants.kDirSeparator + alpha_num_title + Constants.kDirSeparator + alpha_num_title + Constants.kHtmlFileEnding
        link[Constants.kHtmlInnerHref] = new_val


def download_and_alter_page_content(pagefolder, soup, tag, inner):
    for res in soup.findAll(tag):   # images, css, etc..
        try:
            file_name = os.path.basename(res[inner])
            # Res[inner] # may or may not exist 
            file_path = os.path.join(pagefolder, file_name)
            new_res_val = os.path.basename(pagefolder) + Constants.kDirSeparator + file_name
            # Copy inner value before altering it
            file_to_save = res[inner]
            # Alter tag inner value to the locally saved content
            res[inner] = new_res_val
            if not os.path.isfile(file_path): # Has not been downloaded
                with open(file_path, 'wb') as file:
                    file_bin = requestsSession.get(file_to_save)
                    file.write(file_bin.content)
        except Exception as exc:      
            print(exc, file=sys.stderr)
