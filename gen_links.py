# Syeda Mahajabin (ssmahaja)
import sys
import os
import pathlib
import time
import json
import random
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import selenium
import selenium.webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException


def findnth(string, substring, n):
    parts = string.split(substring, n + 1)
    if len(parts) <= n + 1:
        return -1
    return len(string) - len(parts[-1]) - len(substring)


def main(argv):
    # check args length
    if len(argv) < 3:
        print("Error: Specify all arguments.")
        exit(1)

    # get args
    username = argv[1]
    password = argv[2]
    dept = ""
    if (len(argv) > 3):
        dept = argv[3]

    # make webpage directory
    webpage_dir = pathlib.Path("webpages/")
    if not os.path.isdir(webpage_dir):
        os.mkdir(webpage_dir)

    # driver init
    options = selenium.webdriver.chrome.options.Options()
    options.add_argument("--headless")
    driver = selenium.webdriver.Chrome(options=options, executable_path=ChromeDriverManager().install())
    driver.implicitly_wait(3)
    driver.set_page_load_timeout(15)

    # login
    driver.get("https://weblogin.umich.edu/?cosign-shibboleth.umich.edu&https://shibboleth.umich.edu/idp/Authn/RemoteUser?conversation=e1s1")
    driver.find_element(By.ID, "login").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "loginSubmit").click()
    driver.switch_to.frame(driver.find_element(By.ID, "duo_iframe"))
    driver.find_element(By.CLASS_NAME, "auth-button").click()
    time.sleep(6)
    driver.switch_to.default_content()

    # download webpage
    webpage = driver.page_source
    crn_webpage = webpage_dir/"webpage-0" # check login, page should read 'Stale Request'
    with open(crn_webpage, 'w+') as web_file:
        web_file.write(webpage)

    frontier = {}
    front_key = 0
    ATLAS_COURSE_URL = "https://atlas.ai.umich.edu/course/"
    # the code below generates all atlas course links
    # idk why but this helps the api authentication?
    try:
        driver.get("https://atlas.ai.umich.edu/course/EECS%20376/")
        # download webpage
        webpage = driver.page_source
        crn_webpage = webpage_dir/"webpage-2"
        with open(crn_webpage, 'w+') as web_file:
            web_file.write(webpage)
    except TimeoutException as e:
        print("TimeoutException: " + str(e))
        pass
    cont = True
    crn_api_vis = "https://atlas.ai.umich.edu/api/courses/browse/?format=api&page=2" # "https://atlas.ai.umich.edu/api/courses/browse/?format=api/"
    if dept != "":
        crn_api_vis = "https://atlas.ai.umich.edu/api/courses/browse/?format=api&page_size=32&subject=" + dept.upper()
    links_out = open("atlas_links_" + dept, 'w+')
    while cont:
        try:
            driver.get(crn_api_vis)
            pre = driver.find_element(By.CLASS_NAME, "response-info").text # By.XPATH, "/html/body/div/div[2]/div/div[2]/div[4]").text
            pre = pre[findnth(pre, "\n", 4):]
            data = json.loads(pre)
            for res in data["results"]:
                add_link = ATLAS_COURSE_URL + res['subject'] + "%20" + str(res['catalog_number']) + "/"
                frontier[front_key] = add_link
                front_key += 1
                # print(add_link)
                links_out.write(add_link + "\n")
            if not data["next"]:
                cont = False
            else:
                crn_api_vis = data["next"]
        except TimeoutException as e:
            print("TimeoutException: " + str(e))
            pass

    # end while loop
    links_out.close()
    print("end loop")

    driver.quit()

    print("end main")


if __name__ == "__main__":
    main(sys.argv)
