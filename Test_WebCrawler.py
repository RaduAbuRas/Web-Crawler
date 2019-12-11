#Unit testing module

import unittest
import WebCrawler

class TestWebCrawl(unittest.TestCase):

    def test_crawlPageThreeLevels(self):
        WebCrawler.crawlPage('https://legioxiii.ro', 1)

if __name__ == '__main__':
    unittest.main()
