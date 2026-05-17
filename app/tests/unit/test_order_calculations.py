"""Unit tests for Order calculated fields."""
import sys
import os
from datetime import datetime, timezone
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from models.order import Order, OrderService, STATUS_IN_PROGRESS
from models.delivery_service import DeliveryService
from value_objects import Price, Duration


def make_service(price_kopecks: int, time_seconds: int) -> DeliveryService:
    svc = DeliveryService()
    svc.price_kopecks = price_kopecks
    svc.time_seconds = time_seconds
    svc.price = Price(price_kopecks)
    svc.duration = Duration(time_seconds)
    return svc


def make_order_service(service: DeliveryService) -> OrderService:
    os_obj = OrderService()
    os_obj.service = service
    return os_obj


def make_order(services: list[DeliveryService]) -> Order:
    order = Order()
    order.id = 1
    order.status = STATUS_IN_PROGRESS
    order.start_date = datetime.now(timezone.utc)
    order.end_date = datetime.now(timezone.utc)
    order.version = 0
    order.order_services = [make_order_service(s) for s in services]
    return order


class TestOrderCalculations:
    def test_total_price_kopecks_sum(self):
        services = [
            make_service(price_kopecks=10000, time_seconds=600),
            make_service(price_kopecks=20000, time_seconds=1200),
        ]
        order = make_order(services)
        assert order.total_price_kopecks == 30000

    def test_total_price_rubles_conversion(self):
        services = [
            make_service(price_kopecks=50000, time_seconds=600),
        ]
        order = make_order(services)
        assert order.total_price_rubles == 500.0

    def test_total_time_seconds_sum(self):
        services = [
            make_service(price_kopecks=1000, time_seconds=600),
            make_service(price_kopecks=2000, time_seconds=1200),
        ]
        order = make_order(services)
        assert order.total_time_seconds == 1800

    def test_total_time_minutes_conversion(self):
        services = [
            make_service(price_kopecks=1000, time_seconds=1800),
        ]
        order = make_order(services)
        assert order.total_time_minutes == 30

    def test_empty_order_has_zero_totals(self):
        order = make_order([])
        assert order.total_price_kopecks == 0
        assert order.total_price_rubles == 0.0
        assert order.total_time_seconds == 0
        assert order.total_time_minutes == 0

    def test_multiple_services_all_summed(self):
        services = [
            make_service(price_kopecks=100, time_seconds=60),
            make_service(price_kopecks=200, time_seconds=120),
            make_service(price_kopecks=300, time_seconds=180),
        ]
        order = make_order(services)
        assert order.total_price_kopecks == 600
        assert order.total_time_seconds == 360
        assert order.total_time_minutes == 6
