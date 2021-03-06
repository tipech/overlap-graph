#!/usr/bin/env python

"""
Enumeration of all Intersecting Regions by Region 
Intersection Graph -- NetworkX

Implements the EnumerateByNxGraph class that takes a Region intersection graph,
based on NetworkX, and enumerates all intersecting Regions (all cliques).
Provides the evaluate() class method that first constructs a Region
intersection graph, based on NetworkX, and enumerates all intersecting Regions
(all cliques).

The construction of the Region intersection graph is performed via the
one-pass sweep-line algorithm, through a subscription to RegionSweep.

The enumeration outputs an Iterator of the intersecting Regions as tuple of
Region intersection and RegionIntns in order of the number of intersecting
Regions involved.

Classes:
- EnumerateByNxGraph
"""

from typing import Any, Callable, Iterator, Union

from networkx import networkx as nx

from sources.algorithms import NxGraphSweepCtor
from sources.core import NxGraph, Region, RegionSet

from .common import RegionIntersect


class EnumerateByNxGraph:
  """
  Enumeration of all intersecting Regions by Region Intersection Graph

  Computes an Iterator of all of the intersecting Regions by enumerating
  all cliques belonging to a given Region intersection graph.

  Attributes:
    G:
      The NetworkX graph representation of
      intersecting Regions.
  """
  G: NxGraph

  def __init__(self, G: NxGraph):
    """
    Initialize this computation for enumerating all of the intersecting
    Regions within the given Region intersection graph.

    Args:
      G:
        The NetworkX graph representation of
        intersecting Regions.
    """
    self.G = G

  ### Properties

  @property
  def results(self) -> Iterator[RegionIntersect]:
    """
    The resulting Iterator of intersecting Regions as tuple of
    Region intersection and RegionIntns.

    Returns:
      The resulting Iterator of intersecting Regions as
      tuple of Region intersection and RegionIntns.
    """
    yield from self.compute()

  ### Methods: Computations

  def compute(self) -> Iterator[RegionIntersect]:
    """
    The resulting Iterator of intersecting Regions as tuple of
    Region intersection and RegionIntns.

    Returns:
      The resulting Iterator of intersecting Regions as
      tuple of Region intersection and RegionIntns.
    """
    graph = self.G

    for clique in nx.enumerate_all_cliques(graph.G):
      if len(clique) > 1:
        intersect = [graph.region(r) for r in clique]
        region    = Region.from_intersect(intersect, linked=True)

        assert isinstance(region, Region)
        yield (region, intersect)

  ### Class Methods: Evaluation

  @classmethod
  def prepare(cls, context: Union[RegionSet, NxGraph],
                   *args, ctor = NxGraphSweepCtor,
                   **kwargs) -> Callable[[Any], Iterator[RegionIntersect]]:
    """
    Factory function for computes an Iterator of all of the intersecting
    Regions using the construction of a Region intersection graph by
    one-pass sweep-line algorithm. Wraps NxGraphSweepCtor.evaluate().

    Args:
      context:
        RegionSet:
          The set of Regions to construct a new
          Region intersection graph from.
        NxGraph:
          The preconstructed Region intersection graph.
      ctor:
        The Region intersection graph
        construction algorithm.
      args, kwargs:
        Additional arguments for class method:
        NxGraphSweepCtor.prepare().

    Returns:
      A function to evaluate the one-pass sweep-line
      algorithm to construct the Region intersecting graph
      and compute the Iterator of all intersecting Regions.

      Args:
        args, kwargs:
          Arguments for alg.evaluate()

      Returns:
        The resulting Iterator of intersecting Regions.
    """
    assert isinstance(context, (RegionSet, NxGraph))

    if isinstance(context, NxGraph):
      fn = lambda: context
    else:
      fn = ctor.prepare(context, *args, **kwargs)      

    def evaluate(*args, **kwargs):
      return cls(fn(*args, **kwargs)).results

    return evaluate
