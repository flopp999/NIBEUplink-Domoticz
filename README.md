Please use my Tibber invite code, then we both get SEK 500, to use in Tibber shop.  
https://tibber.com/se/invite/8af85f51
---
Create a folder with name "NIBEUplink" in "domoticz/plugins"  
Put plugin.py, requirements.txt in that folder

or

Run in domoticz/plugins "sudo git clone h<span>ttps://gith<span>ub.com/flopp999/NIBEUplink-Domoticz NIBEUplink"  

Run "pip3 install -r requirements.txt" to install all packages that this plugin needs

---
You need to have some information to be able to use this plugin:  
[Identifier](https://github.com/flopp999/NIBEUplink-Domoticz/blob/main/README.md#Identifier,-Secret-and-URL)  
[Secret](https://github.com/flopp999/NIBEUplink-Domoticz/blob/main/README.md#Identifier,-Secret-and-URL)  
[Callback URL](https://github.com/flopp999/NIBEUplink-Domoticz/blob/main/README.md#Identifier,-Secret-and-Callback-URL)  
[System ID](https://github.com/flopp999/NIBEUplink-Domoticz/blob/main/README.md#System-ID)  
[Charge from your electricity company](https://github.com/flopp999/NIBEUplink-Domoticz/blob/main/README.md#Charge-from-your-electricity-company)  
[Access code](https://github.com/flopp999/NIBEUplink-Domoticz/blob/main/README.md#Access-code)

# Identifier, Secret and Callback URL
Login to [NIBE Uplink API](https://api.nibeuplink.com/)  
Create an application under My Applications  
For Callback URL use "h<span>ttps://a<span>pi.nib<span>euplink.com/"  
Copy Identifier, Secret and Callback URL, paste to NIBEUplink hardware in Domoticz  

# System ID
Login to [NIBE Uplink](https://nibeuplink.com/)  
When logged in, look at the address bar, "h<span>ttps://w<i></i>ww.<span>nibeuplink.com/System/xxxxxx/Status/Overview", xxxxxx is your System ID  
Copy your System ID and paste to NIBEUplink hardware in Domoticz  

# Charge from your electricity company
You need to add the total extra charge your electricity company have, without taxes  
e.g. Tibber have SEK 1.55 at the moment  

# Access code
You need to create an Access code before first use  
Click on the link below, you will get an error, that is OK  
https://api.nibeuplink.com/oauth/authorize?client_id=yyyyyy&scope=READSYSTEM&state=x&redirect_uri=https://api.nibeuplink.com/&response_type=code  
Once you clicked it, in the address bar change yyyyyy to your Identifier, NOT YOUR SYSTEM ID!!!  
Then it will ask you to login and accept.  
When this is done the address bar will look something like below  
"h<span>ttps://a<span>pi.nib<span>euplink.com/?code=ndfhj3u38ufhswhnerjqa5zEyN-RmBgkTCc&state=x"  
Copy everything after "...code=" and before "&state...", the code above is just an example, normally the code is ~380 characters
Above example have access code "ndfhj3u38ufhswhnerjqa5zEyN-RmBgkTCc"


Support me with a coffee https://www.buymeacoffee.com/flopp999 or use my Tibber link https://tibber.com/se/invite/8af85f51
