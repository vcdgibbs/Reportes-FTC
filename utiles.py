#!/usr/bin/env python3

import datetime
import requests

class Colores:
    reset='\033[0m'
    bold='\033[01m'
    disable='\033[02m'
    underline='\033[04m'
    reverse='\033[07m'
    strikethrough='\033[09m'
    invisible='\033[08m'
    class fg:
        black='\033[30m'
        red='\033[31m'
        green='\033[32m'
        orange='\033[33m'
        blue='\033[34m'
        purple='\033[35m'
        cyan='\033[36m'
        lightgrey='\033[37m'
        darkgrey='\033[90m'
        lightred='\033[91m'
        lightgreen='\033[92m'
        yellow='\033[93m'
        lightblue='\033[94m'
        pink='\033[95m'
        lightcyan='\033[96m'
    class bg:
        black='\033[40m'
        red='\033[41m'
        green='\033[42m'
        orange='\033[43m'
        blue='\033[44m'
        purple='\033[45m'
        cyan='\033[46m'
        lightgrey='\033[47m'


def valid_ip(address):
    try:
        host_bytes = address.split('.')
        valid = [int(b) for b in host_bytes]
        valid = [b for b in valid if b >= 0 and b<=255]
        return len(host_bytes) == 4 and len(valid) == 4
    except:
        return False

def is_number(n):
       try:
           float(n)   # Type-casting the string to `float`.
                      # If string is not a valid `float`, 
                      # it'll raise `ValueError` exception
       except ValueError:
           return False
       return True

# Fucntion to get a dict class with parameter
'''
The idea is the convert params of:

$ command -param1 val1 -param2 val2 option1 option2

so "-param1 val1" will be a key:value pair as {"param1":"val1"}
and 
if "option1" is text, it will we a key:value pair as {"option1":True}
if "option1" is a number, it will be as {"option1":number} 

Note: All params will be converted to lowercase, values and options will be as entered, for example:

$ comamand -PaRams1 Val1 Option1 oPtiOn2  will take the following form:

returned={'params1'='Val1', 'Option1'=1, 'oPtiOn2'=1}
'''

def params2dict(args):
    #print(len(args))
    # args[0] -> comando mismo
    # args[1] .. args[n] -> parametros

    p={}
    # option_number
    on=1 
    i=1

    while i<len(args):
        try:
            if args[i][0] == "-":
                # We expect a value for a parameter, so next argument can't begin with '-'
                if args[i+1][0] == "-":
                    p={"error":"expected value for " + args[i]}
                    break
                #print("está " + args[i][0] + " bien?" +args[i])
                temp=args[i].strip('-')
                p[temp.lower()]=args[i+1]
                i+=2
            else:
                if is_number(args[i]):
                        nopt = "option" + str(on)
                        # is the number an 'int' or 'float'?  - check whether there is a decimal dot.
                        if args[i].count(".")==1:
                            p[nopt]=float(args[i])
                        else:
                            p[nopt]=int(args[i])
                        on+=1
                else:
                    p[args[i]]=1
                i+=1
            #p[args[i]]=args[i+1]
        except:
            p={"error":"expected value"}
            i+=1
            break
        
    return p

# Just an easy way...
def printInfo(msg):
    fh=str(datetime.datetime.now())
    print(fh + Colores.fg.green + " [INFO] " + msg + Colores.reset)
    return 0

def printError(msg):
    fh=str(datetime.datetime.now())
    print(fh + Colores.fg.red + " [ERROR] " + msg + Colores.reset)
    return 0

def printWarning(msg):
    fh=str(datetime.datetime.now())
    print(fh + Colores.fg.yellow + " [WARNING] " + msg + Colores.reset)
    return 0

def printLog(msg):
    fh=str(datetime.datetime.now())
    print(fh  + " [INFO] " + msg )
    return 0


###################################################################################
# API Calls to Prism Central
# https://httpstatuses.com/ is a good page to know the HTTP status codes
###################################################################################

def Prism_API_Call(Method, URL, Credentials, Payload=None):
    #printInfo("Making a " + Method + " call to " + URL)
    headers = {'ContentType':'application/json','cache-control': 'no-cache','Accept':'application/json'}
    us=Credentials["User"]
    pw=Credentials["Password"]
   
    # GET ##########################################################
    if Method == "GET":
        if Payload == None:
            r = requests.get(URL, auth=(us,pw), verify=False)
        else:
            r = requests.get(URL, auth=(us,pw), json=Payload, verify=False)

        if r.status_code!=200 and r.status_code!=202:
            printError("Response code " + str(r.status_code))
    
    # POST #########################################################
    if Method == "POST":
        if Payload == None:
            r = requests.post(URL, auth=(us,pw), verify=False)
        else:
            r = requests.post(URL, auth=(us,pw), json=Payload, verify=False)

        if r.status_code!=200 and r.status_code!=202:
            printError("Response code " + str(r.status_code))

    # PUT ##########################################################
    if Method == "PUT":
        if Payload == None:
            r = requests.put(URL, auth=(us,pw), verify=False)
        else:
            r = requests.put(URL, auth=(us,pw), json=Payload, verify=False)

        if r.status_code!=200 and r.status_code!=202:
            printError("Response code " + str(r.status_code))

    # Python returns a "dict" with the JSON info, so returned value should be json.dumps('d) in order to use it as JSON in another API Call.
    # if returned JSON hasn't status code, I add it to the Dictionay.
    ret =  r.json()
    if "code" not in ret:
        ret["code"]=r.status_code
    return ret
