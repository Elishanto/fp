#!/bin/bash
cd ~/dev/fp
git pull origin $1
sudo pkill -f main.py
sudo python3 main.py