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
            raise Exception("There was an error: " + str(r.json()['error']))
        return r.json()
    else:
        raise Exception("There was an error: Code " + str(r.status_code))

def authenticate(user, password, deviceName="Python", deviceOsVersion=platform.python_version()):
    headers = {'X-Client-Version': 'Android/2.2.4', 'X-device': deviceName, 'X-os-version': deviceOsVersion}
    data = {"username": user, "password": password}
    r = requests.post("https://latch.elevenpaths.com/control/1.8/authenticate", headers=headers, data=data)
    if r.status_code == 200:
        if "error" in r.json():
            raise Exception("There was an error: " + str(r.json()['error']))
        return r.cookies.get("PATH2_SESSION")
    else:
        raise Exception("There was an error: Code " + str(r.status_code))

def register(name, email, password, deviceName="Python", deviceOsVersion=platform.python_version(), communicationsAllowed=False):
    if communicationsAllowed:
        communicationsAllowed = "true"
    else:
        communicationsAllowed = "false"
    headers = {'X-Client-Version': 'Android/2.2.4', 'X-device': deviceName, 'X-os-version': deviceOsVersion}
    data = {"password": password, "terms": "true", "communicationsAllowed": communicationsAllowed, "passwordCheck": password, "name": name, "email": email}
    r = requests.post("https://latch.elevenpaths.com/www/registerNative", headers=headers, data=data)
    if r.status_code == 200:
        try:
            if "error" in r.json():
                raise Exception("There was an error: " + str(r.json()['error']))
            return
        except:
            pass
    else:
        raise Exception("There was an error: Code " + str(r.status_code))

def changePassword(email, deviceName="Python", deviceOsVersion=platform.python_version()):
    headers = {'X-Client-Version': 'Android/2.2.4', 'X-device': deviceName, 'X-os-version': deviceOsVersion}
    data = {"email": email}
    r = requests.post("https://latch.elevenpaths.com/www/requestPasswordResetMobile", headers=headers, data=data)
    if r.status_code == 200:
        try:
            if "error" in r.json():
                raise Exception("There was an error: " + str(r.json()['error']))
            return
        except:
            pass
    else:
        raise Exception("There was an error: Code " + str(r.status_code))

class app:
    def __init__(self, user, password, deviceName="Python", deviceOsVersion=platform.python_version()):
        self.PATH2_SESSION = authenticate(user, password, deviceName, deviceOsVersion)
        self.deviceName = deviceName
        self.deviceOsVersion = deviceOsVersion
        self.headers = {'X-Client-Version': 'Android/2.2.4', 'X-device': self.deviceName, 'X-os-version': self.deviceOsVersion}
        self.cookies = {"PATH2_SESSION": self.PATH2_SESSION}

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

    def setAppPreferences(self, settingsDict):
        settingsStr = str(settingsDict).replace("True", "true").replace("False", "true")
        data = {"appPreferences": settingsStr}
        r = requests.post("https://latch.elevenpaths.com/control/1.8/appPreferences", headers=self.headers, cookies=self.cookies, data=data)
        if r.status_code == 200:
            if "error" in r.json():
                raise Exception("There was an error: " + str(r.json()['error']))
            return
        else:
            raise Exception("There was an error: Code " + str(r.status_code))

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
        data = {"status["+latchCode+"]": state}
        r = requests.post("https://latch.elevenpaths.com/control/1.8/update", headers=self.headers, cookies=self.cookies, data=data)
        if r.status_code == 200:
            if "error" in r.json():
                raise Exception("There was an error: " + str(r.json()['error']))
            return
        else:
            raise Exception("There was an error: Code " + str(r.status_code))

    def getOperationsHistory(self, latchCode, fromDate, toDate):
        fromUnixTime = fromDate.timestamp()
        toUnixTime = toDate.timestamp()
        url = "https://latch.elevenpaths.com/control/1.8/history/" + latchCode + "/" + fromUnixTime + "/" + toUnixTime
        json = self.makeAuthedGetRequest(url)
        data = json['data']
        return data

    def getPairingToken(self):
        url = "https://latch.elevenpaths.com/control/1.8/pairingToken"
        json = self.makeAuthedGetRequest(url)
        data = json['data']
        return data
    
    def addTotp(self, name, accountName, secret):
        data = {"name": name, "secret": secret, "accountName": accountName}
        r = requests.post("https://latch.elevenpaths.com/control/1.8/totp", headers=self.headers, cookies=self.cookies, data=data)
        if r.status_code == 200:
            if "error" in r.json():
                raise Exception("There was an error: " + str(r.json()['error']))
            return r.json()["data"]
        else:
            raise Exception("There was an error: Code " + str(r.status_code))

    def removeTotp(self, latchCode):
        r = requests.delete("https://latch.elevenpaths.com/control/1.8/totp/" + latchCode, headers=self.headers, cookies=self.cookies)
        if r.status_code == 200:
            if "error" in r.json():
                raise Exception("There was an error: " + str(r.json()['error']))
            return
        else:
            raise Exception("There was an error: Code " + str(r.status_code))

    def logoutSpecificSession(self, sessionCode):
        r = requests.delete("https://latch.elevenpaths.com/control/1.8/sessions/" + sessionCode, headers=self.headers, cookies=self.cookies)
        if r.status_code == 200:
            if "error" in r.json():
                raise Exception("There was an error: " + str(r.json()['error']))
            return
        else:
            raise Exception("There was an error: Code " + str(r.status_code))

    def logout(self):
        url = "https://latch.elevenpaths.com/control/1.8/logout"
        self.makeAuthedGetRequest(url)

def totpTo2FAUBPortsJson(latchTotps):
    timeZone = datetime.now().strftime("%Z%z")
    if timeZone == "":
        timeZone = "UTC+0000" #Sometimes timezone is none so need this fora voiding errors
    date = datetime.now().strftime(f"%a. %b. %d %H:%M:%S %Y {timeZone}")
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
    totpsJson = json.dumps(totpsJson)#str(totpsJson).replace("'", "\"")
    return totpsJson

def totpToUrls(latchTotps): # Theese can be encoded (one by one) in a QR for scanning with any app
    data = json.loads(totpTo2FAUBPortsJson(latchTotps))
    urls = []
    for totp in data["keys"]:
        urls.append(totp["keyJSON"])
    return urls

