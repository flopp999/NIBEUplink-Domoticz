# NIBEUplink Python Plugin
#
# Author: flopp999
#
"""
<plugin key="NIBEUplink" name="NIBE Uplink 0.88" author="flopp999" version="0.88" wikilink="https://github.com/flopp999/NIBEUplink-Domoticz" externallink="https://www.nibeuplink.com">
    <description>
        <h3>NIBE Uplink is used to read data from api.nibeuplink.com</h3><br/>
        <h3>Support me with a coffee &<a href="https://www.buymeacoffee.com/flopp999">https://www.buymeacoffee.com/flopp999</a></h3><br/>
        <h3>or use my Tibber link &<a href="https://tibber.com/se/invite/8af85f51">https://tibber.com/se/invite/8af85f51</a></h3><br/>
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>..</li>
        </ul>
        <h3>Categories that will be fetched, if they exist</h3>
        <ul style="list-style-type:square">
            <li>ACTIVE_COOLING_2_PIPE</li>
            <li>ADDITION</li>
            <li>AHPS</li>
            <li>AUX_IN_OUT</li>
            <li>CPR_INFO_EP14</li>
            <li>DEFROSTING</li>
            <li>EME</li>
            <li>HEAT_METER</li>
            <li>HTS1</li>
            <li>PASSIVE_COOLING_2_PIPE</li>
            <li>PASSIVE_COOLING_INTERNAL</li>
            <li>SMART_ENERGY_SOURCE_PRICES</li>
            <li>SMART_PRICE_ADAPTION</li>
            <li>STATUS</li>
            <li>SYSTEM_1</li>
            <li>SYSTEM_2</li>
            <li>SYSTEM_INFO</li>
            <li>VENTILATION</li>
        </ul>
        <h3>How to get your Identifier, Secret and URL?</h3>
        <h4>&<a href="https://github.com/flopp999/NIBEUplink-Domoticz#identifier-secret-and-callback-url">https://github.com/flopp999/NIBEUplink-Domoticz#identifier-secret-and-callback-url</a></h4>
        <br/>
        <h3>How to get your Access Code?</h3>
        <h4>&<a href="https://github.com/flopp999/NIBEUplink-Domoticz#access-code">https://github.com/flopp999/NIBEUplink-Domoticz#access-code</a></h4>
        <h3>Configuration</h3>
    </description>
    <params>
        <param field="Mode4" label="Uplink Identifier" width="320px" required="true" default="Identifier"/>
        <param field="Mode2" label="Uplink Secret" width="350px" required="true" default="Secret"/>
        <param field="Address" label="Callback URL" width="950px" required="true" default="URL"/>
        <param field="Mode1" label="Access Code" width="350px" required="true" default="Access Code"/>
        <param field="Mode3" label="Refresh Token" width="350px" default="Copy Refresh Token from Log to here" required="true"/>
        <param field="Port" label="Update every" width="100px">
            <options>
                <option label="1 minute" value=6 />
                <option label="5 minutes" value=30 />
                <option label="10 minutes" value=60 />
                <option label="15 minutes" value=90 />
            </options>
        </param>
        <param field="Mode5" label="Show categories" width="50px">
            <options>
                <option label="Yes" value="Yes" />
                <option label="No" value="No" />
            </options>
        </param>
        <param field="Mode6" label="Debug to file (Nibe.log)" width="50px">
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
handler = RotatingFileHandler(dir+'/NIBEUplink.log', maxBytes=1000000, backupCount=5)
logger.addHandler(handler)

categories = ["AUX_IN_OUT", "STATUS", "CPR_INFO_EP14", "VENTILATION", "SYSTEM_1", "ADDITION", "SMART_PRICE_ADAPTION", "SYSTEM_INFO", "SYSTEM_2", "HEAT_METER", "ACTIVE_COOLING_2_PIPE", "PASSIVE_COOLING_INTERNAL", "PASSIVE_COOLING_2_PIPE", "DEFROSTING", "SMART_ENERGY_SOURCE_PRICES", "EME", "HTS1", "AHPS"]

class BasePlugin:
    enabled = False

    def __init__(self):
        self.token = ''
        self.loop = 0
        self.Count = 5
        return

    def onStart(self):
#        Domoticz.Debugging(1)
        WriteDebug("===onStart===")
        self.Ident = Parameters["Mode4"]
        self.ShowCategories = Parameters["Mode5"]
        self.URL = Parameters["Address"]
        self.Access = Parameters["Mode1"]
        self.Secret = Parameters["Mode2"]
        self.Refresh = Parameters["Mode3"]
        self.Update = Parameters["Port"]
        self.Categories = []
        self.SystemID = ""
        self.NoOfSystems = ""
        self.SystemUnitId = 0
        self.FirstRun = True
        self.AllSettings = True

        if len(self.Ident) < 32:
            Domoticz.Log("Identifier too short")
            WriteDebug("Identifier too short")

        if len(self.URL) < 10:
            Domoticz.Log("URL too short")
            WriteDebug("URL too short")

        if len(self.Access) < 370:
            Domoticz.Log("Access Code too short")
            WriteDebug("Access Code too short")

        if len(self.Secret) < 44:
            Domoticz.Log("Secret too short")
            WriteDebug("Secret too short")
        else:
            self.Secret = self.Secret.replace("+", "%2B")

        if len(self.Refresh) < 270:
            Domoticz.Log("Refresh too short")
            WriteDebug("Refresh too short")

        if os.path.isfile(dir+'/NIBEUplink.zip'):
            if 'NIBEUplink' not in Images:
                Domoticz.Image('NIBEUplink.zip').Create()
            self.ImageID = Images["NIBEUplink"].ID

        self.GetRefresh = Domoticz.Connection(Name="Get Refresh", Transport="TCP/IP", Protocol="HTTPS", Address="api.nibeuplink.com", Port="443")
        if len(self.Refresh) < 50 and self.AllSettings == True:
            self.GetRefresh.Connect()
        self.GetToken = Domoticz.Connection(Name="Get Token", Transport="TCP/IP", Protocol="HTTPS", Address="api.nibeuplink.com", Port="443")
        self.GetData = Domoticz.Connection(Name="Get Data 0", Transport="TCP/IP", Protocol="HTTPS", Address="api.nibeuplink.com", Port="443")
        self.GetData1 = Domoticz.Connection(Name="Get Data 1", Transport="TCP/IP", Protocol="HTTPS", Address="api.nibeuplink.com", Port="443")
        self.GetSystemID = Domoticz.Connection(Name="Get SystemID", Transport="TCP/IP", Protocol="HTTPS", Address="api.nibeuplink.com", Port="443")
        self.GetNoOfSystems = Domoticz.Connection(Name="Get NoOfSystems", Transport="TCP/IP", Protocol="HTTPS", Address="api.nibeuplink.com", Port="443")
        self.GetTarget = Domoticz.Connection(Name="Get Target", Transport="TCP/IP", Protocol="HTTPS", Address="api.nibeuplink.com", Port="443")
        self.GetCategories = Domoticz.Connection(Name="Get Categories", Transport="TCP/IP", Protocol="HTTPS", Address="api.nibeuplink.com", Port="443")

    def onDisconnect(self, Connection):
        WriteDebug("onDisconnect called for connection '"+Connection.Name+"'.")

    def onConnect(self, Connection, Status, Description):
        WriteDebug("onConnect")
        if CheckInternet() == True and self.AllSettings == True:
            if (Status == 0):
                headers = { 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8', 'Host': 'api.nibeuplink.com'}
                data = "client_id="+self.Ident
                data += "&client_secret="+self.Secret

                if Connection.Name == ("Get Refresh"):
                    WriteDebug("Get Refresh")
                    data += "&grant_type=authorization_code"
                    data += "&code="+self.Access
                    data += "&redirect_uri="+self.URL
                    data += "&scope=READSYSTEM"
                    Connection.Send({'Verb':'POST', 'URL': '/oauth/token', 'Headers': headers, 'Data': data})

                elif Connection.Name == ("Get Token"):
                    WriteDebug("Get Token")
                    if len(self.Refresh) > 50:
                        self.reftoken = self.Refresh
                    data += "&grant_type=refresh_token"
                    data += "&refresh_token="+self.reftoken
                    Connection.Send({'Verb':'POST', 'URL': '/oauth/token', 'Headers': headers, 'Data': data})

                headers = { 'Host': 'api.nibeuplink.com', 'Authorization': 'Bearer '+self.token}

                if Connection.Name == ("Get Data 0"):
                    WriteDebug("Get Data 0")
                    self.loop = 0
                    self.SystemUnitId = 0
                    for category in categories:
                        Connection.Send({'Verb':'GET', 'URL': '/api/v1/systems/'+self.SystemID+'/serviceinfo/categories/'+category+'?systemUnitId=0', 'Headers': headers})

                elif Connection.Name == ("Get Data 1"):
                    WriteDebug("Get Data 1")
                    self.loop = 0
                    self.SystemUnitId = 1
                    for category in categories:
                        Connection.Send({'Verb':'GET', 'URL': '/api/v1/systems/'+self.SystemID+'/serviceinfo/categories/'+category+'?systemUnitId=1', 'Headers': headers})

                elif Connection.Name == ("Get SystemID"):
                        WriteDebug("Get SystemID")
                        Connection.Send({'Verb':'GET', 'URL': '/api/v1/systems/', 'Headers': headers})

                elif Connection.Name == ("Get NoOfSystems"):
                        WriteDebug("Get NoOfSystems")
                        Connection.Send({'Verb':'GET', 'URL': '/api/v1/systems/'+self.SystemID+'/units', 'Headers': headers})

                elif Connection.Name == ("Get Target"):
                        WriteDebug("Get Target")
                        Connection.Send({'Verb':'GET', 'URL': '/api/v1/systems/'+self.SystemID+'/parameters?parameterIds=47398', 'Headers': headers})

                elif Connection.Name == ("Get Categories"):
                        WriteDebug("Get Categories")
                        self.SystemUnitId = 0
                        while self.SystemUnitId < int(self.NoOfSystems):
                            Connection.Send({'Verb':'GET', 'URL': '/api/v1/systems/'+self.SystemID+'/serviceinfo/categories?systemUnitId='+str(self.SystemUnitId), 'Headers': headers})
                            self.SystemUnitId += 1



    def onMessage(self, Connection, Data):
        Status = int(Data["Status"])

        if (Status == 200):
            Data = Data['Data'].decode('UTF-8')
            Data = json.loads(Data)

            if Connection.Name == ("Get Refresh"):
                self.reftoken = Data["refresh_token"]
                if len(self.Refresh) < 50:
                    Domoticz.Log("Copy token to Setup->Hardware->NibeUplink->Refresh Token:")
                    Domoticz.Log(str(self.reftoken))
                self.GetRefresh.Disconnect()
                self.GetToken.Connect()

            elif Connection.Name == ("Get SystemID"):
                self.SystemID = str(Data["objects"][0]["systemId"])
                self.GetSystemID.Disconnect()
                self.GetNoOfSystems.Connect()

            elif Connection.Name == ("Get NoOfSystems"):
                Domoticz.Log("Systems found:"+str(len(Data)))
                self.NoOfSystems = len(Data) # will be 1 higher then SystemUnitId
                self.GetNoOfSystems.Disconnect()
                if self.FirstRun == True and self.ShowCategories == "Yes":
                    self.GetCategories.Connect()
                self.GetData.Connect()

            elif Connection.Name == ("Get Target"):
                sValue = Data[0]["rawValue"]/10.0
                UpdateDevice(int(117), str(sValue), Data[0]["unit"], Data[0]["title"], Data[0]["parameterId"], Data[0]["designation"], 0)
                self.GetTarget.Disconnect()

            elif Connection.Name == ("Get Token"):
                self.token = Data["access_token"]
                self.GetToken.Disconnect()
                if self.SystemID == "":
                    self.GetSystemID.Connect()
                else:
                    self.GetData.Connect()

            elif Connection.Name == ("Get Categories"):
                for each in Data:
                    self.Categories.append(each["categoryId"])
                Domoticz.Log(str(self.Categories))
                self.GetCategories.Disconnect()

            elif Connection.Name == ("Get Data 0"):
                if self.loop == 6:
                    SPAIDS=[]
                    for ID in Data:
                        SPAIDS.append(ID["parameterId"])
                    if 10069 not in SPAIDS:
                        UpdateDevice(int(64), str(0), "", "price of electricity", 10069, "", self.SystemUnitId)
                    if 44908 not in SPAIDS:
                        UpdateDevice(int(63), str(0), "", "smart price adaption status", 44908, "", self.SystemUnitId)
                    if 44896 not in SPAIDS:
                        UpdateDevice(int(61), str(0), "", "comfort mode heating", 44896, "", self.SystemUnitId)
                    if 44897 not in SPAIDS:
                        UpdateDevice(int(62), str(0), "", "comfort mode hot water", 44897, "", self.SystemUnitId)
                loop2 = 0
                for each in Data:
                    loop2 += 1
                    Unit = str(self.loop)+str(loop2)
                    sValue = each["rawValue"]
                    # unit
                    if each["unit"] == "bar" and sValue != -32768:
                        sValue = sValue / 10.0
                    elif each["unit"] == "°C" and sValue != -32768:
                        sValue = sValue / 10.0
                    elif each["unit"] == "kWh" and sValue != -32768:
                        sValue = sValue / 10.0
                    elif each["unit"] == "DM" and sValue != -32768:
                        sValue = sValue / 10.0
                    elif each["unit"] == "l/m" and sValue != -32768:
                        sValue = sValue / 10.0
                    elif each["unit"] == "A" and each["title"] != "fuse size":
                        sValue = sValue / 10.0
                    elif each["unit"] == "öre/kWh":
                        sValue = (sValue / 1000.0)
                    # title
                    if each["title"] == "set max electrical add.":
                        sValue = sValue / 100.0
                    elif each["title"] == "time factor":
                        sValue = (sValue / 10.0)
                        each["title"] = "electrical time factor"
                    elif each["title"] == "electrical addition power":
                        sValue = (sValue / 100.0)
                    # parameterId
                    if each["parameterId"] == 44896:
                        sValue = (sValue / 10.0)
                    elif each["parameterId"] == 40121:
                        sValue = (sValue / 10.0)
                    elif each["parameterId"] == 43144:
                        sValue = (sValue / 10.0)
                    elif each["parameterId"] == 43136:
                        sValue = (sValue / 10.0)
                    elif each["parameterId"] == 43305:
                        sValue = (sValue / 10.0)
                    # other
                    if int(Unit) > 70 and int(Unit) < 80:
                        sValue = each["displayValue"]
                    UpdateDevice(int(Unit), str(sValue), each["unit"], each["title"], each["parameterId"], each["designation"], self.SystemUnitId)
                self.loop += 1
                if self.loop == len(categories)-1:
                    Domoticz.Log("System 1 Updated")
                    self.GetData.Disconnect()
                    self.GetTarget.Connect()

            elif Connection.Name == ("Get Data 1"):
                if self.loop == 6:
                    SPAIDS=[]
                    for ID in Data:
                        SPAIDS.append(ID["parameterId"])
                    if 10069 not in SPAIDS:
                        UpdateDevice(int(64), str(0), "", "price of electricity", 10069, "", self.SystemUnitId)
                    if 44908 not in SPAIDS:
                        UpdateDevice(int(63), str(0), "", "smart price adaption status", 44908, "", self.SystemUnitId)
                    if 44896 not in SPAIDS:
                        UpdateDevice(int(61), str(0), "", "comfort mode heating", 44896, "", self.SystemUnitId)
                    if 44897 not in SPAIDS:
                        UpdateDevice(int(62), str(0), "", "comfort mode hot water", 44897, "", self.SystemUnitId)
                loop2 = 0
                for each in Data:
                    loop2 += 1
                    Unit = str(self.loop)+str(loop2)
                    sValue = each["rawValue"]
                    if each["unit"] == "bar" and sValue != -32768:
                        sValue = sValue / 10.0
                    elif each["unit"] == "°C" and sValue != -32768:
                        sValue = sValue / 10.0
                    elif each["unit"] == "kWh" and sValue != -32768:
                        sValue = sValue / 10.0
                    elif each["unit"] == "DM" and sValue != -32768:
                        sValue = sValue / 10.0
                    elif each["unit"] == "l/m" and sValue != -32768:
                        sValue = sValue / 10.0
                    elif each["unit"] == "A" and each["title"] != "fuse size":
                        sValue = sValue / 10.0
                    elif each["unit"] == "öre/kWh":
                        sValue = (sValue / 1000.0)
                    if each["title"] == "set max electrical add.":
                        sValue = sValue / 100.0
                    elif each["title"] == "time factor":
                        sValue = (sValue / 10.0)
                        each["title"] = "electrical time factor"
                    elif each["title"] == "electrical addition power":
                        sValue = (sValue / 100.0)
                    if each["parameterId"] == 44896:
                        sValue = (sValue / 10.0)
                    elif each["parameterId"] == 40121:
                        sValue = (sValue / 10.0)
                    elif each["parameterId"] == 43144:
                        sValue = (sValue / 10.0)
                    elif each["parameterId"] == 43136:
                        sValue = (sValue / 10.0)
                    elif each["parameterId"] == 43305:
                        sValue = (sValue / 10.0)
                    elif each["parameterId"] == 44701:
                        sValue = (sValue / 10.0)
                    if int(Unit) > 70 and int(Unit) < 80:
                        sValue = each["displayValue"]

                    UpdateDevice(int(Unit), str(sValue), each["unit"], each["title"], each["parameterId"], each["designation"], self.SystemUnitId)
                self.loop += 1
                if self.loop == len(categories)-1:
                    Domoticz.Log("System 2 Updated")
                    self.GetData1.Disconnect()



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
            if _plugin.GetTarget.Connected():
                _plugin.GetTarget.Disconnect()
            if _plugin.GetNoOfSystems.Connected():
                _plugin.GetNoOfSystems.Disconnect()


    def onHeartbeat(self):
        if _plugin.GetRefresh.Connected() or _plugin.GetRefresh.Connecting():
            _plugin.GetRefresh.Disconnect()
        if _plugin.GetToken.Connected() or _plugin.GetToken.Connecting():
            _plugin.GetToken.Disconnect()
        if _plugin.GetData.Connected() or _plugin.GetData.Connecting():
            _plugin.GetData.Disconnect()
        if _plugin.GetData1.Connected() or _plugin.GetData1.Connecting():
            _plugin.GetData1.Disconnect()
        if _plugin.GetSystemID.Connected() or _plugin.GetSystemID.Connecting():
            _plugin.GetSystemID.Disconnect()
        if _plugin.GetNoOfSystems.Connected() or _plugin.GetNoOfSystems.Connecting():
            _plugin.GetNoOfSystems.Disconnect()
        if _plugin.GetTarget.Connected() or _plugin.GetTarget.Connecting():
            _plugin.GetTarget.Disconnect()

        self.Count += 1
        if self.Count >= int(self.Update) and not self.GetToken.Connected() and not self.GetToken.Connecting():
            self.GetToken.Connect()
            WriteDebug("onHeartbeat")
            self.Count = 0
        if self.Count >= int(self.Update) + 3 and self.NoOfSystems == 2 and not self.GetToken.Connected() and not self.GetToken.Connecting():
                self.GetData1.Connect()
                WriteDebug("Data1")

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def UpdateDevice(ID, sValue, Unit, Name, PID, Design, SystemUnitId):

    if PID == 10001:
        ID = 31
    elif PID == 10012:
        ID = 21
    elif PID == 10014:
        ID = 20
    elif PID == 10033:
        ID = 51
    elif PID == 10069:
        ID = 64
    elif PID == 40004:
        ID = 14
    elif PID == 40008:
        ID = 44
    elif PID == 40012:
        ID = 45
    elif PID == 40013:
        ID = 13
    elif PID == 40014:
        ID = 12
    elif PID == 40015:
        ID = 7
    elif PID == 40016:
        ID = 8
    elif PID == 40017:
        ID = 9
    elif PID == 40018:
        ID = 10
    elif PID == 40019:
        ID = 36
    elif PID == 40020:
        ID = 24
    elif PID == 40022:
        ID = 19
    elif PID == 40023:
        ID = 23
    elif PID == 40024:
        ID = 52
    elif PID == 40025:
        ID = 32
    elif PID == 40026:
        ID = 33
    elif PID == 40033:
        ID = 46
    elif PID == 40067:
        ID = 11
    elif PID == 40071:
        ID = 43
    elif PID == 40072:
        ID = 27
    elif PID == 40075:
        ID = 28
    elif PID == 40079:
        ID = 17
    elif PID == 40081:
        ID = 16
    elif PID == 40083:
        ID = 15
    elif PID == 40101:
        ID = 29
    elif PID == 40121:
        ID = 30
    elif PID == 40152:
        ID = 118
    elif PID == 40183:
        ID = 40
    elif PID == 40311:
        ID = 50
    elif PID == 40312:
        ID = 60
    elif PID == 40737:
        ID = 70
    elif PID == 40771:
        ID = 117
    elif PID == 40782:
        ID = 80
    elif PID == 40919:
        ID = 90
    elif PID == 40942:
        ID = 34
    elif PID == 41002:
        ID = 119
    elif PID == 41026:
        ID = 35
    elif PID == 41162:
        ID = 120
    elif PID == 41163:
        ID = 121
    elif PID == 41164:
        ID = 122
    elif PID == 41167:
        ID = 123
    elif PID == 41427:
        ID = 124
    elif PID == 43005:
        ID = 18
    elif PID == 43009:
        ID = 42
    elif PID == 43066:
        ID = 37
    elif PID == 43081:
        ID = 54
    elif PID == 43091:
        ID = 125
    elif PID == 43084:
        ID = 55
    elif PID == 43103:
        ID = 38
    elif PID == 43122:
        ID = 39
    elif PID == 43123:
        ID = 47
    elif PID == 43124:
        ID = 48
    elif PID == 43125:
        ID = 49
    elif PID == 43136:
        ID = 116
    elif PID == 43161:
        ID = 41
    elif PID == 43181:
        ID = 57
    elif PID == 43416:
        ID = 22
    elif PID == 43420:
        ID = 25
    elif PID == 43424:
        ID = 26
    elif PID == 43437:
        ID = 58
    elif PID == 43439:
        ID = 59
    elif PID == 44014:
        ID = 126
    elif PID == 44055:
        ID = 65
    elif PID == 44058:
        ID = 66
    elif PID == 44059:
        ID = 67
    elif PID == 44060:
        ID = 68
    elif PID == 44061:
        ID = 69
    elif PID == 44069:
        ID = 75
    elif PID == 44071:
        ID = 76
    elif PID == 44073:
        ID = 77
    elif PID == 44270:
        ID = 78
    elif PID == 44298:
        ID = 79
    elif PID == 44300:
        ID = 81
    elif PID == 44302:
        ID = 82
    elif PID == 44304:
        ID = 83
    elif PID == 44306:
        ID = 84
    elif PID == 44308:
        ID = 85
    elif PID == 44362:
        ID = 86
    elif PID == 44363:
        ID = 87
    elif PID == 44396:
        ID = 88
    elif PID == 44457:
        ID = 91
    elif PID == 44699:
        ID = 92
    elif PID == 44700:
        ID = 93
    elif PID == 44701:
        ID = 94
    elif PID == 44702:
        ID = 95
    elif PID == 44703:
        ID = 96
    elif PID == 44896:
        ID = 61
    elif PID == 44897:
        ID = 62
    elif PID == 44908:
        ID = 63
    elif PID == 47011:
        ID = 97
    elif PID == 47041:
        ID = 98
    elif PID == 47043:
        ID = 99
    elif PID == 47044:
        ID = 100
    elif PID == 47045:
        ID = 101
    elif PID == 47046:
        ID = 102
    elif PID == 47047:
        ID = 103
    elif PID == 47048:
        ID = 104
    elif PID == 47049:
        ID = 105
    elif PID == 47212:
        ID = 56
    elif PID == 47214:
        ID = 53
    elif PID == 47260:
        ID = 106
    elif PID == 47276:
        ID = 107
    elif PID == 47374:
        ID = 108
    elif PID == 47375:
        ID = 109
    elif PID == 47376:
        ID = 110
    elif PID == 47377:
        ID = 111
    elif PID == 47394:
        ID = 112
    elif PID == 47398:
        ID = 127
    elif PID == 47407:
        ID = 5
    elif PID == 47408:
        ID = 4
    elif PID == 47409:
        ID = 3
    elif PID == 47410:
        ID = 2
    elif PID == 47411:
        ID = 1
    elif PID == 47412:
        ID = 6
    elif PID == 47613:
        ID = 128
    elif PID == 48043:
        ID = 113
    elif PID == 48132:
        ID = 115
    elif PID == 48366:
        ID = 129
    elif PID == 48745:
        ID = 71
    elif PID == 48793:
        ID = 114
    elif PID == 48914:
        ID = 89
    if SystemUnitId == 1:
        ID = ID + 130
    if (ID in Devices):
        if Devices[ID].sValue != sValue:
            Devices[ID].Update(0, str(sValue))

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
                Domoticz.Device(Name=Name+" 1", Unit=ID, TypeName="Custom", Used=1, Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)+"\nSystem="+str(SystemUnitId)).Create()
            if ID == 16:
                Domoticz.Device(Name=Name+" 2", Unit=ID, TypeName="Custom", Used=1, Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)+"\nSystem="+str(SystemUnitId)).Create()
            if ID == 17:
                Domoticz.Device(Name=Name+" 3", Unit=ID, TypeName="Custom", Used=1, Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)+"\nSystem="+str(SystemUnitId)).Create()
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


def CheckInternet():
    WriteDebug("Entered CheckInternet")
    try:
        WriteDebug("Ping")
        requests.get(url='https://api.nibeuplink.com/', timeout=2)
        WriteDebug("Internet is OK")
        return True
    except:
        if _plugin.GetRefresh.Connected() or _plugin.GetRefresh.Connecting():
            _plugin.GetRefresh.Disconnect()
        if _plugin.GetToken.Connected() or _plugin.GetToken.Connecting():
            _plugin.GetToken.Disconnect()
        if _plugin.GetData.Connected() or _plugin.GetData.Connecting():
            _plugin.GetData.Disconnect()
        if _plugin.GetData1.Connected() or _plugin.GetData1.Connecting():
            _plugin.GetData1.Disconnect()
        if _plugin.GetSystemID.Connected() or _plugin.GetSystemID.Connecting():
            _plugin.GetSystemID.Disconnect()
        if _plugin.GetNoOfSystems.Connected() or _plugin.GetNoOfSystems.Connecting():
            _plugin.GetNoOfSystems.Disconnect()
        if _plugin.GetTarget.Connected() or _plugin.GetTarget.Connecting():
            _plugin.GetTarget.Disconnect()

        WriteDebug("Internet is not available")
        return False

def WriteDebug(text):
    if Parameters["Mode6"] == "Yes":
        timenow = (datetime.now())
        logger.info(str(timenow)+" "+text)

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

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
