#!/bin/bash

export LANG=en_US.UTF-8
cd ../
screen -AmdS etl sudo -u siem python3 main.py

