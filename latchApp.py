import requests
import json
from datetime import datetime
import platform

def makeGetRequest(url, PATH2_SESSION, deviceName="Python", deviceOsVersion=platform.python_version()):
    headers = {'X-Client-Version': 'Android/2.2.4', 'X-device': deviceName, 'X-os-version': deviceOsVersion}
    cookies =  {"PATH2_SESSION": PATH2_SESSION}
    r = requests.get(url , headers=headers, cookies=cookies)
    if r.status_code == 200:
        if "error" in r.json():
            raise Exception("Session was closed")
        return r.json()
    else:
        raise Exception("There was an error: Code " + str(r.status_code))

def authenticate(user, password, deviceName="Python", deviceOsVersion=platform.python_version()):
    headers = {'X-Client-Version': 'Android/2.2.4', 'X-device': deviceName, 'X-os-version': deviceOsVersion}
    data = {"username": user, "password": password}
    r = requests.post("https://latch.elevenpaths.com/control/1.8/authenticate", headers=headers, data=data)
    if r.status_code == 200:
        return r.cookies.get("PATH2_SESSION")
    else:
        raise Exception("There was an error: Code " + str(r.status_code))

def register(name, email, password, communicationsAllowed=False):
    if communicationsAllowed:
        communicationsAllowed = "true"
    else:
        communicationsAllowed = "false"
    headers = {'X-Client-Version': 'Android/2.2.4', 'X-device': deviceName}
    data = {"password": password, "terms": "true", "communicationsAllowed": communicationsAllowed, "passwordCheck": password, "name": name, "email": email}
    r = requests.post("https://latch.elevenpaths.com/www/registerNative", headers=headers, data=data)
    if r.status_code == 200:
        return
    else:
        raise Exception("There was an error: Code " + str(r.status_code))

class app:
    def __init__(self, PATH2_SESSION, deviceName="Python"):
        self.PATH2_SESSION = PATH2_SESSION
        self.deviceName = deviceName

    def makeAuthedGetRequest(self, url):
        return makeGetRequest(url, self.PATH2_SESSION)

    def getApplications(self):
        url = "https://latch.elevenpaths.com/control/1.8/applications"
        json = self.makeAuthedGetRequest(url)
        data = json['data']
        return data
    
    def getLatches(self):
        return self.getApplications()['operations']

    def getTotps(self):
        return self.getApplications()['totp']

    def getAppPreferences(self):
        url = "https://latch.elevenpaths.com/control/1.8/appPreferences"
        json = self.makeAuthedGetRequest(url)
        data = json['data']
        return data
    
    def getSessions(self):
        url = "https://latch.elevenpaths.com/control/1.8/sessions"
        json = self.makeAuthedGetRequest(url)
        data = json['data']
        return data
    
    def setLatchState(self, latchCode, state):
        if state: 
            state = "off" #Inversed the way the api considers states cause i think this is much more logical
        else:
            state = "on"
        headers = {'X-Client-Version': 'Android/2.2.4'}
        cookies =  {"PATH2_SESSION": self.PATH2_SESSION}
        data = {"status["+latchCode+"]": state}
        r = requests.post("https://latch.elevenpaths.com/control/1.8/update", headers=headers, cookies=cookies, data=data)
        if r.status_code == 200:
            if "error" in r.json():
                raise Exception("Session was closed")
            return
        else:
            raise Exception("There was an error: Code " + str(r.status_code))

    def getOperationsHistory(self, latchCode, fromDate, toDate):
        fromUnixTime = fromDate.timestamp()
        toUnixTime = toDate.timestamp()
        url = "https://latch.elevenpaths.com/control/1.8/history/" + latchCode + "/" + fromUnixTime + "/" + toUnixTime
        self.makeAuthedGetRequest(url)
        data = json['data']
        return data

    def logoutSpecificSession(self, sessionCode):
        headers = {'X-Client-Version': 'Android/2.2.4'}
        cookies =  {"PATH2_SESSION": self.PATH2_SESSION}
        r = requests.delete("https://latch.elevenpaths.com/control/1.8/sessions/" + sessionCode, headers=headers, cookies=cookies)
        if r.status_code == 200:
            if "error" in r.json():
                raise Exception("Session was closed")
            return
        else:
            raise Exception("There was an error: Code " + str(r.status_code))

    def logout(self):
        url = "https://latch.elevenpaths.com/control/1.8/logout"
        self.makeAuthedGetRequest(url)

def totpTo2FAUBPortsJson(latchTotps):
    date = datetime.now().strftime("%a. %b. %d %H:%M:%S %Y %Z%z")
    totpsJson = {"keys":[]}
    for totp in latchTotps:
        totp = latchTotps[totp]
        if totp["algorithm"] == "Seleccionar":
            totp["algorithm"] = "SHA1"
        if totp["customName"] == "":
            totp["customName"] = totp["name"]
        prepared = {"added":date,"description":totp["customName"],"keyJSON":"otpauth://totp/"+ totp["customName"] +":"+ totp["accountName"] +"?issuer="+ totp["customName"] +"&secret="+ totp["secret"] +"&algorithm="+totp["algorithm"]+"&digits="+ str(totp["digits"]) +"&period="+ str(totp["period"])}
        prepared["keyJSON"] = prepared["keyJSON"].replace(" ", "%20")
        totpsJson["keys"].append(prepared)
    return totpsJson
