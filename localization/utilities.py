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
_ = translator.gettext


def translate_iterable(iterable):
    """
    Recursively iterates through all iterables and attempts to translate all strings found
    """
    if language == 'ko':
        return iterable

    elif isinstance(iterable, str):
        return translate_string(iterable)

    elif isinstance(iterable, (set, list, tuple)):
        return_type = type(iterable)

        translated_list = []
        for item in iterable:
            translated_list.append(translate_iterable(item))
        return return_type(translated_list)

    elif isinstance(iterable, dict):
        translated_dict = {}
        for key, value in list(iterable.items()):
            translated_key = key
            if isinstance(key, str):
                translated_key = translate_string(key)

            translated_value = translate_iterable(value)
            translated_dict[translated_key] = translated_value
        return translated_dict

    else:
        return iterable


def translate_string(string):
    if language == 'ko':
        return string
    translated_string = ''
    # Try to translate the entire string as is first
    if not _(string) == string:
        return _(string)
    else:
        # Attempt to find each grouping within the string and translate the substring
        # eg 'X(Y)' as seen with skill names should be translated X then Y and rebuilt as 'x(y)'
        string_parts = string.split('(')
        for count, part in enumerate(string_parts):
            if not part:
                translated_string += '('
                continue
            elif not count == 0 and string_parts[count-1]:
                if part.endswith(')'):
                    translated_string += f"({_(part[:-1])})"
                else:
                    translated_string += f"({_(part)}"
            else:
                if part.endswith(')'):
                    translated_string += f"{_(part[:-1])})"
                else:
                    translated_string += _(part)

        return translated_string
