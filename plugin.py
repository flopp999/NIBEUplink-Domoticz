# NIBEUplink Python Plugin
#
# Author: flopp999
#
"""
<plugin key="NIBEUplink" name="NIBE Uplink 0.77" author="flopp999" version="0.77" wikilink="https://github.com/flopp999/NIBEUplink-Domoticz" externallink="https://www.nibeuplink.com">
    <description>
        <h2>NIBE Uplink is used to read data from api.nibeuplink.com</h2><br/>
        <h2>Support me with a coffee &<a href="https://www.buymeacoffee.com/flopp999">https://www.buymeacoffee.com/flopp999</a></h2><br/>
        <h1>To use this plugin you need to agree to send data to me. I will use the data to develop the plugin so it will fit all NIBE systems</h1>
        <h3>You can see what data I have collect by follow this link. I will onlt collect data once after startup. It will include all your parameters, your SystemID and you categories.</h3>
        <h3>&<a href="https://rhematic-visitors.000webhostapp.com/[your systemid]">https://rhematic-visitors.000webhostapp.com/[your systemid]</a></h3>
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>..</li>
        </ul>
        <h3>Devices</h3>
        <ul style="list-style-type:square">
            <li>Unit 0x is AUX_IN_OUT</li>
            <li>Unit 1x is STATUS</li>
            <li>Unit 2x is CPR_INFO_EP14</li>
            <li>Unit 3x is VENTILATION</li>
            <li>Unit 4x is SYSTEM_1</li>
            <li>Unit 5x is ADDITION</li>
            <li>Unit 6x is SMART_PRICE_ADAPTION</li>
            <li>Unit 7x is SYSTEM_INFO</li>
            <li>Unit 8x is SYSTEM_2</li>
            <li>Unit 9x is HEAT_METER</li>
            <li>Unit 10x is ACTIVE_COOLING_2_PIPE</li>
            <li>Unit 11x is PASSIVE_COOLING_INTERNAL</li>
            <li>Unit 12x is PASSIVE_COOLING_2_PIPE</li>
            <li>Unit 13x is DEFROSTING</li>
        </ul>
        <h3>How to get your Identifier, Secret and URL?</h3>
        <h4>&<a href="https://github.com/flopp999/NIBEUplink-Domoticz#identifier-secret-and-callback-url">https://github.com/flopp999/NIBEUplink-Domoticz#identifier-secret-and-callback-url</a></h4>
        <h3>How to get your Access Code?</h3>
        <h4>&<a href="https://github.com/flopp999/NIBEUplink-Domoticz#access-code">https://github.com/flopp999/NIBEUplink-Domoticz#access-code</a></h4>
        <h3>Configuration</h3>
    </description>
    <params>
        <param field="Mode5" label="Agree to send data to developer of this plugin" width="70px" required="true">
            <options>
                <option label="Yes" value=True />
                <option label="No" value=False />
            </options>
        </param>
        <param field="Mode4" label="NIBE Uplink Identifier" width="320px" required="true" default="Identifier"/>
        <param field="Mode2" label="NIBE Uplink Secret" width="350px" required="true" default="Secret"/>
        <param field="Address" label="NIBE Callback URL" width="950px" required="true" default="URL"/>
        <param field="Mode1" label="NIBE Access Code" width="350px" required="true" default="Access Code"/>
        <param field="Mode3" label="NIBE Refresh Token" width="350px" default="Copy Refresh Token from Log to here" required="true"/>
        <param field="Mode6" label="Debug to file (Nibe.log)" width="70px">
            <options>
                <option label="Yes" value="Yes" />
                <option label="No" value="No" />
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz

Package = True

try:
    import requests, json, os, logging
except ImportError as e:
    Package = False

try:
    from logging.handlers import RotatingFileHandler
except ImportError as e:
    Package = False

try:
    from datetime import datetime
except ImportError as e:
    Package = False

dir = os.path.dirname(os.path.realpath(__file__))
logger = logging.getLogger("NIBE")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(dir+'/NIBEUplink.log', maxBytes=50000, backupCount=5)
logger.addHandler(handler)

class BasePlugin:
    enabled = False

    def __init__(self):
        self.token = ''
        self.loop = 0
        self.Count = 5
        return

    def onStart(self):
        WriteDebug("onStart")
        self.Ident = Parameters["Mode4"]
        self.URL = Parameters["Address"]
        self.Access = Parameters["Mode1"]
        self.Secret = Parameters["Mode2"]
        self.Refresh = Parameters["Mode3"]
        self.SystemID = ""
        self.NoOfSystems = ""
        self.SystemUnitId = 0
        self.FirstRun = True
        self.Agree = Parameters["Mode5"]
        self.AllSettings = True
        self.Categories = []

        if len(self.Ident) < 32:
            Domoticz.Log("Identifier too short")
            WriteDebug("Identifier too short")
            self.Ident = CheckFile("Ident")
        else:
            WriteFile("Ident",self.Ident)

        if len(self.URL) < 10:
            Domoticz.Log("URL too short")
            WriteDebug("URL too short")
            self.URL = CheckFile("URL")
        else:
            WriteFile("URL",self.URL)

        if len(self.Access) < 370:
            Domoticz.Log("Access Code too short")
            WriteDebug("Access Code too short")
            self.Access = CheckFile("Access")
        else:
            WriteFile("Access",self.Access)

        if len(self.Secret) < 44:
            Domoticz.Log("Secret too short")
            WriteDebug("Secret too short")
            self.Secret = CheckFile("Secret")
        else:
            self.Secret = self.Secret.replace("+", "%2B")
            WriteFile("Secret",self.Secret)

        if len(self.Refresh) < 270:
            Domoticz.Log("Refresh too short")
            WriteDebug("Refresh too short")
        else:
            WriteFile("Refresh",self.Refresh)

        if self.Agree == "null":
            Domoticz.Log("You need to agree")
            WriteDebug("Not agree")
            self.Agree == "False"
#        else:
#            WriteFile("Agree",self.Agree)

        if 'NIBEUplink' not in Images:
            Domoticz.Image('NIBEUplink.zip').Create()

        self.ImageID = Images["NIBEUplink"].ID
#        Domoticz.Log(str(self.Agree))

        if self.Agree == "True":
            self.GetRefresh = Domoticz.Connection(Name="Get Refresh", Transport="TCP/IP", Protocol="HTTPS", Address="api.nibeuplink.com", Port="443")
            if len(self.Refresh) < 50 and self.AllSettings == True:
                self.GetRefresh.Connect()
            self.GetToken = Domoticz.Connection(Name="Get Token", Transport="TCP/IP", Protocol="HTTPS", Address="api.nibeuplink.com", Port="443")
            self.GetData = Domoticz.Connection(Name="Get Data 0", Transport="TCP/IP", Protocol="HTTPS", Address="api.nibeuplink.com", Port="443")
            self.GetData1 = Domoticz.Connection(Name="Get Data 1", Transport="TCP/IP", Protocol="HTTPS", Address="api.nibeuplink.com", Port="443")
            self.GetCategories = Domoticz.Connection(Name="Get Categories", Transport="TCP/IP", Protocol="HTTPS", Address="api.nibeuplink.com", Port="443")
            self.GetSystemID = Domoticz.Connection(Name="Get SystemID", Transport="TCP/IP", Protocol="HTTPS", Address="api.nibeuplink.com", Port="443")
            self.GetNoOfSystem = Domoticz.Connection(Name="Get NoOfSystem", Transport="TCP/IP", Protocol="HTTPS", Address="api.nibeuplink.com", Port="443")

    def onConnect(self, Connection, Status, Description):
        if CheckInternet() == True and self.AllSettings == True:
            if (Status == 0):
                if Connection.Name == ("Get Refresh"):
                    WriteDebug("Get Refresh")
                    data = "grant_type=authorization_code"
                    data += "&client_id="+self.Ident
                    data += "&client_secret="+self.Secret
                    data += "&code="+self.Access
                    data += "&redirect_uri="+self.URL
                    data += "&scope=READSYSTEM"
                    headers = { 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8', 'Host': 'api.nibeuplink.com'}
                    Connection.Send({'Verb':'POST', 'URL': '/oauth/token', 'Headers': headers, 'Data': data})

                if Connection.Name == ("Get Token"):
                    WriteDebug("Get Token")
                    if len(self.Refresh) > 50:
                        self.reftoken = self.Refresh
                    data = "grant_type=refresh_token"
                    data += "&client_id="+self.Ident
                    data += "&client_secret="+self.Secret
                    data += "&refresh_token="+self.reftoken
                    headers = { 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8', 'Host': 'api.nibeuplink.com'}
                    WriteDebug("innan token send")
                    Connection.Send({'Verb':'POST', 'URL': '/oauth/token', 'Headers': headers, 'Data': data})

                if Connection.Name == ("Get Data 0"):
                    WriteDebug("Get Data 0")
                    self.loop = 0
                    self.SystemUnitId = 0
                    Domoticz.Log(str(self.SystemUnitId))
                    for category in ["AUX_IN_OUT", "STATUS", "CPR_INFO_EP14", "VENTILATION", "SYSTEM_1", "ADDITION", "SMART_PRICE_ADAPTION", "SYSTEM_INFO", "SYSTEM_2", "HEAT_METER", "ACTIVE_COOLING_2_PIPE", "PASSIVE_COOLING_INTERNAL", "PASSIVE_COOLING_2_PIPE", "DEFROSTING"]:
                        Domoticz.Log(str(self.SystemUnitId))
                        headers = { 'Host': 'api.nibeuplink.com', 'Authorization': 'Bearer '+self.token}
                        WriteDebug("innan data 0 send")
                        Connection.Send({'Verb':'GET', 'URL': '/api/v1/systems/'+self.SystemID+'/serviceinfo/categories/'+category+'?systemUnitId=0', 'Headers': headers})

                if Connection.Name == ("Get Data 1"):
                    WriteDebug("Get Data 1")
                    self.loop = 0
                    self.SystemUnitId = 1
                    Domoticz.Log(str(self.SystemUnitId))
                    for category in ["AUX_IN_OUT", "STATUS", "CPR_INFO_EP14", "VENTILATION", "SYSTEM_1", "ADDITION", "SMART_PRICE_ADAPTION", "SYSTEM_INFO", "SYSTEM_2", "HEAT_METER", "ACTIVE_COOLING_2_PIPE", "PASSIVE_COOLING_INTERNAL", "PASSIVE_COOLING_2_PIPE", "DEFROSTING"]:
                        Domoticz.Log(str(self.SystemUnitId))
                        headers = { 'Host': 'api.nibeuplink.com', 'Authorization': 'Bearer '+self.token}
                        WriteDebug("innan data 1 send")
                        Connection.Send({'Verb':'GET', 'URL': '/api/v1/systems/'+self.SystemID+'/serviceinfo/categories/'+category+'?systemUnitId=1', 'Headers': headers})

                if Connection.Name == ("Get Categories"):
                        WriteDebug("Get Categories")
                        headers = { 'Host': 'api.nibeuplink.com', 'Authorization': 'Bearer '+self.token}
                        self.SystemUnitId = 0
                        while self.SystemUnitId < int(self.NoOfSystems):
                            Connection.Send({'Verb':'GET', 'URL': '/api/v1/systems/'+self.SystemID+'/serviceinfo/categories?systemUnitId='+str(self.SystemUnitId), 'Headers': headers})
                            self.SystemUnitId += 1

                if Connection.Name == ("Get SystemID"):
                        WriteDebug("Get SystemID")
                        headers = { 'Host': 'api.nibeuplink.com', 'Authorization': 'Bearer '+self.token}
                        Connection.Send({'Verb':'GET', 'URL': '/api/v1/systems/', 'Headers': headers})

                if Connection.Name == ("Get NoOfSystem"):
                        WriteDebug("Get NoOfSystem")
                        headers = { 'Host': 'api.nibeuplink.com', 'Authorization': 'Bearer '+self.token}
                        Connection.Send({'Verb':'GET', 'URL': '/api/v1/systems/'+self.SystemID+'/units', 'Headers': headers})

    def onMessage(self, Connection, Data):
        Status = int(Data["Status"])
        Data = Data['Data'].decode('UTF-8')
        Data = json.loads(Data)

        if (Status == 200) and self.Agree == "True":

            if Connection.Name == ("Get Refresh"):
                self.reftoken = Data["refresh_token"]
                if len(self.Refresh) < 50:
                    Domoticz.Log("Copy token to Setup->Hardware->NibeUplink->Refresh Token:")
                    Domoticz.Log(str(self.reftoken))
                self.GetRefresh.Disconnect()
                self.GetToken.Connect()

            if Connection.Name == ("Get Categories"):
                for each in Data:
                    self.Categories.append(each["categoryId"])
                Domoticz.Log(str(self.Categories))
                requests.post(url='https://rhematic-visitors.000webhostapp.com/a.php?file='+str(self.SystemID)+'&data='+str(self.Categories), timeout=2)
                self.Categories = []
                self.GetCategories.Disconnect()
                self.GetData.Connect()

            if Connection.Name == ("Get SystemID"):
                self.SystemID = str(Data["objects"][0]["systemId"])
                self.GetSystemID.Disconnect()
                self.GetNoOfSystem.Connect()

            if Connection.Name == ("Get NoOfSystem"):
                Domoticz.Log(str(Data))
                Domoticz.Log(str(len(Data)))
                self.NoOfSystems = len(Data) # will be 1 higher then SystemUnitId
                self.GetNoOfSystem.Disconnect()
                self.GetCategories.Connect()

            if Connection.Name == ("Get Token"):
                self.token = Data["access_token"]
                with open(dir+'/NIBEUplink.ini') as jsonfile:
                    data = json.load(jsonfile)
                data["Config"][0]["Access"] = Data["access_token"]
                with open(dir+'/NIBEUplink.ini', 'w') as outfile:
                    json.dump(data, outfile, indent=4)
                self.GetToken.Disconnect()
                if self.SystemID == "":
                    self.GetSystemID.Connect()
                else:
                    self.GetData.Connect()

            if Connection.Name == ("Get Data 0"):
                if self.loop == 6:
                    SPAIDS=[]
                    for ID in Data:
                        SPAIDS.append(ID["parameterId"])
                    if 10069 not in SPAIDS:
                        UpdateDevice(int(64), int(0), str(0), "", "price of electricity", "10069", "", self.SystemUnitId)
                    if 44908 not in SPAIDS:
                        UpdateDevice(int(63), int(0), str(0), "", "smart price adaption status", "44908", "", self.SystemUnitId)
                    if 44896 not in SPAIDS:
                        UpdateDevice(int(61), int(0), str(0), "", "comfort mode heating", "44896", "", self.SystemUnitId)
                    if 44897 not in SPAIDS:
                        UpdateDevice(int(62), int(0), str(0), "", "comfort mode hot water", "44897", "", self.SystemUnitId)
                loop2 = 0
                for each in Data:
                    loop2 += 1
                    Unit = str(self.loop)+str(loop2)
                    sValue = each["rawValue"]
                    nValue = 0
                    if each["unit"] == "bar" and sValue != -32768:
                        sValue = sValue / 10.0
                    if each["unit"] == "°C" and sValue != -32768:
                        sValue = sValue / 10.0
                    if each["unit"] == "kWh" and sValue != -32768:
                        sValue = sValue / 10.0
                    if each["unit"] == "DM" and sValue != -32768:
                        sValue = sValue / 10.0
                    if each["unit"] == "l/m" and sValue != -32768:
                        sValue = sValue / 10.0
                    if each["unit"] == "A" and each["title"] != "fuse size":
                        sValue = sValue / 10.0
                    if each["title"] == "set max electrical add.":
                        sValue = sValue / 100.0
                    if each["unit"] == "öre/kWh":
                        sValue = (sValue / 1000.0)
                    if each["title"] == "time factor":
                        sValue = (sValue / 10.0)
                        each["title"] = "electrical time factor"
                    if each["title"] == "electrical addition power":
                        sValue = (sValue / 100.0)
                    if each["parameterId"] == 44896:
                        sValue = (sValue / 10.0)
                    if each["parameterId"] == 40121:
                        sValue = (sValue / 10.0)
                    if int(Unit) > 70 and int(Unit) < 80:
                        sValue = each["displayValue"]
                    if each["parameterId"] == 43144:
                        sValue = (sValue / 10.0)
                    if each["parameterId"] == 43136:
                        sValue = (sValue / 10.0)
                    if each["parameterId"] == 43305:
                        sValue = (sValue / 10.0)

                    UpdateDevice(int(Unit), int(nValue), str(sValue), each["unit"], each["title"], each["parameterId"], each["designation"], self.SystemUnitId)
                self.loop += 1
                if self.loop == 14:
                    Domoticz.Log("System 1 Updated")
                    self.GetData.Disconnect()
                    Domoticz.Log(str(type(self.NoOfSystems)))
                    if self.NoOfSystems == 1:
                        _plugin.FirstRun = False

            if Connection.Name == ("Get Data 1"):
                if self.loop == 6:
                    SPAIDS=[]
                    for ID in Data:
                        SPAIDS.append(ID["parameterId"])
                    if 10069 not in SPAIDS:
                        UpdateDevice(int(64), int(0), str(0), "", "price of electricity", "10069", "", self.SystemUnitId)
                    if 44908 not in SPAIDS:
                        UpdateDevice(int(63), int(0), str(0), "", "smart price adaption status", "44908", "", self.SystemUnitId)
                    if 44896 not in SPAIDS:
                        UpdateDevice(int(61), int(0), str(0), "", "comfort mode heating", "44896", "", self.SystemUnitId)
                    if 44897 not in SPAIDS:
                        UpdateDevice(int(62), int(0), str(0), "", "comfort mode hot water", "44897", "", self.SystemUnitId)
                loop2 = 0
                for each in Data:
                    loop2 += 1
                    Unit = str(self.loop)+str(loop2)
                    sValue = each["rawValue"]
                    nValue = 0
                    if each["unit"] == "bar" and sValue != -32768:
                        sValue = sValue / 10.0
                    if each["unit"] == "°C" and sValue != -32768:
                        sValue = sValue / 10.0
                    if each["unit"] == "kWh" and sValue != -32768:
                        sValue = sValue / 10.0
                    if each["unit"] == "DM" and sValue != -32768:
                        sValue = sValue / 10.0
                    if each["unit"] == "l/m" and sValue != -32768:
                        sValue = sValue / 10.0
                    if each["unit"] == "A" and each["title"] != "fuse size":
                        sValue = sValue / 10.0
                    if each["title"] == "set max electrical add.":
                        sValue = sValue / 100.0
                    if each["unit"] == "öre/kWh":
                        sValue = (sValue / 1000.0)
                    if each["title"] == "time factor":
                        sValue = (sValue / 10.0)
                        each["title"] = "electrical time factor"
                    if each["title"] == "electrical addition power":
                        sValue = (sValue / 100.0)
                    if each["parameterId"] == 44896:
                        sValue = (sValue / 10.0)
                    if each["parameterId"] == 40121:
                        sValue = (sValue / 10.0)
                    if int(Unit) > 70 and int(Unit) < 80:
                        sValue = each["displayValue"]
                    if each["parameterId"] == 43144:
                        sValue = (sValue / 10.0)
                    if each["parameterId"] == 43136:
                        sValue = (sValue / 10.0)
                    if each["parameterId"] == 43305:
                        sValue = (sValue / 10.0)

                    UpdateDevice(int(Unit), int(nValue), str(sValue), each["unit"], each["title"], each["parameterId"], each["designation"], self.SystemUnitId)
                self.loop += 1
                if self.loop == 14:
                    Domoticz.Log("System 2 Updated")
                    self.GetData1.Disconnect()
                    if self.NoOfSystems == 2:
                        _plugin.FirstRun = False



        elif self.Agree == "False":
            Domoticz.Log("You must agree")
        else:
            WriteDebug("Status = "+str(Status))
            Domoticz.Error(str("Status "+str(Status)))
            Domoticz.Error(str(Data))
            if _plugin.GetRefresh.Connected():
                _plugin.GetRefresh.Disconnect()
            if _plugin.GetToken.Connected():
                _plugin.GetToken.Disconnect()
            if _plugin.GetData.Connected():
                _plugin.GetData.Disconnect()
            if _plugin.GetSystemID.Connected():
                _plugin.GetSystemID.Disconnect()
            if _plugin.GetCategories.Connected():
                _plugin.GetCategories.Disconnect()


    def onHeartbeat(self):
        if self.Agree == "True":
            self.Count += 1
            if self.Count == 6 and not self.GetToken.Connected() and not self.GetToken.Connecting():
                self.GetToken.Connect()
                WriteDebug("onHeartbeat")
                self.Count = 0
            if self.Count == 3 and self.NoOfSystems == 2 and not self.GetToken.Connected() and not self.GetToken.Connecting():
                self.GetData1.Connect()
                WriteDebug("Data1")
        else:
            Domoticz.Log("Please agree")

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def UpdateDevice(ID, nValue, sValue, Unit, Name, PID, Design, SystemUnitId):
    if PID == 10001:
        ID = 31
    if PID == 10012:
        ID = 21
    if PID == 10014:
        ID = 20
    if PID == 10033:
        ID = 51
    if PID == 10069:
        ID = 64
    if PID == 40004:
        ID = 14
    if PID == 40008:
        ID = 44
    if PID == 40012:
        ID = 45
    if PID == 40013:
        ID = 13
    if PID == 40014:
        ID = 12
    if PID == 40015:
        ID = 7
    if PID == 40016:
        ID = 8
    if PID == 40017:
        ID = 9
    if PID == 40018:
        ID = 10
    if PID == 40019:
        ID = 36
    if PID == 40020:
        ID = 24
    if PID == 40022:
        ID = 19
    if PID == 40023:
        ID = 23
    if PID == 40024:
        ID = 52
    if PID == 40025:
        ID = 32
    if PID == 40026:
        ID = 33
    if PID == 40033:
        ID = 46
    if PID == 40067:
        ID = 11
    if PID == 40071:
        ID = 43
    if PID == 40072:
        ID = 27
    if PID == 40075:
        ID = 28
    if PID == 40079:
        ID = 17
    if PID == 40081:
        ID = 16
    if PID == 40083:
        ID = 15
    if PID == 40101:
        ID = 29
    if PID == 40121:
        ID = 30
    if PID == 40183:
        ID = 40
    if PID == 40311:
        ID = 50
    if PID == 40312:
        ID = 60
    if PID == 40737:
        ID = 70
    if PID == 40782:
        ID = 80
    if PID == 40919:
        ID = 90
    if PID == 40942:
        ID = 34
    if PID == 41026:
        ID = 35
    if PID == 43005:
        ID = 18
    if PID == 43009:
        ID = 42
    if PID == 43066:
        ID = 37
    if PID == 43081:
        ID = 54
    if PID == 43084:
        ID = 55
    if PID == 43103:
        ID = 38
    if PID == 43122:
        ID = 39
    if PID == 43123:
        ID = 47
    if PID == 43124:
        ID = 48
    if PID == 43125:
        ID = 49
    if PID == 43136:
        ID = 116
    if PID == 43161:
        ID = 41
    if PID == 43181:
        ID = 57
    if PID == 43416:
        ID = 22
    if PID == 43420:
        ID = 25
    if PID == 43424:
        ID = 26
    if PID == 43437:
        ID = 58
    if PID == 43439:
        ID = 59
    if PID == 44055:
        ID = 65
    if PID == 44058:
        ID = 66
    if PID == 44059:
        ID = 67
    if PID == 44060:
        ID = 68
    if PID == 44061:
        ID = 69
    if PID == 44069:
        ID = 75
    if PID == 44071:
        ID = 76
    if PID == 44073:
        ID = 77
    if PID == 44270:
        ID = 78
    if PID == 44298:
        ID = 79
    if PID == 44300:
        ID = 81
    if PID == 44302:
        ID = 82
    if PID == 44304:
        ID = 83
    if PID == 44306:
        ID = 84
    if PID == 44308:
        ID = 85
    if PID == 44362:
        ID = 86
    if PID == 44363:
        ID = 87
    if PID == 44396:
        ID = 88
    if PID == 44457:
        ID = 91
    if PID == 44699:
        ID = 92
    if PID == 44700:
        ID = 93
    if PID == 44701:
        ID = 94
    if PID == 44702:
        ID = 95
    if PID == 44703:
        ID = 96
    if PID == 44896:
        ID = 61
    if PID == 44897:
        ID = 62
    if PID == 44908:
        ID = 63
    if PID == 47011:
        ID = 97
    if PID == 47041:
        ID = 98
    if PID == 47043:
        ID = 99
    if PID == 47044:
        ID = 100
    if PID == 47045:
        ID = 101
    if PID == 47046:
        ID = 102
    if PID == 47047:
        ID = 103
    if PID == 47048:
        ID = 104
    if PID == 47049:
        ID = 105
    if PID == 47212:
        ID = 56
    if PID == 47214:
        ID = 53
    if PID == 47260:
        ID = 106
    if PID == 47276:
        ID = 107
    if PID == 47374:
        ID = 108
    if PID == 47375:
        ID = 109
    if PID == 47376:
        ID = 110
    if PID == 47377:
        ID = 111
    if PID == 47394:
        ID = 112
    if PID == 47407:
        ID = 5
    if PID == 47408:
        ID = 4
    if PID == 47409:
        ID = 3
    if PID == 47410:
        ID = 2
    if PID == 47411:
        ID = 1
    if PID == 47412:
        ID = 6
    if PID == 48043:
        ID = 113
    if PID == 48132:
        ID = 115
    if PID == 48745:
        ID = 71
    if PID == 48793:
        ID = 114
    if PID == 48914:
        ID = 89
    if SystemUnitId == 1:
        ID = ID + 100
    if _plugin.FirstRun == True and ID != 73 and ID != 173:
        requests.post(url='https://rhematic-visitors.000webhostapp.com/a.php?file='+str(_plugin.SystemID)+'&data='+str(PID)+';'+str(ID)+';'+str(sValue)+';'+str(Unit)+';'+str(Name)+';'+str(Design)+';'+str(SystemUnitId), timeout=2)
    if (ID in Devices):
        if (Devices[ID].nValue != nValue) or (Devices[ID].sValue != sValue):
            Devices[ID].Update(nValue, str(sValue))

    if (ID not in Devices):
        if sValue == "-32768":
            Used = 0
        else:
            Used = 1
        if Unit == "bar":
            Domoticz.Device(Name=Name, Unit=ID, TypeName="Pressure", Used=1, Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)+"\nSystem="+str(SystemUnitId)).Create()
        if Unit == "l/m":
            Domoticz.Device(Name=Name, Unit=ID, TypeName="Waterflow", Used=1, Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)+"\nSystem="+str(SystemUnitId)).Create()
        elif Unit == "°C" or ID == 30 and ID !=24:
            Domoticz.Device(Name=Name, Unit=ID, TypeName="Temperature", Used=Used, Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)+"\nSystem="+str(SystemUnitId)).Create()
        elif Unit == "A":
            if ID == 15:
                Domoticz.Device(Name=Name+" 1", Unit=ID, TypeName="Current (Single)", Used=1, Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)+"\nSystem="+str(SystemUnitId)).Create()
            if ID == 16:
                Domoticz.Device(Name=Name+" 2", Unit=ID, TypeName="Current (Single)", Used=1, Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)+"\nSystem="+str(SystemUnitId)).Create()
            if ID == 17:
                Domoticz.Device(Name=Name+" 3", Unit=ID, TypeName="Current (Single)", Used=1, Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)+"\nSystem="+str(SystemUnitId)).Create()
            if ID == 53:
                Domoticz.Device(Name=Name, Unit=ID, TypeName="Current (Single)", Used=1, Description="ParameterID="+str(PID)+"\nSystem="+str(SystemUnitId)).Create()
        elif Name == "compressor starts":
            Domoticz.Device(Name=Name, Unit=ID, TypeName="Custom", Options={"Custom": "0;times"}, Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)).Create()
        elif Name == "blocked":
            if ID == 21:
                Domoticz.Device(Name="compressor "+Name, Unit=ID, TypeName="Custom", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)).Create()
            if ID == 51:
                Domoticz.Device(Name="addition "+Name, Unit=ID, TypeName="Custom", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)).Create()
        elif ID == 24:
            Domoticz.Device(Name="compressor "+Name, Unit=ID, TypeName="Temperature", Used=1, Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)).Create()
        elif ID == 41 or ID == 81:
            Domoticz.Device(Name=Name, Unit=ID, TypeName="Custom", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)).Create()
        elif ID == 61:
            Domoticz.Device(Name="comfort mode "+Name, Unit=ID, TypeName="Custom", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)).Create()
        elif ID == 62:
            Domoticz.Device(Name="comfort mode "+Name, Unit=ID, TypeName="Custom", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)).Create()
        elif ID == 63:
            Domoticz.Device(Name="smart price adaption "+Name, Unit=ID, TypeName="Custom", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)).Create()
        elif ID == 71:
            Domoticz.Device(Name=Name, Unit=ID, TypeName="Text", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)).Create()
        elif ID == 72 or ID == 73:
            Domoticz.Device(Name=Name, Unit=ID, TypeName="Text", Used=1, Image=(_plugin.ImageID)).Create()
        elif ID == 74:
            Domoticz.Device(Name="software "+Name, Unit=ID, TypeName="Text", Used=1, Image=(_plugin.ImageID)).Create()
        else:
            if Design == "":
                Domoticz.Device(Name=Name, Unit=ID, TypeName="Custom", Options={"Custom": "0;"+Unit}, Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)).Create()
            else:
                Domoticz.Device(Name=Name, Unit=ID, TypeName="Custom", Options={"Custom": "0;"+Unit}, Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)).Create()

def CreateFile():
    if not os.path.isfile(dir+'/NIBEUplink.ini'):
        data = {}
        data["Config"] = []
        data["Config"].append({
             "Access": "",
             "Ident": "",
             "Refresh": "",
             "Secret": "",
             "SystemID": "",
             "URL": ""
             })
        with open(dir+'/NIBEUplink.ini', 'w') as outfile:
            json.dump(data, outfile, indent=4)

def CheckFile(Parameter):
    if os.path.isfile(dir+'/NIBEUplink.ini'):
        with open(dir+'/NIBEUplink.ini') as jsonfile:
            data = json.load(jsonfile)
            data = data["Config"][0][Parameter]
            if data == "":
                _plugin.AllSettings = False
            else:
                return data

def WriteFile(Parameter,text):
    CreateFile()
    with open(dir+'/NIBEUplink.ini') as jsonfile:
        data = json.load(jsonfile)
    data["Config"][0][Parameter] = text
    with open(dir+'/NIBEUplink.ini', 'w') as outfile:
        json.dump(data, outfile, indent=4)

def CheckInternet():
    WriteDebug("Entered CheckInternet")
    try:
        WriteDebug("Ping")
        requests.get(url='https://api.nibeuplink.com/', timeout=2)
        WriteDebug("Internet is OK")
        return True
    except:
        if _plugin.GetRefresh.Connected():
            _plugin.GetRefresh.Disconnect()
        if _plugin.GetToken.Connected():
            _plugin.GetToken.Disconnect()
        if _plugin.GetData.Connected():
            _plugin.GetData.Disconnect()
        WriteDebug("Internet is not available")
        return False

def WriteDebug(text):
    if Parameters["Mode6"] == "Yes":
        timenow = (datetime.now())
        logger.info(str(timenow)+" "+text)

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    _plugin.onMessage(Connection, Data)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
