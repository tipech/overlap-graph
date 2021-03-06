#!/usr/bin/env python

"""
Enumeration Query of Single Intersecting Regions with Cyclic
Multi-pass Sweep-line Algorithm

Implements the SRQEnumByRCSweep class that performs the enumeration of
intersecting Regions within a RegionSet that all intersect with a specified
Region via a subscription to RegionCycleSweep.

The enumeration outputs an Iterator of the restricted intersecting Regions as
tuple of Region intersection and RegionIntns in order of the number of
intersecting Regions and the position of the last intersecting Region's
Begin Event.

Classes:
- SRQEnumByRCSweep
"""

from typing import Any, Callable, Iterable, Iterator, List, Union

from sources.abstract import Subscriber
from sources.algorithms import RestrictedRegionCycleSweep, SweepTaskRunner
from sources.core import Region, RegionGrp, RegionId, RegionSet

from ..enumerate import EnumerateByRCSweep, RegionIntersect


class SRQEnumByRCSweep(EnumerateByRCSweep):
  """
  Enumeration of intersecting Regions all intersecting with specific Region by
  Cyclic Multi-pass Sweep-line Algorithm. Computes an Iterator of intersecting
  Regions that all intersect with a specified Region, using the cyclic
  multi-pass sweep-line algorithm, through a subscription to
  RestrictedRegionCycleSweep.

  Extends:
    EnumerateByRCSweep

  Attributes:
    region:
      The specific Region that filters
      resulting intersections.
  """
  region: Region

  def __init__(self, region: Region):
    """
    Initialize this class to compute a list of the intersecting Regions
    that all intersect with the given Region using the cyclic multi-pass
    sweep-line algorithm.

    Args:
      region:
        The specific Region that filters
        resulting intersections.
    """
    assert isinstance(region, Region)

    EnumerateByRCSweep.__init__(self)
    self.region = region

  ### Methods: Computations

  def compute(self) -> Iterator[RegionIntersect]:
    """
    The resulting Iterator of intersecting Regions that all intersect with
    the specified Region as tuple of Region intersection and RegionIntns.

    Returns:
      The resulting Iterator of intersecting Regions
      that all intersect with the specified Region as
      tuple of Region intersection and RegionIntns.
    """
    for region, intersect in self.intersects:
      if self.region in intersect:
        yield (region, intersect)

  ### Class Methods: Evaluation

  @classmethod
  def prepare(cls, regions: RegionSet, region: RegionId,
                   *subscribers: Iterable[Subscriber[RegionGrp]]) \
                   -> Callable[[Any], Iterator[RegionIntersect]]:
    """
    Factory function for computing an Iterator of intersecting Regions
    that all intersect with the given Region via the restricted cyclic
    multi-pass sweep-line algorithm.

    Overrides:
      EnumerateByRCSweep.prepare

    Args:
      regions:      The set of Regions to compute the
                    Iterator of intersecting Regions from.
      region:       The specific Region that filters
                    resulting intersections.
      subscribers:  The other Subscribers to observe the
                    cyclic multi-pass sweep-line algorithm.

    Returns:
      A function to evaluate the cyclic multi-pass
      sweep-line algorithm to compute the Iterator of
      intersecting Regions that all intersect with
      the specified Region.

      Args:
        args, kwargs: Arguments for alg.evaluate()

      Returns:
        The resulting Iterator of subsetted
        intersecting Regions.
    """
    assert isinstance(regions, RegionSet)
    assert isinstance(region, (Region, str)) and region in regions

    if isinstance(region, str):
      region = regions[region]

    return SweepTaskRunner.prepare(cls, RestrictedRegionCycleSweep, **{
      'subscribers': subscribers,
      'alg_args': [regions],
      'alg_kw': {'region': region},
      'task_args': [region]
    })
