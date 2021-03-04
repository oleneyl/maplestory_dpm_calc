#Translations and Generating .po/.mo files
Translatable strings are surrounded with ```_()``` where ```_``` references the function gettext from the gettext module.
This marks them to be picked up by Babel when generating the .pot file. 
i.e 
```python
import gettext
_ = gettext.gettext
```

In our case we create a single translator instance that can be imported within any of our files to provide translation services.
This is done by importing the translator from the localization utilites and registering it as ```_``` as we did above
```python
# import the translator
from localization.utilities import translator
# register the translator to the _ function
_ = translator.gettext
```
## Limitations and Design Choices
There are limitations on where strings can be in order to be detectable for building our initial .pot file.
```python
# Invalid, will not be detected
string = f"{'BIG'} {_('TEST')}"
# Valid, will be detected 
string = "BIG {}".format(_('TEST'))
# Valid, will be detected
string = _("{} TEST").format('BIG')
# Valid, will be detected
str1 = _('TEST')
str2 = _('STOP')
string = f"{str1} {str2}"
```

All but the first option are valid for getting our strings detected and into our .pot file. 
However, we need to make a design decision based off our code base. Since we normally generate skills 
names as ```SKILL NAME(MODIFIER)``` it makes most sense to make use of standalone strings if possible. As
This will allow us to detect each string individually and translate configuration files after loading.

## Changing languages
By default the dpm calculator will run in Korean. In order to run in English modify the .env file to
```
#.env
LANGUAGE=en
```

## Generating Translatable Messages
From the top level directory of the project run the following command
```
pybabel extract -F babel.cfg -o localization/locales/messages.pot .
```
This creates our base file of messages to be used in our translations.
From this file we can update the .po files which will contain our actual translations.
```
# Update the Korean .po file
pybabel update -i localization/locales/messages.pot -d localization/locales/ -l ko
# Update the English .po file
pybabel update -i localization/locales/messages.pot -d localization/locales/ -l en
```

For new strings not already in the english .po file under localization/locales/en/LC_MESSAGES/messages.po we need to add their translation.

An entry in the .po will look as such, we need to add the translated text in the mgstr field.
```
## Untranslated
#: dpmModule/jobs/blazewizard.py:41
msgid "플레임 템페스타"
msgstr ""

## Translated
#: dpmModule/jobs/blazewizard.py:41
msgid "플레임 템페스타"
msgstr "Flame Tempest"
```
Any untranslated msgid's will default to Korean and remain untranslated.

The final step is to generate the .mo files which will be what the machine uses to perform the string translations.

```
# Compile the .mo files for machine use
pybabel compile -d localization/locales
```
