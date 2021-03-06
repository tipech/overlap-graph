#!/usr/bin/env python

"""
Enumeration of Region Intersections

Enumerates an Iterator of the intersecting Regions as tuple of Region
intersection and RegionIntns in order of the number of intersecting Regions.

Types:
- RegionIntersect
- EnumerateRegionIntersect
"""

from typing import Iterator, Tuple

from sources.algorithms import SweepTaskRunner
from sources.core import Region, RegionGrp, RegionIntxn

RegionIntersect = Tuple[Region, RegionIntxn]
EnumerateRegionIntersect = SweepTaskRunner[RegionGrp, Iterator[RegionIntersect]]
