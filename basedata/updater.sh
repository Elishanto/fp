#!/bin/bash
cd ~/code/fp
git pull origin master
sudo pkill -f main.py
sudo python3 main.py