import os
import gettext
from dotenv import load_dotenv

# Load our environment variables from the .env file
load_dotenv()

# Get the language to use from translating, defaulting to Korean
language = os.getenv("LANGUAGE")
if not language:
    language = 'ko'

# This is to provide a absolute instead of relative path the the locales directory which ensures there are no errors when importing this into other files
locales_dir = os.getenv("LOCALE_DIR_OVERRIDE")
if not locales_dir:
    locales_dir = os.path.join(os.path.dirname(__file__), 'locales')

# The translator instance which will provide translations to all files that import this as long as the register the gettext function as _
# ie '_ = translator.gettext'
translator = gettext.translation(domain='messages', localedir=locales_dir, languages=[language])