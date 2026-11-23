# A part of NonVisual Desktop Access (NVDA)
# Copyright (C) 2026 NV Access Limited, Julien Cochuyt
# This file may be used under the terms of the GNU General Public License, version 2 or later, as modified by the NVDA license.
# For full terms and any additional permissions, see the NVDA license file: https://github.com/nvaccess/nvda/blob/master/copying.txt

"""Tests for reporting prolonged magnifier tracking failures."""

import unittest
from unittest.mock import MagicMock, Mock, patch

from _magnifier.magnifier import Magnifier
from _magnifier.utils.focusManager import FocusManager
from _magnifier.utils.types import Coordinates, MagnifierTrackingType
from exceptions import LocationUnavailableError

from tests.unit.test_magnifier.test_magnifier import _TestMagnifier

_DELAY = Magnifier._TRACKING_FAILURE_REPORT_DELAY_SEC


class TestFailedSources(unittest.TestCase):
	"""The focus manager records which sources had to fall back during an update."""

	def setUp(self) -> None:
		self.focusManager = FocusManager()

	def testReviewFailure(self) -> None:
		with patch(
			"_magnifier.utils.focusManager.api.getReviewPosition",
			side_effect=LocationUnavailableError(),
		):
			self.focusManager._getReviewPosition()
		self.assertEqual(self.focusManager.getFailedSources(), {MagnifierTrackingType.REVIEW})

	def testNavigatorObjectFailure(self) -> None:
		with patch(
			"_magnifier.utils.focusManager.api.getNavigatorObject",
			side_effect=RuntimeError(),
		):
			self.focusManager._getNavigatorObjectPosition()
		self.assertEqual(self.focusManager.getFailedSources(), {MagnifierTrackingType.NAVIGATOR_OBJECT})

	def testCaretFailureWithFocusLocationIsNotAFailure(self) -> None:
		focusObject = Mock(location=(100, 150, 200, 300))
		with (
			patch("_magnifier.utils.focusManager.api.getFocusObject", return_value=focusObject),
			patch("_magnifier.utils.focusManager.api.getCaretPosition", side_effect=RuntimeError()),
		):
			self.assertEqual(self.focusManager._getSystemFocusPosition(), Coordinates(100, 150))
		self.assertEqual(self.focusManager.getFailedSources(), frozenset())

	def testCaretAndFocusLocationFailure(self) -> None:
		focusObject = Mock(location=None)
		with (
			patch("_magnifier.utils.focusManager.api.getFocusObject", return_value=focusObject),
			patch("_magnifier.utils.focusManager.api.getCaretPosition", side_effect=RuntimeError()),
		):
			self.focusManager._getSystemFocusPosition()
		self.assertEqual(self.focusManager.getFailedSources(), {MagnifierTrackingType.SYSTEM_FOCUS})

	def testFailedSourcesAreClearedOnEachUpdate(self) -> None:
		self.focusManager._failedSources.add(MagnifierTrackingType.REVIEW)
		self.focusManager._getMousePosition = MagicMock(return_value=Coordinates(0, 0))
		self.focusManager._getSystemFocusPosition = MagicMock(return_value=Coordinates(0, 0))
		self.focusManager._getReviewPosition = MagicMock(return_value=None)
		self.focusManager._getNavigatorObjectPosition = MagicMock(return_value=Coordinates(0, 0))
		with (
			patch("_magnifier.utils.focusManager.getFollowState", return_value=True),
			patch("_magnifier.utils.focusManager.winUser.getAsyncKeyState", return_value=0),
		):
			self.focusManager.getCurrentFocusCoordinates()
		self.assertEqual(self.focusManager.getFailedSources(), frozenset())


class TestTrackingFailureReport(_TestMagnifier):
	"""The magnifier announces once when the followed source stays unavailable."""

	def setUp(self) -> None:
		super().setUp()
		self.magnifier._isActive = True
		self.magnifier._doUpdate = MagicMock()
		self.magnifier._startTimer = MagicMock()
		self.followed = MagnifierTrackingType.SYSTEM_FOCUS
		self.failedSources: set[MagnifierTrackingType] = set()
		self.magnifier._focusManager.getLastFocusType = MagicMock(side_effect=lambda: self.followed)
		self.magnifier._focusManager.getFailedSources = MagicMock(
			side_effect=lambda: frozenset(self.failedSources),
		)
		self.now = 100.0
		timePatcher = patch("_magnifier.magnifier.time")
		mockTime = timePatcher.start()
		self.addCleanup(timePatcher.stop)
		mockTime.monotonic.side_effect = lambda: self.now
		messagePatcher = patch("_magnifier.magnifier.ui.message")
		self.mockMessage = messagePatcher.start()
		self.addCleanup(messagePatcher.stop)

	def _updateAfter(self, seconds: float) -> None:
		self.now += seconds
		self.magnifier._updateMagnifier()

	def testShortFailureIsSilent(self) -> None:
		self.failedSources = {self.followed}
		self._updateAfter(0)
		self._updateAfter(_DELAY / 2)
		self.mockMessage.assert_not_called()

	def testProlongedFailureIsAnnouncedOnce(self) -> None:
		self.failedSources = {self.followed}
		self._updateAfter(0)
		self._updateAfter(_DELAY)
		self.mockMessage.assert_called_once()
		for _ in range(10):
			self._updateAfter(_DELAY)
		self.mockMessage.assert_called_once()

	def testFailureAfterSuccessIsAnnouncedAgain(self) -> None:
		self.failedSources = {self.followed}
		self._updateAfter(0)
		self._updateAfter(_DELAY)
		self.failedSources = set()
		self._updateAfter(0.1)
		self.failedSources = {self.followed}
		self._updateAfter(0.1)
		self.assertEqual(self.mockMessage.call_count, 1)
		self._updateAfter(_DELAY)
		self.assertEqual(self.mockMessage.call_count, 2)

	def testUnfollowedSourceFailureIsSilent(self) -> None:
		self.failedSources = {MagnifierTrackingType.REVIEW, MagnifierTrackingType.NAVIGATOR_OBJECT}
		self._updateAfter(0)
		self._updateAfter(_DELAY * 2)
		self.mockMessage.assert_not_called()

	def testNoFollowedSourceIsSilent(self) -> None:
		self.followed = None
		self.failedSources = {MagnifierTrackingType.SYSTEM_FOCUS}
		self._updateAfter(0)
		self._updateAfter(_DELAY * 2)
		self.mockMessage.assert_not_called()

	def testUnexpectedTrackingErrorCountsAsFailure(self) -> None:
		self.magnifier._focusManager.getCurrentFocusCoordinates = MagicMock(side_effect=ValueError())
		with patch("_magnifier.magnifier.log"):
			self._updateAfter(0)
			self._updateAfter(_DELAY)
		self.mockMessage.assert_called_once()

	def testUnavailableLocationCountsAsFailure(self) -> None:
		self.magnifier._focusManager.getCurrentFocusCoordinates = MagicMock(
			side_effect=LocationUnavailableError(),
		)
		self._updateAfter(0)
		self._updateAfter(_DELAY)
		self.mockMessage.assert_called_once()

	def testRestartResetsTheFailureClock(self) -> None:
		self.failedSources = {self.followed}
		self._updateAfter(0)
		self.magnifier._isActive = False
		self.magnifier._startMagnifier()
		self._updateAfter(_DELAY / 2)
		self.mockMessage.assert_not_called()
