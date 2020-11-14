import csv
import requests
from selenium import webdriver
from bs4 import BeautifulSoup

URL_ALL_CAT = "https://gmg.greatermankato.com/allcategories"
URL_BASE = "https://gmg.greatermankato.com/"
FILENAME = "businesses.csv"
URL = "https://mblsportal.sos.state.mn.us/Business/Search"
HEADER = "Business Name & Website,Industry,Chamber Level,Street Address,City,State,Postal Code,Phone Number,Name on State Business Filings"

output = []
names = []

driver = webdriver.Chrome()

def getAllIndustries():
    page = requests.get(URL_ALL_CAT)
    soup = BeautifulSoup(page.content, "html.parser")
    industries = []
    for ref in soup.find_all("li", class_="ListingCategories_AllCategories_CATEGORY"):
        text = str(ref.text)
        text = text.replace(" ", "-")
        text = text.replace("/", "-")
        industries.append(text)
    return industries

def getNamesFromState(name):
    driver.get(URL)
    businessName = driver.find_element_by_id('BusinessName')
    businessName.send_keys(name)
    driver.find_element_by_xpath('//*[@id="businessNameTab"]/div[1]/div/button').click()
    try:
        driver.find_element_by_xpath(
            '//*[@id="main"]/section/div[3]/div/div[2]/div[2]/div/table/tbody/tr[2]/td[2]/a').click()
    except:
        pass

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    options = []

    try:
        options.append(soup.find("dt", text="Manager").find_next_sibling().text)
    except:
        pass
    try:
        options.append(soup.find("dt", text="Chief Executive Officer").find_next_sibling().text)
    except:
        pass
    try:
        options.append(soup.find("dt", text="Individual Contact for Agent").find_next_sibling().text)
    except:
        pass
    try:
        options.append(soup.find("dt", text="Registered Agent(s)").find_next_sibling().text)
    except:
        pass

    # Remove Duplicates and known unwanteds
    options = list(dict.fromkeys(options))
    try:
        options.remove('(Optional) Currently No Agent')
    except:
        pass
    try:
        options.remove('United States Corporation Agents, Inc.')
    except:
        pass
    try:
        options.remove('Corporation Service Company')
    except:
        pass
    return str(options)

def getBizInfo(industry):
    page = requests.get(URL_BASE + industry)
    rows = []
    print(industry)
    soup = BeautifulSoup(page.content, 'html.parser')

    for lvl in range(4, 1, -1):
        path = "ListingResults_All_CONTAINER ListingResults_Level" + str(lvl) + "_CONTAINER"
        phonePath = "ListingResults_Level" + str(lvl) + "_PHONE1"
        webPath = "ListingResults_Level" + str(lvl) + "_VISITSITE"
        data = soup.find_all("div", class_=path)
        for info in data:
            try:
                name = info.find("span", itemprop="name").text
                address = info.find("span", itemprop="street-address").text
                city = info.find("span", itemprop="locality").text
                state = info.find("span", itemprop="region").text
                zip = info.find("span", itemprop="postal-code").text
                phone = info.find("div", class_=phonePath).text
                website = info.find("span", class_=webPath).find("a", href=True)
                chamberlvl = lvl
            except:
                print("One or more Attribute Missing")
            else:
                final = ['=HYPERLINK("' + website['href'] + '","' + name + '")', industry, chamberlvl, address, city, state, zip,
                         phone, getNamesFromState(name)]
                rows.append(final)
    return rows


def initCSV(Header):
    text_file = open(FILENAME, "w")
    text_file.write(Header)
    text_file.write("\n")
    text_file.close()


def writeToCSV(data):
    with open(FILENAME, 'a', newline="") as f:
        write = csv.writer(f)
        write.writerows(data)


def testURL(industry):
    page = requests.get(URL_BASE + industry)
    if page.status_code != 200:
        print(industry)


def main():
    initCSV(HEADER)
    verticals = getAllIndustries()
    for i in verticals:
        ready = getBizInfo(i)
        writeToCSV(ready)


if __name__ == "__main__":
    main()
