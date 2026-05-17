"""Unit tests for Order state machine logic."""
import sys
import os
from datetime import datetime, timezone
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from models.order import (
    Order,
    STATUS_IN_PROGRESS,
    STATUS_COMPLETED,
    VALID_TRANSITIONS,
    STATUS_LABELS,
)


def make_order(status: int = STATUS_IN_PROGRESS) -> Order:
    order = Order()
    order.id = 1
    order.status = status
    order.start_date = datetime.now(timezone.utc)
    order.end_date = datetime.now(timezone.utc)
    order.version = 0
    order.order_services = []
    return order


class TestOrderStateMachine:
    def test_in_progress_can_transition_to_completed(self):
        order = make_order(STATUS_IN_PROGRESS)
        assert order.can_transition_to(STATUS_COMPLETED) is True

    def test_in_progress_cannot_transition_to_in_progress(self):
        order = make_order(STATUS_IN_PROGRESS)
        assert order.can_transition_to(STATUS_IN_PROGRESS) is False

    def test_completed_cannot_transition_to_any(self):
        order = make_order(STATUS_COMPLETED)
        assert order.can_transition_to(STATUS_IN_PROGRESS) is False
        assert order.can_transition_to(STATUS_COMPLETED) is False

    def test_is_completed_false_when_in_progress(self):
        order = make_order(STATUS_IN_PROGRESS)
        assert order.is_completed is False

    def test_is_completed_true_when_completed(self):
        order = make_order(STATUS_COMPLETED)
        assert order.is_completed is True

    def test_valid_transitions_structure(self):
        assert STATUS_IN_PROGRESS in VALID_TRANSITIONS
        assert STATUS_COMPLETED in VALID_TRANSITIONS
        assert STATUS_COMPLETED in VALID_TRANSITIONS[STATUS_IN_PROGRESS]
        assert len(VALID_TRANSITIONS[STATUS_COMPLETED]) == 0

    def test_status_labels_exist(self):
        assert STATUS_IN_PROGRESS in STATUS_LABELS
        assert STATUS_COMPLETED in STATUS_LABELS
