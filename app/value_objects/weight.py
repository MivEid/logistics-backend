class Weight:
    """Value Object: stores weight in grams, exposes human-readable kilograms."""

    def __init__(self, grams: int) -> None:
        self.grams = grams

    @classmethod
    def from_kg(cls, kg: float) -> "Weight":
        return cls(round(kg * 1000))

    @property
    def kg(self) -> float:
        return self.grams / 1000

    @property
    def format(self) -> str:
        return f"{self.kg:.3f} кг"

    def __composite_values__(self) -> tuple:
        return (self.grams,)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Weight) and self.grams == other.grams

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return f"Weight(grams={self.grams})"
