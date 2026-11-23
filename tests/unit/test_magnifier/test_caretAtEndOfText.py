# A part of NonVisual Desktop Access (NVDA)
# Copyright (C) 2026 NV Access Limited, Julien Cochuyt
# This file may be used under the terms of the GNU General Public License, version 2 or later, as modified by the NVDA license.
# For full terms and any additional permissions, see the NVDA license file: https://github.com/nvaccess/nvda/blob/master/copying.txt

"""Tests for the magnifier's location of a caret at the end of the text (#20415)."""

import unittest
from unittest.mock import Mock, PropertyMock

import textInfos
from _magnifier.utils.focusManager import FocusManager
from locationHelper import Point, RectLTRB, RectLTWH
from textInfos.offsets import OffsetsTextInfo

from ..textProvider import BasicTextInfo, BasicTextProvider

_CHAR_WIDTH = 10
_LINE_HEIGHT = 20
_RIGHT_MARGIN = 200


class _GridTextInfo(BasicTextInfo):
	"""Lays the text out on a grid; Hebrew lines start at the right margin.

	Like Firefox, there is no location at the end of the text.
	"""

	# NVDAObjectTextInfo returns the object location; use the offsets-based implementation.
	_get_boundingRects = OffsetsTextInfo._get_boundingRects

	def _getBoundingRectFromOffset(self, offset: int) -> RectLTRB:
		text = self._getStoryText()
		if offset >= len(text):
			raise LookupError
		lineStart = text.rfind("\n", 0, offset) + 1
		lineEnd = text.find("\n", offset)
		line = text[lineStart : lineEnd if lineEnd >= 0 else None]
		column = offset - lineStart
		top = text.count("\n", 0, offset) * _LINE_HEIGHT
		if any("\u0590" <= character <= "\u05ff" for character in line):
			right = _RIGHT_MARGIN - column * _CHAR_WIDTH
			return RectLTRB(right - _CHAR_WIDTH, top, right, top + _LINE_HEIGHT)
		left = column * _CHAR_WIDTH
		return RectLTRB(left, top, left + _CHAR_WIDTH, top + _LINE_HEIGHT)


class _GridTextProvider(BasicTextProvider):
	TextInfo = _GridTextInfo
	location = RectLTWH(0, 0, 1000, 1000)
	hasIrrelevantLocation = False


class TestCaretAtEndOfText(unittest.TestCase):
	"""``FocusManager._getPointAtStart`` for a caret without a location of its own."""

	def setUp(self):
		self.focusManager = FocusManager()

	def _point(self, text: str, caretOffset: int) -> Point:
		# TextInfos only keep a weak reference to their object.
		self.provider = _GridTextProvider(text=text, selection=(caretOffset, caretOffset))
		caret = self.provider.makeTextInfo(textInfos.POSITION_CARET)
		return self.focusManager._getPointAtStart(caret)

	def test_caretWithLocation_isUnchanged(self):
		self.assertEqual(self._point("abc", 1), Point(10, 0))

	def test_leftToRight_rightEdgeOfPreviousCharacter(self):
		self.assertEqual(self._point("abc", 3), Point(30, 0))

	def test_rightToLeft_leftEdgeOfPreviousCharacter(self):
		self.assertEqual(self._point("\u05d0\u05d1\u05d2", 3), Point(170, 0))

	def test_neutralAfterLeftToRight_followsTheLine(self):
		self.assertEqual(self._point("abc ", 4), Point(40, 0))

	def test_neutralAfterRightToLeft_followsTheLine(self):
		self.assertEqual(self._point("\u05d0\u05d1\u05d2 ", 4), Point(160, 0))

	def test_neutralOnly_isLeftToRight(self):
		self.assertEqual(self._point("12", 2), Point(20, 0))

	def test_afterLineBreak_startOfNextLine(self):
		self.assertEqual(self._point("ab\ncd\n", 6), Point(0, 40))

	def test_afterLineBreakInRightToLeft_startOfNextLine(self):
		self.assertEqual(self._point("\u05d0\u05d1\n", 3), Point(_RIGHT_MARGIN, 20))

	def test_emptyText_raisesOriginalError(self):
		with self.assertRaises(LookupError):
			self._point("", 0)


class TestCaretAtEndOfTextFailures(unittest.TestCase):
	"""The original error is kept when the previous character cannot locate the caret."""

	def setUp(self):
		self.focusManager = FocusManager()

	def _makeCaret(self, *, isCollapsed: bool = True, previousCharacterRects=None) -> Mock:
		caret = Mock(spec=textInfos.TextInfo)
		type(caret).pointAtStart = PropertyMock(side_effect=LookupError)
		type(caret).isCollapsed = PropertyMock(return_value=isCollapsed)
		previousCharacter = caret.copy.return_value
		previousCharacter.move.return_value = -1
		previousCharacter.text = "a"
		if isinstance(previousCharacterRects, Exception):
			type(previousCharacter).boundingRects = PropertyMock(side_effect=previousCharacterRects)
		else:
			type(previousCharacter).boundingRects = PropertyMock(return_value=previousCharacterRects or [])
		return caret

	def test_notCollapsed(self):
		caret = self._makeCaret(isCollapsed=False, previousCharacterRects=[RectLTWH(10, 20, 5, 8)])
		with self.assertRaises(LookupError):
			self.focusManager._getPointAtStart(caret)
		caret.copy.assert_not_called()

	def test_previousCharacterWithoutLocation(self):
		with self.assertRaises(LookupError):
			self.focusManager._getPointAtStart(self._makeCaret(previousCharacterRects=[]))

	def test_previousCharacterLocationFails(self):
		with self.assertRaises(LookupError):
			self.focusManager._getPointAtStart(self._makeCaret(previousCharacterRects=NotImplementedError()))
