from pymongo import MongoClient

nID = 54

print('Try to connect to mongo. Default command - mongod')
client = MongoClient()
client.drop_database('health')
print('Done. Now select db')
database = client['health']
print('Done. Now create some config params')
database['data.system'].save({'config': 'main', 'queue': []})

print('Na done. Now u can start do.py and go to localhost:PORT to connect with id', nID)
