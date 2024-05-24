import requests, sys
 
server = "https://rest.ensembl.org"
ext = "/archive/id/ENSG00000157764?"
 
r = requests.get(server+ext, headers={ "Content-Type" : "application/json"})
 
if not r.ok:
  r.raise_for_status()
  sys.exit()
 
decoded = r.json()
#print(repr(decoded))

ext = "/info/species?"
 
r = requests.get(server+ext, headers={ "Content-Type" : "application/json"})
 
if not r.ok:
  r.raise_for_status()
  sys.exit()
 
decoded = r.json()
#print(repr(decoded))

ext = "/vep/human/hgvs/ENSP00000401091.1:p.Tyr124Cys?"
 
r = requests.get(server+ext, headers={ "Content-Type" : "application/json"})
 
if not r.ok:
  r.raise_for_status()
  sys.exit()
 
decoded = r.json()
#print(repr(decoded))

ext = "/vep/human/id/RS1801133?"
 
r = requests.get(server+ext, headers={ "Content-Type" : "application/json"})
 
if not r.ok:
  r.raise_for_status()
  sys.exit()
 
decoded = r.json()
print(repr(decoded)) 