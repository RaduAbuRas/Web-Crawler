#Holds constants of all types

import os

# Directory constants
kHtmlFileEnding = '.html'
kOutputFolder = 'output'
k_files = '_files'
kDirSeparator = os.path.sep

# HTML constants
kHtmlTagImg = 'img'
kHtmlTagLink = 'link'
kHtmlTagScript = 'script'

kHtmlInnerSrc = 'src'
kHtmlInnerDataSrc = 'data-src'
kHtmlInnerHref = 'href'

kHtmlTagInnerVals = [ 
    (kHtmlTagImg, kHtmlInnerSrc), 
    (kHtmlTagImg, kHtmlInnerDataSrc), 
    (kHtmlTagLink, kHtmlInnerHref), 
    (kHtmlTagScript, kHtmlInnerSrc) 
]