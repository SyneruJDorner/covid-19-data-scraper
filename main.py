import os, time, atexit
import requests #pip install requests
from flask import Flask, jsonify #pip install flask
from lxml import html #pip install lxml
import socket
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

localHost = '127.0.0.1'
globalHost = 'xxx.xxx.xxx.xxx'
clear = lambda: os.system('cls')
coronaGlobalData = dict()
coronaLocalData = dict()
countryList = list()

#init flask
app = Flask(__name__)
app.secret_key = os.urandom(16)

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
        info[3] = info[3].strip()
        dicInfo = {info[0].lower(): {
            "Country": info[0],
            "Total Cases": info[1],
            "New Cases": info[2],
            "Total Deaths": info[3],
            "New Deaths": info[4],
            "Total Recovered": info[5],
            "Active Cases": info[6],
            "Serious Critical": info[7],
            "Total Cases/1M pop": info[8]
        }}
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

@app.route('/global')
def getGlobalStats():
    global coronaGlobalData
    return coronaGlobalData

@app.route('/country/<id>')
def getLocalStatsByCountry(id):
    global coronaLocalData
    return coronaLocalData[id.lower()]

@app.route('/getCountryList')
def getCountryList():
    global countryList
    return jsonify(countryList)

def infoFetcher():
    page = requests.get('https://www.worldometers.info/coronavirus/')
    htmlContents = html.fromstring(page.text)

    #update our global variables
    updateGlobalStats(htmlContents)
    updateLocalStats(htmlContents)
    updateAffectedCountries()

    print("Updated the API [" + str(datetime.datetime.now()) + "]")

def main():
    global globalHost
    hostname = socket.gethostname()    
    globalHost = socket.gethostbyname(hostname)  

    infoFetcher()
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=infoFetcher, trigger="interval", seconds=20)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

    app.run(host=localHost, port='8000', debug=False, use_reloader=False)

if __name__ == "__main__":
    main()