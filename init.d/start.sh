#!/bin/bash
ETL_PATH=/home/siem/PycharmProjects/nspk

export LANG=en_US.UTF-8
cd $ETL_PATH
source venv/bin/activate
screen -AmdS etl_process sudo -u siem python3 main.py

