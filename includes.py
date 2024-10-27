import requests
import itertools
import json
from bs4 import BeautifulSoup
from lxml import etree 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep