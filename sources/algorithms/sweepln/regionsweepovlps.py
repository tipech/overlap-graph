#!/usr/bin/env python

"""
Compute Region Pairwise Overlaps by One-pass Sweep-line Algorithm

Implements the RegionSweepOverlaps class that computes a list of all of the
pairwise overlapping Regions using the one-pass sweep-line algorithm, through
a subscription to RegionSweep.

Classes:
- RegionSweepOverlaps
"""

from typing import Any, Callable, Iterable, List, Tuple

from sources.abstract import Event, Subscriber
from sources.core import \
     Region, RegionEvent, RegionGrp, RegionPair, RegionSet

from .basesweep import SweepTaskRunner
from .regionsweep import RegionSweep, RegionSweepEvtKind


class RegionSweepOverlaps(SweepTaskRunner[RegionGrp, List[RegionPair]]):
  """
  Computes a list of all of the pairwise overlapping Regions
  using the one-pass sweep-line algorithm, through a subscription
  to RegionSweep.

  Extends:
    SweepTaskRunner[RegionGrp, List[RegionPair]]

  Attributes:
    overlaps:
      The List of pairwise overlapping Regions.
  """
  overlaps: List[RegionPair]

  def __init__(self):
    """
    Initialize this class to compute a list of all of the pairwise
    overlapping Regions using the one-pass sweep-line algorithm.
    Sets the events as RegionSweepEvtKind.
    """
    Subscriber.__init__(self, RegionSweepEvtKind)

    self.overlaps = None

  ### Properties

  @property
  def results(self) -> List[RegionPair]:
    """
    The resulting List of pairwise overlapping Regions.
    Alias for: self.overlaps

    Returns:
      The resulting List of pairwise
      overlapping Regions.
    """
    return self.overlaps

  ### Methods: Event Handlers

  def on_init(self, event: RegionEvent):
    """
    Handle Event when sweep-line algorithm initializes.

    Args:
      event:
        The initialization Event.
    """
    assert event.kind == RegionSweepEvtKind.Init

    self.overlaps = []

  def on_intersect(self, event: Event[RegionPair]):
    """
    Handle Event when sweep-line algorithm encounters
    the two or more Regions intersecting.

    Args:
      event:
        The intersecting Regions Event.
    """
    assert event.kind == RegionSweepEvtKind.Intersect
    assert isinstance(event.context, Tuple) and len(event.context) == 2
    assert all([isinstance(r, Region) for r in event.context])

    self.overlaps.append(event.context)

  ### Class Methods: Evaluation

  @classmethod
  def prepare(cls, regions: RegionSet,
                   *subscribers: Iterable[Subscriber[RegionGrp]]) \
                   -> Callable[[Any], List[RegionPair]]:
    """
    Factory function for computes a list of all of the pairwise overlapping
    Regions using the one-pass sweep-line algorithm.

    Overrides:
      SweepTaskRunner.prepare

    Args:
      regions:
        The set of Regions to compute the list of
        the pairwise overlapping Regions from.
      subscribers:
        The other Subscribers to observe the
        one-pass sweep-line algorithm.

    Returns:
      A function to evaluate the one-pass sweep-line
      algorithm and compute the list of the pairwise
      overlapping Regions.

      Args:
        args, kwargs:
          Arguments for alg.evaluate()

      Returns:
        The resulting List of pairwise
        overlapping Regions.
    """
    assert isinstance(regions, RegionSet)
    return SweepTaskRunner.prepare(cls, RegionSweep, **{
      'subscribers': subscribers,
      'alg_args': [regions]
    })
