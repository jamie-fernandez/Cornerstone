# app/config.py

import os
import sys

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


CONFIG = {
    'DEBUG_ENV': DEBUG_ENV,
    'BASE_PATH': BASE_PATH,
    'HTML_PATH': HTML_PATH,
}

import logging

logging.basicConfig(
    level=logging.INFO if DEBUG_ENV else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
