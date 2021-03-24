a=$(curl -H "Authorization: Bearer "$1 "https://api.nibeuplink.com/api/v1/systems/102684")
#echo $a
a=$(curl -H "Authorization: Bearer "$1 "https://api.nibeuplink.com/api/v1/systems/102684/status/system")
#echo $a
a=$(curl -H "Authorization: Bearer "$1 "https://api.nibeuplink.com/api/v1/systems/102684/status/systemUnit")
echo $a
a=$(curl -H "Authorization: Bearer "$1 "https://api.nibeuplink.com/api/v1/systems/102684/config")
#echo $a
a=$(curl -H "Authorization: Bearer "$1 "https://api.nibeuplink.com/api/v1/systems/102684/units")
#echo $a
a=$(curl -H "Authorization: Bearer "$1 "https://api.nibeuplink.com/api/v1/systems/102684/parameter/43416")
#echo $a
a=$(curl -H "Authorization: Bearer "$1 "https://api.nibeuplink.com/api/v1/systems/102684/premium")
#echo $a
a=$(curl -H "Authorization: Bearer "$1 "https://api.nibeuplink.com/api/v1/systems/102684/serviceinfo/categories")
#echo $a
