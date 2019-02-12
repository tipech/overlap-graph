#!/usr/bin/env python

"""
Enumeration Query of Single Intersecting Regions and its Neighbors
by Region Intersection Graph -- NetworkX

Implements the enumeration of intersecting Regions to intersect with a
specified Region, via a Region intersection graph.

Implements the SRQEnumByNxGraph class that takes a Region intersection
graph, based on NetworkX and a specific Region within the graph. Subgraphs the
given Region intersection graph with the specified Region and its neighbors,
then enumerates all intersecting Regions (all cliques) with the generated
subgraph, and outputs only the intersecting Regions that all intersect with
the specified Region.

The construction of the Region intersection graph is performed via the one-pass
sweep-line algorithm, through a subscription to RegionSweep. The enumeration
outputs an Iterator of the intersecting Regions as tuple of Region intersection
and RegionIntns in order of the number of intersecting Regions involved.

Classes:
- SRQEnumByNxGraph
"""

from typing import Any, Callable, Iterable, Iterator, List, Union

from networkx import networkx as nx

from sources.abstract import Subscriber
from sources.core import NxGraph, Region, RegionId, RegionGrp, RegionSet

from ..enumerate import EnumerateByNxGraph, NxGraphSweepCtor, RegionIntersect
from ..mrqenum import MRQEnumByNxGraph


class SRQEnumByNxGraph(MRQEnumByNxGraph):
  """
  Enumeration Query of the intersecting Regions that all intersect with
  a specific Region by Region Intersection Graph

  Computes an Iterator of intersecting Regions that all intersect with a
  specific Region by enumerating all cliques belonging to a subgraph of the
  given Region intersection graph, where the subgraph is generated by only
  keeping the specified Region and its neighbors. The output only includes
  cliques that include the specified Region.

  Extends:
    MRQEnumByNxGraph

  Attributes:
    region:
      The specific Region that filters
      resulting intersections.
  """
  region: Region

  def __init__(self, graph: NxGraph, region: RegionId):
    """
    Initialize this computation for enumerating intersecting
    Regions within the given Region intersection graph that all
    intersect with the given specific Region.

    Args:
      graph:  The NetworkX graph representation of
              intersecting Regions.
      region: The specific Region that filters
              resulting intersections.
    """
    assert isinstance(graph, NxGraph)
    assert isinstance(region, (Region, str))

    region_id = lambda r: r.id if isinstance(r, Region) else r
    G, r = graph.G, region_id(region)

    assert r in G.nodes

    MRQEnumByNxGraph.__init__(self, graph, [r, *nx.neighbors(G, r)])
    self.region = graph.region(r)

  ### Methods: Computations

  def compute(self) -> Iterator[RegionIntersect]:
    """
    The resulting Iterator of intersecting Regions that all intersect with
    the specified Region as tuple of Region intersection and RegionIntns.

    Overrides:
      EnumerateByNxGraph.compute

    Returns:
      The resulting Iterator of intersecting Regions
      that all intersect with the specified Region as
      tuple of Region intersection and RegionIntns.
    """
    for region, intersect in EnumerateByNxGraph.compute(self):
      if self.region in intersect:
        yield (region, intersect)

  ### Class Methods: Evaluation

  @classmethod
  def prepare(cls, context: Union[RegionSet, NxGraph], region: RegionId,
                   *subscribers: Iterable[Subscriber[RegionGrp]],
                   ctor = NxGraphSweepCtor) \
                   -> Callable[[Any], Iterator[RegionIntersect]]:
    """
    Factory function for computing an Iterator of intersecting Regions that
    all intersect with a specific Region using the newly constructed or given
    Region intersection graph by one-pass sweep-line algorithm.
    Wraps NxGraphSweepCtor.prepare().

    Overrides:
      EnumerateByNxGraph.prepare

    Args:
      context:
        RegionSet:  The set of Regions to construct a new
                    Region intersection graph from.
        NxGraph:    The NetworkX graph representation of
                    intersecting Regions.
      region:       The specific Region that filters
                    resulting intersections.
      subscribers:  List of other Subscribers to observe
                    the one-pass sweep-line algorithm.
      ctor:         The Region intersection graph
                    construction algorithm.

    Returns:
      A function to evaluate the one-pass sweep-line
      algorithm to construct the Region intersecting graph
      and compute the Iterator of intersecting Regions
      that all intersect with the specified Region.

      Args:
        args, kwargs: Arguments for alg.evaluate()

      Returns:
        The resulting Iterator of intersecting
        Regions that all intersect with the
        specified Region.
    """
    assert isinstance(context, (RegionSet, NxGraph))

    def evaluate(*args, **kwargs):
      if isinstance(context, NxGraph):
        return cls(context, region).results
      else:
        fn = ctor.prepare(context, *subscribers)
        return cls(fn(*args, **kwargs), region).results

    return evaluate
