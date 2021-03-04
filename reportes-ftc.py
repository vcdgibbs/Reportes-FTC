#!/usr/bin/env python3

# número de comuna:
#2345678901234567890123456789012345678901234567890123456789012345678901234567890
helpMsg='''
reportes-ftc.py -params valor opcion

Descripción:  Armar el resporte requerido de los proyectos y uso de recursos en 
              un archivo excel (.xlsx) o un archivo .csv

Parameters:
   -prism <ip>      : Prism Central IP address.
   -user <username> : username who will execute the commands. (optional)
   -password <pwd>  : username's password (optional)


Options:
   archivo : nombre del archivo excel, no es necesario la extensión .xlsx, si no 
   está en el nombre, se agregará automáticamente.
   help    : display this text as help.

Link:  https://github.com/vcdgibbs/Reportes-FTC

Notes:

Author: Victor D'Gibbs (victor.dgibbs@nutanix.com)
Revision:  February 25, 2021

To do:
- todo por ahora

'''
import requests
import json
import urllib3
import sys
import stdiomask
from utiles import *

'''
Se desabilita el "Warning" de conexion insegura. Esto lo dejo asi solo por estar en un ambiente de desarrrollo.
En un ambiente productivo esto no deberia estar.
'''
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# let's construct a DICT class from the arguments:
pars = params2dict(sys.argv)

# Revision de parametros:

if "error" in pars:
    printError(pars['error'])
    exit(1)

if "help" in pars:
    print(helpMsg)
    exit(0)

if "prism" in pars:
    if valid_ip(pars['prism']):
        PC_IP=pars["prism"]
        try:
            t_url="https://"+PC_IP+":9440/console/#login"
            r1 = requests.get(t_url, verify=False)
        except:
            printError("Trying to go to "+ t_url + ", but it is unreachable, is the Prism Central IP address " + PC_IP + " Correct?")
            exit(1)

    else:
        print(Colores.fg.red+"[Error] Please provide a valid IP address." + Colores.reset)
        exit(1)
else:
    print(Colores.fg.red+"[Error] Prism Central address not provided." + Colores.reset)
    exit(1)

if "user" in pars:
    User = pars["user"]
else:
    User = input("User: ")

if "password" in pars:
    Password = pars["password"]
else:
    Password = stdiomask.getpass()

# Variables
API_Server_End_Point="https://" + PC_IP + ":9440/api/nutanix/v3/"
PrismCreds = {
    "User" : User,
    "Password" : Password
    }



###############################################################
# 1. Rescatar la información de los proyectos
###############################################################

comURL=API_Server_End_Point + "projects/list"
pl={"kind":"project"}

try:
    info_proyectos = Prism_API_Call("POST",comURL,PrismCreds,pl)
    # Control: está rescatando lo correcto?
    #print(json.dumps(info_proyectos, indent=2))

except:
        printError("Something get wrong, finishing")
        exit(1)


###############################################################
# 2. Crear tabla (en variable dict) con la información
###############################################################
# tabla_proyectos {
#     "tenant-1" : {"nombre":"<nombre del proyecto",
#                   "owner": "<información del dueño del proyecto>",   // usaré la descripción
#                   "vcpu_uso": "<vcpu usado>",
#                   "vcpu_total": "<vcpu asignado al proyecto>",    // es posible que no tenga cuotas
#                   "mem_uso": "<memoria usada>>",
#                   "mem_total":"<memoria asignada al proyecto>",   // es posible que no tenga cuotas
#                   "hdd_uso": "<storage usado>",
#                   "hdd_total": "<storage asognado al proyecto>"   // es posible que no tenga cutoas
#                   }
# }
i=0
t = {}
tabla_proyectos = {}
while i < int(info_proyectos["metadata"]["length"]):
    nombre_proyecto = info_proyectos["entities"][i]["status"]["name"]
    print(Colores.fg.green + "Proyecto: " + nombre_proyecto + Colores.reset)
    
    if nombre_proyecto.lower() == "default":
        print("Proyecto default no se tomará en cuenta.")
        i+=1
        continue
    
    #t["nombre"]=info_proyectos["entities"][i]["status"]["name"]
    t["nombre"] = nombre_proyecto
    t["owner"]  = info_proyectos["entities"][i]["status"]["description"]

    if len(info_proyectos["entities"][i]["status"]["resources"]["resource_domain"]) == 0:
        t["vcpu_uso"] = 0
        t["vcpu_total"] = 0
        t["mem_uso"] = 0
        t["mem_total"] = 0
        t["hdd_uso"] = 0
        t["hdd_total"] = 0
        i+=1
    else:
        print(info_proyectos["entities"][i]["status"]["resources"]["resource_domain"])
        #print(len(info_proyectos["entities"][i]["status"]["resources"]["resource_domain"]))
        if len(info_proyectos["entities"][i]["status"]["resources"]["resource_domain"]) > 0:
            if "resources" in info_proyectos["entities"][i]["status"]["resources"]["resource_domain"].keys():
                #print(type(info_proyectos["entities"][i]["status"]["resources"]["resource_domain"]["resources"]))
                print(len(info_proyectos["entities"][i]["status"]["resources"]["resource_domain"]["resources"]))
                if len(info_proyectos["entities"][i]["status"]["resources"]["resource_domain"]["resources"]) > 0:
                    for nn  in range (0,len(info_proyectos["entities"][i]["status"]["resources"]["resource_domain"]["resources"])):
                        #print(info_proyectos["entities"][i]["status"]["resources"]["resource_domain"]["resources"][nn].keys())
                        if "limits" in info_proyectos["entities"][i]["status"]["resources"]["resource_domain"]["resources"][nn].keys():
                            total = info_proyectos["entities"][i]["status"]["resources"]["resource_domain"]["resources"][nn]["limits"]
                        else:
                            total = 0 
                        uso = info_proyectos["entities"][i]["status"]["resources"]["resource_domain"]["resources"][nn]["value"]
                        #if ""

                       

                    
        i+=1 


#  with open(pars['sourcecsv']) as csv_file:
#         csv_reader = csv.reader(csv_file, delimiter=',')
#         line_count = 0
#         for row in csv_reader:
#             if line_count == 0:
#                 #print(f'Column names are {", ".join(row)}')
#                 # Init some vars
#                 myVarItem={}
#                 myListVMs={}
#                 line_count += 1
#             else:
#                 # Make sure row has 3 values
#                 if len(row) != 3:
#                     continue
#                 nn=row[0].strip()
#                 cc=row[1].strip()
#                 vv=row[2].strip()
#                 myVarItem = { 
#                     "vm_name" : nn.replace(" ", "_"),
#                     "category_name" : cc.replace(" ", "_"),
#                     "value_name" : vv.replace(" ", "_")
#                 }
#                 vmn = "vm" + str(line_count)
#                 myListVMs[vmn] = myVarItem
#                 line_count += 1
# else:
#     if "vm" in pars and "category" in pars and "value" in pars:
#         # código para dict de una sola VM
#         myVarItem = { 
#             "vm_name" : pars['vm'],
#             "category_name" : pars['category'],
#             "value_name" : pars['value']
#         }
#         myListVMs = { "vm1" : myVarItem }

# for VMS in myListVMs:
    
#     if "add" in pars.keys(): act="add"
#     else: act="remove"
#     Category = myListVMs[VMS]["category_name"]
#     Value = myListVMs[VMS]["value_name"]
