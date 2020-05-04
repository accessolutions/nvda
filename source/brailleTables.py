# A part of NonVisual Desktop Access (NVDA)
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2008-2020 NV Access Limited, Joseph Lee, Babbage B.V., Julien Cochuyt

"""Manages information about available braille translation tables.
"""

import collections
from configobj import ConfigObj
from io import StringIO
from typing import BinaryIO, Generator


#: The directory in which liblouis braille tables are located.
TABLES_DIR = r"louis\tables"

#: Table to use for both input and output if configuration is invalid.
FALLBACK_TABLE_NAME = "en-ueb-g1.ctb"

#: List of directories for braille tables lookup, including custom tables.
tablesDirs = [TABLES_DIR]

#: Information about a braille table.
#: This has the following attributes:
#: * fileName: The file name of the table.
#: * displayname: The name of the table as displayed to the user. This should be translatable.
#: * contracted: C{True} if the table is contracted, C{False} if uncontracted.
#: * output: C{True} if this table can be used for output, C{False} if not.
#: * input: C{True} if this table can be used for input, C{False} if not.
BrailleTable = collections.namedtuple("BrailleTable", ("fileName", "displayName", "contracted", "output", "input"))

#: Maps file names to L{BrailleTable} objects.
_tables = {}

def addTable(fileName, displayName, contracted=False, output=True, input=True):
	"""Register a braille translation table.
	At least one of C{input} or C{output} must be C{True}.
	@param fileName: The file name of the table.
	@type fileName: basestring
	@param displayname: The name of the table as displayed to the user. This should be translatable.
	@type displayName: unicode
	@param contracted: C{True} if the table is contracted, C{False} if uncontracted.
	@type cContracted: bool
	@param output: C{True} if this table can be used for output, C{False} if not.
	@type output: bool
	@param input: C{True} if this table can be used for input, C{False} if not.
	@type input: bool
	"""
	if not output and not input:
		raise ValueError("input and output cannot both be False")
	table = BrailleTable(fileName, displayName, contracted, output, input)
	_tables[fileName] = table


def getTable(fileName: str) -> BrailleTable:
	"""Get information about a table given its file name.
	@return: The table information.
	@raise LookupError: If there is no table registered with this file name.
	"""
	return _tables[fileName]


def getFallbackTable() -> BrailleTable:
	return getTable(FALLBACK_TABLE_NAME)


def listTables():
	"""List all registered braille tables.
	@return: A list of braille tables.
	@rtype: list of L{BrailleTable}
	"""
	return sorted(_tables.values(), key=lambda table: table.displayName)

#: Maps old table names to new table names for tables renamed in newer versions of liblouis.
RENAMED_TABLES = {
	"ar-fa.utb" : "fa-ir-g1.utb",
	"da-dk-g16.utb":"da-dk-g16.ctb",
	"da-dk-g18.utb":"da-dk-g18.ctb",
	"de-de-g0.utb":"de-g0.utb",
	"de-de-g1.ctb":"de-g1.ctb",
	"de-de-g2.ctb":"de-g2.ctb",
	"en-us-comp8.ctb" : "en-us-comp8-ext.utb",
	"fr-ca-g1.utb":"fr-bfu-comp6.utb",
	"Fr-Ca-g2.ctb":"fr-bfu-g2.ctb",
	"gr-bb.ctb": "grc-international-en.utb",
	"gr-gr-g1.utb":"el.ctb",
	"hr.ctb":"hr-comp8.utb",
	"mn-MN.utb":"mn-MN-g1.utb",
	"nl-BE-g1.ctb":"nl-BE-g0.utb",
	"nl-NL-g1.ctb":"nl-NL-g0.utb",
	"no-no.ctb":"no-no-8dot.utb",
	"no-no-comp8.ctb":"no-no-8dot.utb",
	"ru-compbrl.ctb":"ru.ctb",
	"sk-sk-g1.utb":"sk-g1.ctb",
	"UEBC-g1.ctb":"en-ueb-g1.ctb",
	"UEBC-g2.ctb":"en-ueb-g2.ctb",
}


def initialize():
	# Add builtin tables.
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("afr-za-g1.ctb", _("Afrikaans grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("ar-ar-comp8.utb", _("Arabic 8 dot computer braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("ar-ar-g1.utb", _("Arabic grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("ar-ar-g2.ctb", _("Arabic grade 2"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("as-in-g1.utb", _("Assamese grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("be-in-g1.utb", _("Bengali grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("bg.ctb", _("Bulgarian 8 dot computer braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("ckb-g1.ctb", _("Central Kurdish grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("cy-cy-g1.utb", _("Welsh grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("cy-cy-g2.ctb", _("Welsh grade 2"), contracted=True)
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("cs-comp8.utb", _("Czech 8 dot computer braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("cs-g1.ctb", _("Czech grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("da-dk-g08.ctb", _("Danish 8 dot computer braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("da-dk-g16.ctb", _("Danish 6 dot grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("da-dk-g18.ctb", _("Danish 8 dot grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("da-dk-g26.ctb", _("Danish 6 dot grade 2"), contracted=True)
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("da-dk-g28.ctb", _("Danish 8 dot grade 2"), contracted=True)
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("de-de-comp8.ctb", _("German 8 dot computer braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("de-g0.utb", _("German grade 0"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("de-g1.ctb", _("German grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("de-g2.ctb", _("German grade 2"), contracted=True)
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("el.ctb", _("Greek (Greece)"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("en-gb-comp8.ctb", _("English (U.K.) 8 dot computer braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("en-gb-g1.utb", _("English (U.K.) grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("en-GB-g2.ctb", _("English (U.K.) grade 2"), contracted=True)
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("en-nabcc.utb", _("English North American Braille Computer Code"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("en-ueb-g1.ctb", _("Unified English Braille Code grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("en-ueb-g2.ctb", _("Unified English Braille Code grade 2"), contracted=True)
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("en-us-comp6.ctb", _("English (U.S.) 6 dot computer braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("en-us-comp8-ext.utb", _("English (U.S.) 8 dot computer braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("en-us-g1.ctb", _("English (U.S.) grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("en-us-g2.ctb", _("English (U.S.) grade 2"), contracted=True)
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("eo-g1.ctb", _("Esperanto grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("Es-Es-G0.utb", _("Spanish 8 dot computer braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("es-g1.ctb", _("Spanish grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("es-g2.ctb", _("Spanish grade 2"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("et-g0.utb", _("Estonian grade 0"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("ethio-g1.ctb", _("Ethiopic grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("fa-ir-comp8.ctb", _("Persian 8 dot computer braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("fa-ir-g1.utb", _("Persian grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("fi.utb", _("Finnish 6 dot"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("fi-fi-8dot.ctb", _("Finnish 8 dot computer braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("fr-bfu-comp6.utb", _("French (unified) 6 dot computer braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("fr-bfu-comp8.utb", _("French (unified) 8 dot computer braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("fr-bfu-g2.ctb", _("French (unified) grade 2"), contracted=True)
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("ga-g1.utb", _("Irish grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("ga-g2.ctb", _("Irish grade 2"), contracted=True)
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("gu-in-g1.utb", _("Gujarati grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("grc-international-en.utb", _("Greek international braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("he.ctb", _("Hebrew 8 dot computer braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("hi-in-g1.utb", _("Hindi grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("hr-comp8.utb", _("Croatian 8 dot computer braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("hr-g1.ctb", _("Croatian grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("hu-hu-comp8.ctb", _("Hungarian 8 dot computer braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("hu-hu-g1.ctb", _("Hungarian grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("hu-hu-g2.ctb", _("Hungarian grade 2"), contracted=True)
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("is.ctb", _("Icelandic 8 dot computer braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("it-it-comp6.utb", _("Italian 6 dot computer braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("it-it-comp8.utb", _("Italian 8 dot computer braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("ka-in-g1.utb", _("Kannada grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("ko-2006-g1.ctb", _("Korean grade 1 (2006)"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("ko-2006-g2.ctb", _("Korean grade 2 (2006)"), contracted=True)
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("ko-g1.ctb", _("Korean grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("ko-g2.ctb", _("Korean grade 2"), contracted=True)
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("ks-in-g1.utb", _("Kashmiri grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("lt.ctb", _("Lithuanian 8 dot"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("lt-6dot.utb", _("Lithuanian 6 dot"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("Lv-Lv-g1.utb", _("Latvian grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("ml-in-g1.utb", _("Malayalam grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("mn-in-g1.utb", _("Manipuri grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("mn-MN-g1.utb", _("Mongolian grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("mn-MN-g2.ctb", _("Mongolian grade 2"), contracted=True)
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("mr-in-g1.utb", _("Marathi grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("nl-BE-g0.utb", _("Dutch (Belgium) 6 dot"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("nl-NL-g0.utb", _("Dutch (Netherlands) 6 dot"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("nl-comp8.utb", _("Dutch 8 dot"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("no-no-8dot.utb", _("Norwegian 8 dot computer braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("No-No-g0.utb", _("Norwegian grade 0"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("No-No-g1.ctb", _("Norwegian grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("No-No-g2.ctb", _("Norwegian grade 2"), contracted=True)
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("No-No-g3.ctb", _("Norwegian grade 3"), contracted=True)
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("np-in-g1.utb", _("Nepali grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("or-in-g1.utb", _("Oriya grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("pl-pl-comp8.ctb", _("Polish 8 dot computer braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("Pl-Pl-g1.utb", _("Polish grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("pt-pt-comp8.ctb", _("Portuguese 8 dot computer braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("Pt-Pt-g1.utb", _("Portuguese grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("Pt-Pt-g2.ctb", _("Portuguese grade 2"), contracted=True)
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("pu-in-g1.utb", _("Punjabi grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("ro.ctb", _("Romanian"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("ru.ctb", _("Russian computer braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("ru-ru-g1.utb", _("Russian grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("sa-in-g1.utb", _("Sanskrit grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("Se-Se.ctb", _("Swedish 8 dot computer braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("Se-Se-g1.utb", _("Swedish grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("sk-g1.ctb", _("Slovak grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("sl-si-comp8.ctb", _("Slovenian 8 dot computer braille"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("sl-si-g1.utb", _("Slovenian grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("sr-g1.ctb", _("Serbian grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("ta-ta-g1.ctb", _("Tamil grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("te-in-g1.utb", _("Telugu grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("tr.ctb", _("Turkish grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("uk.utb", _("Ukrainian"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("unicode-braille.utb", _("Unicode braille"), output=False)
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("vi-g1.ctb", _("Vietnamese grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("zhcn-g1.ctb", _("Chinese (China, Mandarin) grade 1"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("zhcn-g2.ctb", _("Chinese (China, Mandarin) grade 2"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("zh-hk.ctb", _("Chinese (Hong Kong, Cantonese)"))
	# Translators: The name of a braille table displayed in the
	# braille settings dialog.
	addTable("zh-tw.ctb", _("Chinese (Taiwan, Mandarin)"))

	# Add custom tables.
	import os
	from logHandler import log
	customDirs = _getCustomTablesDirs()
	# Insert the custom directories before the default one.
	tablesDirs[:0] = customDirs
	# Reversing the order ensures that user defined configuration takes
	# precedence over addons.
	for dir_ in reversed(customDirs):
		try:
			dirList = os.listdir(dir_)
		# Redundant check, in case an add-on added an external directory to the list.
		except FileNotFoundError:
			log.error(f"Directory not found: {dir_}")
			continue
		for fileName in dirList:
			path = os.path.join(dir_, fileName)
			if os.path.isfile(path) and fileName.endswith(".ini"):
				try:
					with open(path, "rb") as file_:
						manifest = CustomTablesManifest(file_)
						loadCustomTablesConfig(manifest.dict())
				except Exception:
					log.exception(f"Error while applying custom braille tables config: {path}")


def terminate():
	global tablesDirs, _tables
	tablesDirs = [TABLES_DIR]
	_tables = {}


def _getCustomTablesDirs() -> Generator[str, None, None]:
	"""Retrieve the custom braille tables directories.
	
	These are "brailleTables" sub-directories searched after in order in:
	 - The scratchpad directory, if enabled.
	 - Every running addon.
	"""
	import os

	def candidates() -> Generator[str, None, None]:
		import config
		import globalVars
		if (
			not globalVars.appArgs.secure
			and config.conf['development']['enableScratchpadDir']
		):
			yield os.path.join(config.getScratchpadDir(), "brailleTables")
		import addonHandler
		for addon in addonHandler.getRunningAddons():
			yield os.path.join(addon.path, "brailleTables")

	return [dir_ for dir_ in candidates() if os.path.isdir(dir_)]


class CustomTablesManifest(ConfigObj):
	"""Information regarding one or more custom braille tables.
	"""
	configspec = ConfigObj(StringIO(
		"""# NVDA Custom Braille Tables Manifest ConfigObj specification
# Table file name (not the full path)
[__many__]
	contracted = boolean(default=false)
	input = boolean(default=true)
	output = boolean(default=true)
	[[displayName]]
		# The key is a locale code (eg. "de", "pt_BR", ...).
		# The value is the displayName for that locale.
		__many__ = string()"""
	))

	def __init__(self, file_: BinaryIO):
		""" Initializes an L{CustomTablesManifest} instance from a file.
		@param file_: The manifest file-like object, opened in binary mode.
		"""
		super(CustomTablesManifest, self).__init__(
			file_,
			configspec=self.configspec,
			encoding='utf-8',
			default_encoding='utf-8'
		)


def loadCustomTablesConfig(data: dict):
	"""Load the configuration data for custom tables.
	
	The expected data is a dictionary, typically loaded from a ConfigObj .ini file, of the form:
	{
		"filename1.utb": <TABLE_CONFIGURATION>,
		"filename2.utb": <TABLE_CONFIGURATION>,
		...
	}
	
	Expected TABLE_CONFIGURATION is of the form:
	{
		"contracted": <bool>,  # Optional, defaults to False
		"output": <bool>,      # Optional, defaults to True
		"input": <bool>,       # Optional, defaults to True
		"displayName": <DISPLAY_NAME>
	}
	
	DISPLAY_NAME, if specified, can either be a string literal or a dictionary
	mapping language or country codes to string literals.
	If omitted, the display name will be the file name.
	"""
	for fileName, tableCfg in data.items():
		addTable(
			fileName,
			displayName=_getCustomTableDisplayName(fileName, tableCfg),
			contracted=tableCfg.get("contracted", False),
			output=tableCfg.get("output", True),
			input=tableCfg.get("input", True)
		)


def _getCustomTableDisplayName(fileName: str, tableCfg: dict) -> str:
	"""Retrieve the appropriate display name for the given custom braille table configuration.
	"""
	try:
		value = tableCfg.get("displayName")
	except KeyError:
		return fileName
	if isinstance(value, str):
		return _(value)
	if not isinstance(value, dict):
		raise ValueError(
			f"Unexpected displayName value for custom braille table {fileName}: {value}"
		)
	import languageHandler
	lang = languageHandler.getLanguage()
	displayName = value.get(lang)
	if not displayName:
		displayName = value.get(lang.split("_")[0])
	if not displayName:
		displayName = value.get("en_US")
	if not displayName:
		displayName = value.get("en")
	if not displayName:
		displayName = fileName
	return displayName
