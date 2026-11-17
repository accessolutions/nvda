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


def _makeCaretAtEnd(
	*,
	isCollapsed: bool = True,
	moved: int = -1,
	previousCharacterRects: list[RectLTWH] | Exception | None = None,
) -> Mock:
	"""A non-offset TextInfo whose ``pointAtStart`` fails, as Firefox's at the end of the text."""
	caret = Mock(spec=textInfos.TextInfo)
	type(caret).pointAtStart = PropertyMock(side_effect=LookupError)
	type(caret).isCollapsed = PropertyMock(return_value=isCollapsed)
	previousCharacter = caret.copy.return_value
	previousCharacter.move.return_value = moved
	if isinstance(previousCharacterRects, Exception):
		type(previousCharacter).boundingRects = PropertyMock(side_effect=previousCharacterRects)
	else:
		type(previousCharacter).boundingRects = PropertyMock(
			return_value=previousCharacterRects if previousCharacterRects is not None else [],
		)
	return caret


class TestCaretAtEndOfText(unittest.TestCase):
	"""``FocusManager._getPointAtStart`` when the TextInfo has no location of its own."""

	def setUp(self):
		self.focusManager = FocusManager()

	def test_pointAvailable_isReturned(self):
		caret = Mock(spec=textInfos.TextInfo)
		type(caret).pointAtStart = PropertyMock(return_value=Point(1, 2))
		self.assertEqual(self.focusManager._getPointAtStart(caret), Point(1, 2))
		caret.copy.assert_not_called()

	def test_compoundCaretAtEnd_usesPreviousCharacterRightEdge(self):
		caret = _makeCaretAtEnd(previousCharacterRects=[RectLTWH(10, 20, 5, 8)])
		self.assertEqual(self.focusManager._getPointAtStart(caret), Point(15, 20))
		previousCharacter = caret.copy.return_value
		previousCharacter.move.assert_called_once_with(textInfos.UNIT_CHARACTER, -1)
		previousCharacter.expand.assert_called_once_with(textInfos.UNIT_CHARACTER)

	def test_previousCharacterOnSeveralRects_usesLast(self):
		caret = _makeCaretAtEnd(previousCharacterRects=[RectLTWH(0, 0, 1, 1), RectLTWH(30, 40, 6, 8)])
		self.assertEqual(self.focusManager._getPointAtStart(caret), Point(36, 40))

	def test_notCollapsed_raisesOriginalError(self):
		caret = _makeCaretAtEnd(isCollapsed=False, previousCharacterRects=[RectLTWH(10, 20, 5, 8)])
		with self.assertRaises(LookupError):
			self.focusManager._getPointAtStart(caret)
		caret.copy.assert_not_called()

	def test_startOfText_raisesOriginalError(self):
		caret = _makeCaretAtEnd(moved=0, previousCharacterRects=[RectLTWH(10, 20, 5, 8)])
		with self.assertRaises(LookupError):
			self.focusManager._getPointAtStart(caret)

	def test_previousCharacterWithoutLocation_raisesOriginalError(self):
		caret = _makeCaretAtEnd(previousCharacterRects=[])
		with self.assertRaises(LookupError):
			self.focusManager._getPointAtStart(caret)

	def test_previousCharacterLocationFails_raisesOriginalError(self):
		caret = _makeCaretAtEnd(previousCharacterRects=NotImplementedError())
		with self.assertRaises(LookupError):
			self.focusManager._getPointAtStart(caret)

	def test_offsetsCaretAtEnd_stillUsesOffsets(self):
		caret = Mock(spec=OffsetsTextInfo, isCollapsed=True, _startOffset=5)
		type(caret).pointAtStart = PropertyMock(side_effect=LookupError)
		caret._getBoundingRectFromOffset.return_value = RectLTRB(10, 20, 30, 40)
		self.assertEqual(self.focusManager._getPointAtStart(caret), Point(30, 20))
		caret._getBoundingRectFromOffset.assert_called_once_with(4)
		caret.copy.assert_not_called()

	def test_offsetsCaretAtEndWithoutLocation_raisesOriginalError(self):
		caret = Mock(spec=OffsetsTextInfo, isCollapsed=True, _startOffset=5)
		type(caret).pointAtStart = PropertyMock(side_effect=LookupError)
		caret._getBoundingRectFromOffset.side_effect = LookupError
		caret._getPointFromOffset.side_effect = NotImplementedError
		with self.assertRaises(LookupError):
			self.focusManager._getPointAtStart(caret)
		caret.copy.assert_not_called()
