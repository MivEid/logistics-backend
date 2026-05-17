class Price:
    """Value Object: stores price in kopecks, exposes human-readable rubles."""

    def __init__(self, kopecks: int) -> None:
        self.kopecks = kopecks

    @classmethod
    def from_rubles(cls, rubles: float) -> "Price":
        return cls(round(rubles * 100))

    @property
    def rubles(self) -> float:
        return self.kopecks / 100

    @property
    def format(self) -> str:
        return f"{self.rubles:.2f} руб."

    def __composite_values__(self) -> tuple:
        return (self.kopecks,)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Price) and self.kopecks == other.kopecks

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return f"Price(kopecks={self.kopecks})"
