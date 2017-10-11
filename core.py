from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import time
import urllib

def checkinternet():
    """ Check internet conection. If internet is down, print the last URL"""
    try:
        urllib.request.urlopen('http://www.google.com')
    except:
        print(n)
        driver.quit()

def main():

    mime = "application/pdf,text/html,text/txt,application/msword"
    profile = FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2)  # custom location
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference("browser.download.dir", '/Users/thiagovieira/Downloads')
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", mime)
    profile.set_preference("pdfjs.disabled", True)
    profile.set_preference("plugin.disable_full_page_plugin_for_types", mime)

    driver = webdriver.Firefox(firefox_profile=profile)
    driver.get("https://projudi.tjba.jus.br")

    time.sleep(20)
    url = 'https://projudi.tjba.jus.br/projudi/listagens/DownloadArquivo?arquivo={}'
    for n in range(1, 10001):
        try:
            checkinternet()
            driver.set_page_load_timeout(1)
            driver.get(url.format(n))
            time.sleep(5)
        except:
            pass
    driver.quit()

if __name__ == "__main__":
    main()
    