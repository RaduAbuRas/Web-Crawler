#Main module, this should call the crawler on the given arguments

import sys
import os
import Constants

# Remove 'main.py' from argv list
args = sys.argv[1:]

# Create output folder
os.makedirs(Constants.kOutputFolder, exist_ok=True)

# Arguments : website url, depth level
# Minimum depth level is 1 (just save the given page)
if __name__ == '__main__':
    if len(args) != 2:
        print('Invalid arguments, syntax is url depth')
        sys.exit()

    import WebCrawler
    WebCrawler.crawlWebsite(args[0],int(args[1]))
    
    