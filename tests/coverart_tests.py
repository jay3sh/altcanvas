import unittest

from coverart import Amazon


sample_keywords = (
    'norah jones sunrise',
    'colbie caillat',
    'Jem finally woken',
    'John Mayer continuum'
    )

sample_results = []

class TestAmazonSearch(unittest.TestCase):
    def setUp(self):
        self.amazon = Amazon()

    def testSearch(self):
        for kw in sample_keywords:
            results = self.amazon.search(kw.split())
            self.assert_(len(results) > 0)
            # save the first result for getImage test
            sample_results.append(results[0])
        
class TestAmazonGetImages(unittest.TestCase):
    def setUp(self):
        self.amazon = Amazon()

    def testGetImages(self):
        for result in sample_results:
            images = self.amazon.getImages(result)

if __name__ == '__main__':
    for t in [TestAmazonSearch,TestAmazonGetImages]:
        suite = unittest.TestLoader().loadTestsFromTestCase(t)
        testResult = unittest.TextTestRunner(verbosity=2).run(suite)

