import os
import do

port = int(os.environ['port'])
os.getenv(str(port))

do.start(port)
