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
    if len(argv) < 5:
        print("Error: Specify all arguments.")
        exit(1)

    # get args
    seed_file = argv[1]
    max_urls = int(argv[2])
    username = argv[3]
    password = argv[4]
    driver_path = ""
    if len(argv) >= 6:
        driver_path = argv[5]
    driver_path = pathlib.Path(driver_path)

    # check path
    seed_file = pathlib.Path(seed_file)
    if not seed_file.is_file():
        print("Error: Input file does not exist.")
        exit(1)

    # make webpage directory
    webpage_dir = pathlib.Path("webpages/")
    if not os.path.isdir(webpage_dir):
        os.mkdir(webpage_dir)

    # get seeds
    frontier = {}
    visited = set()
    front_key = 0
    with open(seed_file, 'r') as file:
        lines = file.readlines()
        '''
        if os.path.getsize(seed_file) > 80000:
            for _ in range(max_urls):
                rl = random.choice(lines)
                rl = rl.rstrip()
                frontier[front_key] = rl
                front_key += 1
        else:
        '''
        for line in lines:
            line = line.rstrip()
            frontier[front_key] = line
            front_key += 1
    # exit()
    # cr_out = open("crawler.output", 'w+')
    # links_out = open("links.output", 'w+')
    cinfo = open("course-info", 'w+')

    # variables
    # SOURCE_STR = "<SOURCE>***$:"
    HTTPS_STR = "https:"
    ATLAS_COURSE_URL = "https://atlas.ai.umich.edu/course/"
    LEN_BASE = len(ATLAS_COURSE_URL)
    DOMAIN = "atlas.ai.umich.edu"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) ' +
               'AppleWebKit/537.36 (KHTML, like Gecko) ' +
               'Chrome/50.0.2661.102 Safari/537.36'}
    med_grade = { "A+": 100, "A": 90, "A-": 80, "B+": 70, "B": 60, "B-": 50, "C+": 40, "C": 30 }
    highlights = ["desire-highlight", "understanding-highlight",
                  "expectations-highlight", "increased-interest-highlight"]
    # source_url = ""
    front_idx = 0

    # driver init
    options = selenium.webdriver.chrome.options.Options()
    options.add_argument("--headless")
    chromedriver_path = pathlib.Path("chromedriver_linux64") / "chromedriver"
    if driver_path != "":
        chromedriver_path = driver_path
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
    crn_webpage = webpage_dir/"webpage-0"
    with open(crn_webpage, 'w+') as web_file:
        web_file.write(webpage)

    vis_idx = 0
    while len(frontier) > 0 and len(visited) < max_urls:
        crn_url = frontier[front_idx]
        del frontier[front_idx]
        front_idx += 1
        print("crn_url: " + crn_url)

        if len(crn_url) < 1:
            continue

        # add ending slash
        if crn_url[-1] != "/":
            crn_url = crn_url + "/"

        # convert to absolute
        if crn_url.find(HTTPS_STR) == 0:
            pass
        elif crn_url.find("//") == 0:
            crn_url = HTTPS_STR + crn_url
        elif crn_url.find("/") == 0:
            crn_url = HTTPS_STR + "//" + DOMAIN + crn_url
        else:
            continue

        # filter url
        if crn_url.find(ATLAS_COURSE_URL[:-1]) != 0:
            continue
        if "/accounts/logout" in crn_url:
            continue

        # check if url already visited
        if crn_url in visited:
            continue

        # request url
        try:
            driver.get(crn_url)
        except TimeoutException as e:
            print("TimeoutException: " + str(e))
            continue
        except Exception:
            continue

        # add crn_url to visited
        visited.add(crn_url)
        vis_idx += 1
        print("visited: " + crn_url)
        # cr_out.write(crn_url + "\n")

        # download webpage if course page
        webpage = driver.page_source # response.content.decode("latin-1")
        if crn_url.find(ATLAS_COURSE_URL) == 0:
            perc = crn_url.find("%20")
            crn_webpage = crn_url[LEN_BASE:perc] + crn_url[perc+3:-1]
            crn_webpage = webpage_dir/crn_webpage
            # with open(crn_webpage, 'w+') as web_file:
            # web_file.write(crn_url + "\n")
            score = 0.0
            total = 0
            try:
                elem = driver.find_element(By.CLASS_NAME, "grade-median")
                elem = elem.find_element(By.CLASS_NAME, "bold")
                crn_html = elem.get_attribute('innerHTML')
                # web_file.write("grade-median: " + crn_html + "\n")
                score += med_grade[crn_html]
                total += 1
            except (KeyError, StaleElementReferenceException) as e:
                print("Med-Grade Error: " + str(e))
                pass
            except NoSuchElementException as e:
                print("Med-Grade Error: " + str(e))
                mean = "N/A"
                # web_file.write("overall-score: " + mean + "\n")
                cinfo.write(crn_url[LEN_BASE:perc] + crn_url[perc+3:-1] + ": " + mean + "\n")
                # web_file.write("\n----------------- WEBPAGE BELOW FOR REF ------------------------\n")
                # web_file.write(webpage)
                continue
            except Exception:
                continue
            for high in highlights:
                try:
                    elem = driver.find_element(By.CLASS_NAME, high)
                    crn_html = elem.get_attribute('innerHTML')
                    # web_file.write(high + ": " + crn_html + "\n")
                    score += int(crn_html[:-1])
                    total += 1
                except (NoSuchElementException, StaleElementReferenceException) as e:
                    print("Highlight Error: " + str(e))
                    pass
                except Exception:
                    continue
            mean = "N/A"
            if total > 0:
                mean = str(score/total)
            # web_file.write("overall-score: " + mean + "\n")
            cinfo.write(crn_url[LEN_BASE:perc] + crn_url[perc+3:-1] + ": " + mean + "\n")
            # web_file.write("\n----------------- WEBPAGE BELOW FOR REF ------------------------\n")
            # web_file.write(webpage)

        # parse webpage for new links
        # soup = BeautifulSoup(webpage, "html.parser")
        # for link in soup.findAll('a', href=True):
        #    frontier[front_key] = link.get('href')
        #    front_key += 1

    # end while loop
    print("end loop")

    driver.quit()
    # cr_out.close()
    # links_out.close()
    cinfo.close()

    print("end main")


if __name__ == "__main__":
    main(sys.argv)
