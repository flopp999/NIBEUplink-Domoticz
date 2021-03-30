# NIBEUplink Python Plugin
#
# Author: flopp999
#
"""
<plugin key="NIBEUplink" name="NIBE Uplink 0.72" author="flopp999" version="0.72" wikilink="https://github.com/flopp999/NIBEUplink-Domoticz" externallink="https://www.nibeuplink.com/">
    <description>
        <h2>NIBE Uplink is used to read data from api.nibeuplink.com</h2><br/>
        <h2>Support me with a coffee &<a href="https://www.buymeacoffee.com/flopp999">https://www.buymeacoffee.com/flopp999</a></h2><br/>
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
            <li>Unit 1xx is ACTIVE_COOLING_2_PIPE</li>
        </ul>
        <h3>How to get your Identifier, Secret and URL?</h3>
        <h4>&<a href="https://github.com/flopp999/NIBEUplink-Domoticz#identifier-secret-and-callback-url">https://github.com/flopp999/NIBEUplink-Domoticz#identifier-secret-and-callback-url</a></h4>
        <h3>How to get your Access Code?</h3>
        <h4>&<a href="https://github.com/flopp999/NIBEUplink-Domoticz#access-code">https://github.com/flopp999/NIBEUplink-Domoticz#access-code</a></h4>
        <h3>How to get your System ID?</h3>
        <h4>&<a href="https://github.com/flopp999/NIBEUplink-Domoticz#system-id">https://github.com/flopp999/NIBEUplink-Domoticz#system-id</a></h4>
        <h3>Configuration</h3>
    </description>
    <params>
        <param field="Username" label="NIBE Uplink Identifier" width="320px" required="true" default="Identifier"/>
        <param field="Mode2" label="NIBE Uplink Secret" width="350px" required="true" default="Secret"/>
        <param field="Address" label="NIBE Callback URL" width="950px" required="true" default="URL"/>
        <param field="Mode1" label="NIBE Access Code" width="350px" required="true" default="Access Code"/>
        <param field="Mode4" label="NIBE System ID" width="140px" required="true" default="ID"/>
        <param field="Mode3" label="NIBE Refresh Token" width="350px" default="Copy Refresh Token from Log to here" required="true"/>
        <param field="Mode5" label="Electricity Company Charge" width="70px" default="0" required="true"/>
        <param field="Mode6" label="Debug to file (Nibe.log)" width="70px">
            <options>
                <option label="Yes" value="Yes" />
                <option label="No" value="No" default="true" />
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
        self.Ident = Parameters["Username"]
        self.URL = Parameters["Address"]
        self.Access = Parameters["Mode1"]
        self.Secret = Parameters["Mode2"]
        self.Refresh = Parameters["Mode3"]
        self.SystemID = Parameters["Mode4"]
        self.Charge = Parameters["Mode5"]
        self.AllSettings = True
        self.Categories = []

        if len(self.Ident) < 32:
            Domoticz.Log("Identifier too short")
            WriteDebug("Identifier too short")
            self.Ident = CheckFile("Ident")
        else:
            WriteFile("Ident",self.Ident)

        if len(self.URL) < 26:
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
            WriteFile("Secret",self.Secret)

        if len(self.Refresh) < 270:
            Domoticz.Log("Refresh too short")
            WriteDebug("Refresh too short")
        else:
            WriteFile("Refresh",self.Refresh)

        if len(self.SystemID) < 4:
            Domoticz.Log("System ID too short")
            WriteDebug("System ID too short")
            self.SystemID = CheckFile("SystemID")
        else:
            WriteFile("SystemID",self.SystemID)

        if 'NIBEUplink' not in Images:
            Domoticz.Image('NIBEUplink.zip').Create()

        self.ImageID = Images["NIBEUplink"].ID

        self.GetRefresh = Domoticz.Connection(Name="Get Refresh", Transport="TCP/IP", Protocol="HTTPS", Address="api.nibeuplink.com", Port="443")
        if len(self.Refresh) < 50 and self.AllSettings == True:
            self.GetRefresh.Connect()
        self.GetToken = Domoticz.Connection(Name="Get Token", Transport="TCP/IP", Protocol="HTTPS", Address="api.nibeuplink.com", Port="443")
        self.GetData = Domoticz.Connection(Name="Get Data", Transport="TCP/IP", Protocol="HTTPS", Address="api.nibeuplink.com", Port="443")
        self.GetCategories = Domoticz.Connection(Name="Get Categories", Transport="TCP/IP", Protocol="HTTPS", Address="api.nibeuplink.com", Port="443")

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
                    headers = { 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8', 'Host': 'api.nibeuplink.com', 'Authorization': ''}
                    Connection.Send({'Verb':'POST', 'URL': '/oauth/token', 'Headers': headers, 'Data': data})

                if Connection.Name == ("Get Token"):
                    WriteDebug("Get Token")
                    if len(self.Refresh) > 50:
                        self.reftoken = self.Refresh
                    data = "grant_type=refresh_token"
                    data += "&client_id="+self.Ident
                    data += "&client_secret="+self.Secret
                    data += "&refresh_token="+self.reftoken
                    headers = { 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8', 'Host': 'api.nibeuplink.com', 'Authorization': ''}
                    WriteDebug("innan token send")
                    Connection.Send({'Verb':'POST', 'URL': '/oauth/token', 'Headers': headers, 'Data': data})

                if Connection.Name == ("Get Data"):
                    WriteDebug("Get Data")
                    if self.Categories == []:
                        self.GetCategories.Connect()
                    self.loop = 0
                    for category in ["AUX_IN_OUT", "STATUS", "CPR_INFO_EP14", "VENTILATION", "SYSTEM_1", "ADDITION", "SMART_PRICE_ADAPTION", "SYSTEM_INFO", "SYSTEM_2", "HEAT_METER", "ACTIVE_COOLING_2_PIPE"]:
#                    for category in self.Categories:
                        headers = { 'Host': 'api.nibeuplink.com', 'Authorization': 'Bearer '+self.token}
                        WriteDebug("innan data send")
                        Connection.Send({'Verb':'GET', 'URL': '/api/v1/systems/'+self.SystemID+'/serviceinfo/categories/'+category, 'Headers': headers})

                if Connection.Name == ("Get Categories"):
                        WriteDebug("Get Categories")
                        headers = { 'Host': 'api.nibeuplink.com', 'Authorization': 'Bearer '+self.token}
                        Connection.Send({'Verb':'GET', 'URL': '/api/v1/systems/'+self.SystemID+'/serviceinfo/categories/', 'Headers': headers})

    def onMessage(self, Connection, Data):
        Status = int(Data["Status"])
        Data = Data['Data'].decode('UTF-8')
        WriteDebug("Status = "+str(Status))
        Data = json.loads(Data)

        if (Status == 200):

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
                self.GetCategories.Disconnect()

            if Connection.Name == ("Get Token"):
                self.token = Data["access_token"]
                with open(dir+'/NIBEUplink.ini') as jsonfile:
                    data = json.load(jsonfile)
                data["Config"][0]["Access"] = Data["access_token"]
                with open(dir+'/NIBEUplink.ini', 'w') as outfile:
                    json.dump(data, outfile, indent=4)
                self.GetToken.Disconnect()
                self.GetData.Connect()

            if Connection.Name == ("Get Data"):
                if self.loop == 6:
                    SPAIDS=[]
                    for ID in Data:
                        SPAIDS.append(ID["parameterId"])
                    if 10069 not in SPAIDS:
                        UpdateDevice(int(64), int(0), str(0), "", "price of electricity", "10069", "")
                    if 44908 not in SPAIDS:
                        UpdateDevice(int(63), int(0), str(0), "", "smart price adaption status", "44908", "")
                    if 44896 not in SPAIDS:
                        UpdateDevice(int(61), int(0), str(0), "", "comfort mode heating", "44896", "")
                    if 44897 not in SPAIDS:
                        UpdateDevice(int(62), int(0), str(0), "", "comfort mode hot water", "44897", "")
                loop2 = 0
                for each in Data:
                    loop2 += 1
                    Unit = str(self.loop)+str(loop2)
                    sValue = each["rawValue"]
                    nValue = 0
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
                        sValue = (((sValue / 1000.0) + float(Parameters["Mode5"])) * 1.25)
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

                    UpdateDevice(int(Unit), int(nValue), str(sValue), each["unit"], each["title"], each["parameterId"], each["designation"])
                self.loop += 1
                if self.loop == 11:
                    Domoticz.Log("Updated")
                    self.GetData.Disconnect()

        else:
            Domoticz.Error(str("Status "+str(Status)))
            Domoticz.Error(str(Data))
            if _plugin.GetRefresh.Connected():
                _plugin.GetRefresh.Disconnect()
            if _plugin.GetToken.Connected():
                _plugin.GetToken.Disconnect()
            if _plugin.GetData.Connected():
                _plugin.GetData.Disconnect()



    def onHeartbeat(self):
        self.Count += 1
        if self.Count == 6 and not self.GetToken.Connected() and not self.GetToken.Connecting():
            self.GetToken.Connect()
            WriteDebug("onHeartbeat")
            self.Count = 0

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def UpdateDevice(ID, nValue, sValue, Unit, Name, PID, Design):
    if PID == 44896:
        ID = 61
    if PID == 44897:
        ID = 62
    if PID == 44908:
        ID = 63
    if PID == 10069:
        ID = 64
    if (ID in Devices):
        if (Devices[ID].nValue != nValue) or (Devices[ID].sValue != sValue):
            Devices[ID].Update(nValue, str(sValue))
    if (ID not in Devices):
        Domoticz.Log(str(ID))
        Domoticz.Log(str(Name))
        Domoticz.Log(str(PID))
        Domoticz.Log(str(Unit))
        Domoticz.Log(str(nValue))
        Domoticz.Log(str(sValue))

        if sValue == "-32768":
            return
        elif Unit == "l/m":
            Domoticz.Device(Name=Name, Unit=ID, TypeName="Waterflow", Used=1, Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)).Create()
        elif Unit == "°C" or ID == 56 and ID !=24:
            Domoticz.Device(Name=Name, Unit=ID, TypeName="Temperature", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)).Create()
        elif Unit == "A":
            if ID == 15:
                Domoticz.Device(Name=Name+" 1", Unit=ID, TypeName="Current (Single)", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)).Create()
            if ID == 16:
                Domoticz.Device(Name=Name+" 2", Unit=ID, TypeName="Current (Single)", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)).Create()
            if ID == 17:
                Domoticz.Device(Name=Name+" 3", Unit=ID, TypeName="Current (Single)", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)).Create()
            if ID == 53:
                Domoticz.Device(Name=Name, Unit=ID, TypeName="Current (Single)", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)).Create()
        elif Name == "compressor starts":
            Domoticz.Device(Name=Name, Unit=ID, TypeName="Custom", Options={"Custom": "0;times"}, Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)).Create()
        elif Name == "blocked":
            if ID == 21:
                Domoticz.Device(Name="compressor "+Name, Unit=ID, TypeName="Custom", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)).Create()
            if ID == 51:
                Domoticz.Device(Name="addition "+Name, Unit=ID, TypeName="Custom", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)).Create()
        elif ID == 24:
            Domoticz.Device(Name="compressor "+Name, Unit=ID, TypeName="Temperature", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)).Create()
        elif ID == 41 or ID == 81:
            Domoticz.Device(Name=Name, Unit=ID, TypeName="Custom", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)).Create()
        elif ID == 61:
            Domoticz.Device(Name="comfort mode "+Name, Unit=ID, TypeName="Custom", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)).Create()
        elif ID == 62:
            Domoticz.Device(Name="comfort mode "+Name, Unit=ID, TypeName="Custom", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)).Create()
        elif ID == 63:
            Domoticz.Device(Name="smart price adaption "+Name, Unit=ID, TypeName="Custom", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)).Create()
        elif ID == 71:
            Domoticz.Log("71")
            Domoticz.Device(Name=Name, Unit=ID, TypeName="Text", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)).Create()
        elif ID == 72 or ID == 73:
            Domoticz.Log("72")
            Domoticz.Device(Name=Name, Unit=ID, TypeName="Text", Used=1, Image=(_plugin.ImageID)).Create()
        elif ID == 74:
            Domoticz.Device(Name="software "+Name, Unit=ID, TypeName="Text", Used=1, Image=(_plugin.ImageID)).Create()
        else:
            if Design == "":
                Domoticz.Log("tomt"+str(ID))
                Domoticz.Device(Name=Name, Unit=ID, TypeName="Custom", Options={"Custom": "0;"+Unit}, Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)).Create()
            else:
                Domoticz.Log("med"+str(ID))
                Domoticz.Device(Name=Name, Unit=ID, TypeName="Custom", Options={"Custom": "0;"+Unit}, Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)).Create()

def CreateFile():
    if not os.path.isfile(dir+'/NIBEUplink.ini'):
        data = {}
        data["Config"] = []
        data["Config"].append({
             "Access": "",
             "Charge": "",
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
