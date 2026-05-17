class Duration:
    """Value Object: stores duration in seconds, exposes human-readable minutes."""

    def __init__(self, seconds: int) -> None:
        self.seconds = seconds

    @classmethod
    def from_minutes(cls, minutes: int) -> "Duration":
        return cls(minutes * 60)

    @property
    def minutes(self) -> int:
        return self.seconds // 60

    def __composite_values__(self) -> tuple:
        return (self.seconds,)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Duration) and self.seconds == other.seconds

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return f"Duration(seconds={self.seconds})"
