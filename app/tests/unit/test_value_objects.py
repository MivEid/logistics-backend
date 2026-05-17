"""Unit tests for Value Objects: Price, Duration, Weight."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from value_objects import Price, Duration, Weight


class TestPrice:
    def test_from_rubles_converts_to_kopecks(self):
        price = Price.from_rubles(100.0)
        assert price.kopecks == 10000

    def test_from_rubles_rounds_fractional_kopecks(self):
        price = Price.from_rubles(1.509)
        assert price.kopecks == 151

    def test_rubles_property(self):
        price = Price(kopecks=25050)
        assert price.rubles == 250.50

    def test_format_property(self):
        price = Price(kopecks=50000)
        assert "500.00" in price.format
        assert "руб" in price.format

    def test_composite_values(self):
        price = Price(kopecks=999)
        assert price.__composite_values__() == (999,)

    def test_equality(self):
        assert Price(kopecks=100) == Price(kopecks=100)
        assert Price(kopecks=100) != Price(kopecks=200)

    def test_zero_price(self):
        price = Price.from_rubles(0)
        assert price.kopecks == 0
        assert price.rubles == 0.0


class TestDuration:
    def test_from_minutes_converts_to_seconds(self):
        duration = Duration.from_minutes(30)
        assert duration.seconds == 1800

    def test_minutes_property(self):
        duration = Duration(seconds=3600)
        assert duration.minutes == 60

    def test_minutes_truncates_remainder(self):
        duration = Duration(seconds=90)
        assert duration.minutes == 1

    def test_composite_values(self):
        duration = Duration(seconds=600)
        assert duration.__composite_values__() == (600,)

    def test_equality(self):
        assert Duration(seconds=60) == Duration(seconds=60)
        assert Duration(seconds=60) != Duration(seconds=120)

    def test_zero_duration(self):
        duration = Duration.from_minutes(0)
        assert duration.seconds == 0
        assert duration.minutes == 0


class TestWeight:
    def test_from_kg_converts_to_grams(self):
        weight = Weight.from_kg(5.0)
        assert weight.grams == 5000

    def test_from_kg_fractional(self):
        weight = Weight.from_kg(0.5)
        assert weight.grams == 500

    def test_kg_property(self):
        weight = Weight(grams=2500)
        assert weight.kg == 2.5

    def test_format_property(self):
        weight = Weight(grams=1000)
        assert "1.000" in weight.format
        assert "кг" in weight.format

    def test_composite_values(self):
        weight = Weight(grams=3000)
        assert weight.__composite_values__() == (3000,)

    def test_equality(self):
        assert Weight(grams=1000) == Weight(grams=1000)
        assert Weight(grams=1000) != Weight(grams=2000)

    def test_zero_weight(self):
        weight = Weight.from_kg(0)
        assert weight.grams == 0
