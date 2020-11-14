import csv
import requests

from bs4 import BeautifulSoup

URL_ALL_CAT = "https://gmg.greatermankato.com/allcategories"
URL_BASE = "https://gmg.greatermankato.com/"
FILENAME = "businesses.csv"
HEADER = "Business Name & Website,Industry,Chamber Level,Street Address,City,State,Postal Code,Phone Number"


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
                         phone]
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
        output = getBizInfo(i)
        writeToCSV(output)


if __name__ == "__main__":
    main()
