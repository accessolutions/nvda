# A part of NonVisual Desktop Access (NVDA)
# Copyright (C) 2021 NV Access Limited
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

from dataclasses import (
	dataclass,
	field,
)
from comtypes import (
	GUID,
	byref,
)
from _UIAConstants import (
	UIAutomationType,
)


@dataclass
class CustomPropertyInfo:
	guid: GUID
	programmaticName: str
	uiaType: UIAutomationType
	id: int = field(init=False)

	def __post_init__(self):
		import NVDAHelper
		self.id = NVDAHelper.localLib.registerUIAProperty(
			byref(self.guid),
			self.programmaticName,
			self.uiaType
		)


class CustomProperties:

	def __init__(self):

		self.itemIndex = CustomPropertyInfo(
			guid=GUID("{92A053DA-2969-4021-BF27-514CFC2E4A69}"),
			programmaticName="ItemIndex",
			uiaType=UIAutomationType.Int,
		)

		self.itemCount = CustomPropertyInfo(
			guid=GUID("{ABBF5C45-5CCC-47b7-BB4E-87CB87BBD162}"),
			programmaticName="ItemCount",
			uiaType=UIAutomationType.Int,
		)

		# Microsoft Excel
		self.cellFormula = CustomPropertyInfo(
			guid=GUID("{E244641A-2785-41E9-A4A7-5BE5FE531507}"),
			programmaticName="CellFormula",
			uiaType=UIAutomationType.String,
		)

		self.cellNumberFormat = CustomPropertyInfo(
			guid=GUID("{626CF4A0-A5AE-448B-A157-5EA4D1D057D7}"),
			programmaticName="CellNumberFormat",
			uiaType=UIAutomationType.String,
		)

		self.hasDataValidation = CustomPropertyInfo(
			guid=GUID("{29F2E049-5DE9-4444-8338-6784C5D18ADF}"),
			programmaticName="HasDataValidation",
			uiaType=UIAutomationType.Bool,
		)

		self.hasDataValidationDropdown = CustomPropertyInfo(
			guid=GUID("{1B93A5CD-0956-46ED-9BBF-016C1B9FD75F}"),
			programmaticName="HasDataValidationDropdown",
			uiaType=UIAutomationType.Bool,
		)

		self.dataValidationPrompt = CustomPropertyInfo(
			guid=GUID("{7AAEE221-E14D-4DA4-83FE-842AAF06A9B7}"),
			programmaticName="DataValidationPrompt",
			uiaType=UIAutomationType.String,
		)

		self.hasConditionalFormatting = CustomPropertyInfo(
			guid=GUID("{DFEF6BBD-7A50-41BD-971F-B5D741569A2B}"),
			programmaticName="HasConditionalFormatting",
			uiaType=UIAutomationType.Bool,
		)

		self.areGridLinesVisible = CustomPropertyInfo(
			guid=GUID("{4BB56516-F354-44CF-A5AA-96B52E968CFD}"),
			programmaticName="AreGridlinesVisible",
			uiaType=UIAutomationType.Bool,
		)
