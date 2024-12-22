# models.py

from dataclasses import dataclass, field
from typing import List

@dataclass
class Activity:
    level: str
    dimension: str
    sub_dimension: str
    activity: str
    description: str
    tools: List[str]
    risk: str
    measure: str
    knowledge: str
    resources: str
    time: str
    usefulness: str

@dataclass
class SubDimension:
    name: str
    activities: List[Activity] = field(default_factory=list)

@dataclass
class Dimension:
    name: str
    sub_dimensions: List[SubDimension] = field(default_factory=list)

@dataclass
class Level:
    number: str
    dimensions: List[Dimension] = field(default_factory=list)

@dataclass
class Dsomm:
    levels: List[Level] = field(default_factory=list)
