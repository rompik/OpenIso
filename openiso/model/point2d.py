# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""
2D point representation for Skey Library
"""
from dataclasses import dataclass

@dataclass
class Point2D:
    x: float = 0.0
    y: float = 0.0

    def to_tuple(self) -> tuple:
        return (self.x, self.y)

    @classmethod
    def from_tuple(cls, t: tuple) -> 'Point2D':
        return cls(x=t[0], y=t[1])
