from pymongo import MongoClient
nID = 54

print('Try to connect to mongo. Default command - mongod')
client = MongoClient()
print('Done. Now select db')
database = client['health']
print('Done. Now create some config params')
database['data.system'].save({'config':'main', 'queue':[]})
print('Done. Now remove user with id', nID)
database['users'].remove({'id':nID})
print('Done. And now save it!')
database['users'].save({'id':nID, 'valid':1, 'opened_ex':(10,11)})

print('Na done. Now u can start do.py and go to localhost:PORT to connect with id', nID)


