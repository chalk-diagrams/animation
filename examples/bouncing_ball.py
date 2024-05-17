
class GetPosition:
    v: float
    y = 0.0
    g = 9.81
    ρ = 0.75

    def __post_init__(self):
        assert self.v > 0

    def __call__(self, t):
        assert t >= 0
        # if self.y <= 0:
        #     self.v = self.ρ * self.v
        return self.v * t - self.g * t ** 2 / 2
