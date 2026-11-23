# A part of NonVisual Desktop Access (NVDA)
# Copyright (C) 2026 NV Access Limited, Julien Cochuyt
# This file may be used under the terms of the GNU General Public License, version 2 or later, as modified by the NVDA license.
# For full terms and any additional permissions, see the NVDA license file: https://github.com/nvaccess/nvda/blob/master/copying.txt

"""Tests for ending the full-screen magnifier's screen overview with a second press of its command."""

from unittest.mock import MagicMock, patch

from _magnifier import commands

from .test_screenOverview import _TestScreenOverview


class TestEndScreenOverview(_TestScreenOverview):
	def _assertEndedNormally(self) -> None:
		self.assertFalse(self.spotlight._spotlightIsActive)
		self.assertFalse(self.spotlight._isZoomingBack)
		self.assertEqual(self.fullscreen.zoomLevel, 300)
		self.mockUiMessage.assert_called_once()
		self.assertTrue(self.fullscreen._timer.IsRunning())

	def test_endDuringZoomOut_zoomsBackFromTheCurrentLevel(self):
		stepTimer = self._startDuringAnimation()
		levelWhenEnded = self.spotlight._currentZoomLevel
		self.spotlight.end()
		stepTimer.Stop.assert_called_once()
		self.assertTrue(self.spotlight._isZoomingBack)
		# The first zoom-back step runs at once, from where the zoom-out stopped, towards 300.
		self.assertGreater(self.spotlight._currentZoomLevel, levelWhenEnded)
		self.mockUiMessage.assert_not_called()
		self._runPendingSteps()
		self._assertEndedNormally()

	def test_endDuringHold_stopsMouseMonitoringAndZoomsBack(self):
		idleTimer = self._startDuringHold()
		self.spotlight.end()
		idleTimer.Stop.assert_called_once()
		self._runPendingSteps()
		self._assertEndedNormally()

	def test_endDuringZoomBack_isIgnored(self):
		self._startDuringHold()
		self.spotlight.zoomBack()
		stepTimer = self.mockCallLater.return_value
		callCount = self.mockCallLater.call_count
		self.spotlight.end()
		stepTimer.Stop.assert_not_called()
		self.assertEqual(self.mockCallLater.call_count, callCount)
		self._runPendingSteps()
		self._assertEndedNormally()

	def test_end_whenInactive_changesNothing(self):
		self.fullscreen._setZoomRawValue(250)
		self.spotlight.end()
		self.assertEqual(self.fullscreen.zoomLevel, 250)
		self.mockCallLater.assert_not_called()
		self.mockUiMessage.assert_not_called()

	def test_afterEnd_theOverviewCanStartAgain(self):
		self._startDuringHold()
		self.spotlight.end()
		self._runPendingSteps()
		self._startDuringAnimation()
		self.assertFalse(self.spotlight._isZoomingBack)


class TestScreenOverviewCommand(_TestScreenOverview):
	def setUp(self):
		super().setUp()
		patcher = patch.object(commands, "getMagnifier", return_value=self.fullscreen)
		patcher.start()
		self.addCleanup(patcher.stop)
		patcher = patch.object(commands.ui, "message")
		self.mockCommandMessage = patcher.start()
		self.addCleanup(patcher.stop)

	def test_secondPress_endsTheOverviewSilently(self):
		self._startDuringHold()
		self.spotlight.end = MagicMock()
		commands.startSpotlight()
		self.spotlight.end.assert_called_once_with()
		self.mockCommandMessage.assert_not_called()

	def test_firstPress_startsTheOverview(self):
		commands.startSpotlight()
		self.assertTrue(self.spotlight._spotlightIsActive)
		self.mockCommandMessage.assert_called_once()
