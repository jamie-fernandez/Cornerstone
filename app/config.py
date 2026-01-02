import os
import sys
import logging

DEBUG = False
BASE_PATH = ""
HTML_PATH = ""

if getattr(sys, "frozen", False):
    BASE_PATH = sys._MEIPASS  # PyInstaller temp folder
    DEBUG = False
else:
    BASE_PATH = os.path.dirname(__file__)
    DEBUG = True

if DEBUG:
    HTML_PATH = "http://localhost:5173"  # Dev server
else:
    HTML_PATH = "dist/index.html"  # Bundled files

logging.basicConfig(
    level=logging.INFO if DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

APP_NAME = 'Cornerstone'
APP_VERSION = '0.0.0'

CONFIG = {
    "NAME": APP_NAME,
    "VERSION": APP_VERSION,
    "DEBUG": DEBUG,
    "BASE_PATH": BASE_PATH,
    "HTML_PATH": HTML_PATH,
}
