from os import listdir
from os.path import isfile, join, splitext
from collections import OrderedDict
from urllib.parse import quote

import csv
import json
import requests

from dataloader import DataLoader

if __name__ == '__main__':
    dataLoader = DataLoader()
    dataLoader.load_metadata()
