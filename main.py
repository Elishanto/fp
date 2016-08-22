import os
import yaml
import shutil

if not os.path.exists('localdata'):
    shutil.copytree('basedata/', 'localdata/')
for var, value in yaml.load(open('localdata/config.yml', 'rb')).items():
    os.environ[var] = str(value)
do = __import__('do')

port = int(os.environ['port'])
os.getenv(str(port))

do.start(port)
