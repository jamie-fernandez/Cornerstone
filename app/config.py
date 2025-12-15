import json
import os
import sys
import logging

DEBUG_ENV = False
BASE_PATH = ''
HTML_PATH = ''

if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS  # PyInstaller temp folder
    DEBUG_ENV = False
else:
    BASE_PATH = os.path.dirname(__file__)
    DEBUG_ENV = True

if DEBUG_ENV:
    HTML_PATH = 'http://localhost:5173' # Dev server
else:
    HTML_PATH = 'dist/index.html' # Bundled files


logging.basicConfig(
    level=logging.INFO if DEBUG_ENV else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

with open('package.json', 'r') as file:
    data = json.load(file)

APP_NAME = data.get('name')
APP_VERSION = data.get('version')

CONFIG = {
    'NAME': APP_NAME,
    'VERSION': APP_VERSION,
    'DEBUG_ENV': DEBUG_ENV,
    'BASE_PATH': BASE_PATH,
    'HTML_PATH': HTML_PATH,
}
