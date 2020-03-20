import unicodedata, datetime
import requests         #pip install requests
from lxml import html   #pip install lxml

coronaGlobalData = dict()
coronaLocalData = dict()
countryList = list()

def getCoronaGlobalData():
    global coronaGlobalData
    return coronaGlobalData

def getCoronaLocalData():
    global coronaLocalData
    return coronaLocalData

def getCountryListData():
    global countryList
    return countryList

def updateGlobalStats(htmlContents):
    global coronaGlobalData
    newCoronaGlobalData = dict()
    globalCases = htmlContents.xpath("//*/div[4]/div/span")[0]
    globalDeaths = htmlContents.xpath("//*/div[6]/div/span")[0]
    globalRecoveries = htmlContents.xpath("//*/div[7]/div/span")[0]
    newCoronaGlobalData = {
        "Global Cases": globalCases.text.strip(),
        "Global Deaths": globalDeaths.text.strip(),
        "Global Recoveries": globalRecoveries.text.strip()
    }
    coronaGlobalData = newCoronaGlobalData

def updateLocalStats(htmlContents):
    global coronaLocalData
    rows = htmlContents.xpath('//*[@id="main_table_countries_today"]/tbody[1]/tr')
    newCoronaLocalData = dict()

    for row in rows:
        info = [c.text for c in row.getchildren()]
        
        if (info[0] == None):
            info[0] = row[0][0].text
        info[0] = unicodedata.normalize('NFD', info[0]).encode('ascii', 'ignore').decode("utf-8")

        info[3] = info[3].strip()
        
        dicInfo = { info[0].lower(): {
            "Country": info[0],
            "Total Cases": info[1],
            "New Cases": info[2],
            "Total Deaths": info[3],
            "New Deaths": info[4],
            "Total Recovered": info[5],
            "Active Cases": info[6],
            "Serious Critical": info[7],
            "Total Cases/1M pop": info[8]
        } }
        newCoronaLocalData.update(dicInfo)
    coronaLocalData = newCoronaLocalData

def updateAffectedCountries():
    global coronaLocalData
    global countryList
    newCountryList = list()

    for item in coronaLocalData:
        newCountryList.append(item.title())
    newCountryList.sort()
    countryList = newCountryList

def updateInfo():
    page = requests.get('https://www.worldometers.info/coronavirus/')
    htmlContents = html.fromstring(page.text)

    updateGlobalStats(htmlContents)
    updateLocalStats(htmlContents)
    updateAffectedCountries()

    print("Updated the API [" + str(datetime.datetime.now()) + "]")