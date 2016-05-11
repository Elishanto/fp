#!/bin/bash
cd ~/code/fp
git pull origin master
sudo pkill -f do.py
sudo python3 do.py