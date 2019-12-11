Project description - Web Crawler - 11/Dec/2019 - Abu Ras Radu

1. Installation
m1. I have provided a pyinstaller windows executable which can be found in /dist
m2. Pull from docker : docker pull raduradu0410/web-crawler:v1
m3. Manually install the modules from requirements with pip

2. Running the application, arguments and expected output
Depending on which installation method you chose you can run the application using the following commands:
- main.exe 'link' 'depth'
- docker run web-crawler 'link' 'depth'
- python main.py 'link' 'depth'
e.g main.exe https://legioxiii.ro 2

Arguments :
- link : this should be a valid link in htttp format (as pasted from the browser) that can be used to access the page
- depth : levels of sub pages to be downloaded starting from the root ( given page)

The first argument represents the page that will be crawler and the second one the depth (sub pages) to be crawler as well

Output :
The expected output will be a folder named output in the root of the application that contains a folder hierarchy as such :
output \ page directory \ sub pages directories (this also contains the root page directory which has the same name as the parent page directory)

3. Overview
Web crawler is an application that crawls a website and downloads as much content as possible for off-line usage.
It can be configured so that it downloads as many web pages as desired in order to avoid long processing time and unnecessary pages.
For example if we input an e shop website such as amazon with level 2 depth, it will download the main page and the articles found on the main page.
After downloading a page it can be accessed off-line by navigating to output/page name dir/page name dir/page name dir.html.

4. Architecture and technical details
Web crawler relies heavily on the requests module in order to make calls to the pages that will be scraped and beautifulsoup4 to parse the page content
The main processing module contains a dictionary that holds sub-pages at each level starting with 0 (root) as such:
0: [root]
1: [link 1, link 2]
2: [link 3, link 6, link 7]
When crawling a page the following steps are completed:
- download page content and create a beautifulsoup object from it
- extract links of sub-pages from the current page and add them to the dictionary on the next level. Duplicate links are not added as the page has been or will be downloaded if it is in the dictionary.
(e.g. home page button can be found in all the sub-pages of a page)
- modify the links from the html of the current page so that they point to the sub-pages that will be saved on disk]
- save the current page on disk with as much content as possible (css, images etc)
This process applies to every page individually and each level is processed on multiple threads to improve performance and each thread writes in the same dictionary as they find sub pages when parsing their page.
Before moving to the next level the application waits for all threads of a current level to finish parsing their respective page.
Modules are described via comment at the beginning of the file.

5. Known issues / bugs
- Pages with strong encryption will be downloaded partially
- When unit testing the output folder is not deleted afterwards
- This has not been tested on any other operating system than windows and since the application creates directories it could raise permission problems
- Because the multi threaded work waits for each level to be completed this represents a bottleneck since a large page can block the whole flow untill it is completed

6. Improvements
- Improve speed by redesigning the work split between threads to allow parsing multiple levels at once
- Save even more content offline
- Improve logging so show more errors and exceptions
- Create more unit testing cases

7. Conclussions
Web crawler is far from perfect but it is a promising start and with some tweaks it can definitely become a viable option for saving a website locally

