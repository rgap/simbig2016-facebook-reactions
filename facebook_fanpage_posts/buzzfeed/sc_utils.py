import urllib2
from selenium import webdriver

class ScrapperUtils:

    class NoSuchTagException(Exception): pass

    @staticmethod
    def get_tag(parent, name, *args, **kwargs):
        child = parent.find(name, *args, **kwargs)
        if child is None:
            raise NoSuchTagException(name)
        else:
            return child

    @staticmethod
    def wait_element(browser, className):
        limit = 10   # waiting limit in seconds
        inc = 1   # sleep for 1 s
        c = 0
        while (c < limit):
            try:
                browser.find_element_by_class_name(className)
                return 1
            except:
                time.sleep(inc)
                c = c + 1 
        return 0

    @staticmethod
    def page_loaded(browserclass, url):
        tries = 1
        while tries <= 20:
            try:
                browserclass.browser.refresh()
                browserclass.browser.get(url)
                print ("page loaded")
                return True
            except:
                print ("refresh")
                tries += 1
                try:
                    browserclass.browser.refresh()
                except:
                    break

        key = raw_input('(1) continue, (2) re-open browser, (3) keep trying : ')
                
        if key == "1":
            print "continue"
            return True
        if key == "2":
            print "re-open browser"
            try:
                browserclass.close_browser()
            except:
                pass
            print "browserclass.init_browser()"
            browserclass.init_browser()
            return False
        if key == "3":
            print "keep trying"
            return False

    @staticmethod
    def page_loaded_urllib(urllibclass, url):
        tries = 1
        while tries <= 2:
            try:
                urllibclass.response = urllib2.urlopen(url)
                return True
            except urllib2.HTTPError, e:
                if e.code == 404 or e.code == 403 or e.code == 500: # Not found || Forbidden
                    return False
                else:
                    print e.reason
                    print "trying again... " + str(tries)
                    tries += 1
            except urllib2.URLError, e:
                print e.reason
                print "trying again... " + str(tries)
                tries += 1
                

        key = raw_input('What to do now? (1) stop trying, (2) continue, (3) keep trying : ')
                
        if key == "1":
            print "stop trying"
            return False
        if key == "2":
            print "continue"
            return True
        if key == "3":
            print "keep trying"
            self.page_loaded_urllib(urllibclass, url)