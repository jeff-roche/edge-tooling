"""Tests for transform-spikes helpers."""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from importlib import import_module

_mod = import_module("transform-spikes")
epics_look_refined = _mod.epics_look_refined
EPIC_PLANNING_STATE = _mod.EPIC_PLANNING_STATE


class TestEpicsLookRefined(unittest.TestCase):
    def test_empty_list_returns_false(self):
        assert epics_look_refined([]) is False

    def test_all_past_planning_returns_true(self):
        epics = [
            {"status": "In Progress"},
            {"status": "Closed"},
            {"status": "To Do"},
        ]
        assert epics_look_refined(epics) is True

    def test_missing_status_returns_false(self):
        epics = [{"status": "In Progress"}, {}]
        assert epics_look_refined(epics) is False

    def test_empty_status_returns_false(self):
        epics = [{"status": "In Progress"}, {"status": ""}]
        assert epics_look_refined(epics) is False

    def test_any_epic_in_planning_returns_false(self):
        epics = [
            {"status": "In Progress"},
            {"status": EPIC_PLANNING_STATE},
            {"status": "Closed"},
        ]
        assert epics_look_refined(epics) is False

    def test_feature_pre_refined_states_do_not_affect_result(self):
        """Features in New/Refinement status are irrelevant to epics_look_refined;
        only epic records matter."""
        epics = [{"status": "In Progress"}, {"status": "Closed"}]
        assert epics_look_refined(epics) is True

        epics_with_feature_like_status = [
            {"status": "New"},
            {"status": "Refinement"},
        ]
        assert epics_look_refined(epics_with_feature_like_status) is True


if __name__ == "__main__":
    unittest.main()
