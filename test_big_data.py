import urllib
url = 'https://api.um.warszawa.pl/api/action/datastore_search?resource_id=f2e5503e-927d-4ad3-9500-4ab9e55deb59&limit=5'  
fileobj = urllib.urlopen(url)
print (fileobj.read())