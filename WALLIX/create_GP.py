
# Script de création des groupes primaire de connexion
# Script Name : Create_PG.py
# Script Version 1.0 par Cyrille VERGER Initaialisation le 27/08/24
# Script Versionning ;
# Version : 1.1    Par XXXX modification : WWWWWWW Le (Date)
# Version : 1.2    Par XXXX modification : WWWWWWW Le (Date)
# Version : 1.3    Par XXXX modification : WWWWWWW Le (Date)
# Version : 1.4    Par XXXX modification : WWWWWWW Le (Date)





import urllib3
import ldap3
import json
import requests
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings()
from datetime import datetime


#Variable date
dateday = datetime.now()
date_texte = dateday.strftime("%d/%m/%Y")
#RECUP USER LDAP
ldap_domain = "MyDomain.lab"
ldap_port = "389"
ldap_user = "cs_ad_Script@MyDomain.lab"
ldap_password = "MyP@ssword"
conn = ldap3.Connection(ldap_domain, user=ldap_user, password=ldap_password)
Wab_Master = "IP ou FQDN"


conn.bind()
ou_path = 'OU=Groupes,OU=Entitée,DC=MyDomain,DC=lab'
conn.search(ou_path, '(objectClass=group)', attributes=['distinguishedName', 'sAMAccountName'])

for entry in conn.entries:
   dn_group = str(entry.distinguishedName)
   sam_group = str(entry.sAMAccountName)
   print(dn_group)
   print(sam_group)
   api_account = "cs_api_script"
   api_pwd = "MyP@ssword"

   # Variables
   group_name = sam_group
   description = "groupe " + sam_group + " fait le " + date_texte
   timeframes = ["allthetime"]
   users = ["admin"] #permet l'ajout à tous les groupes primaire le compte local admin
   profile = "user"

# URL de l'API
   url_PG = "https://" + Wab_Master + "/api/usergroups"
   url_LDAP = "https://" + Wab_Master + "/api/authdomains/" + ldap_domain + "/mappings"
# Corps de la requête
   payload_PG = {
       "group_name": sam_group,
       "description": description,
       "timeframes": timeframes,
       "users": users,
       "profile": profile,
   }

   payload_LDAP = {
    "user_group": sam_group,
    "external_group": dn_group
   }
# Effectuer la requête POST pour créer le groupe
   response = requests.post(url_PG, auth=(api_account, api_pwd), json=payload_PG, verify=False)

# Vérifier la réponse
   if response.status_code == 204:
       print(f"Groupe '{group_name}' créé avec succès.")
   else:
       print(f"Échec de la création du groupe. Statut: {response.status_code}, Détails: {response.text}")

# Effectuer la requête POST pour ajouter le groupe le LDAP
   response = requests.post(url_LDAP, auth=(api_account, api_pwd), json=payload_LDAP, verify=False)

# Vérifier la réponse
   if response.status_code == 204:
       print(f"Groupe '{group_name}' LDAP créé avec succès.")
   else:
       print(f"Échec de la création du groupe LDAP. Statut: {response.status_code}, Détails: {response.text}")






