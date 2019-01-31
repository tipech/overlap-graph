#!/usr/bin/env python

"""
Regional Intersection Graph -- NetworkX

Implements the programming interface for representing and constructing a
NetworkX graph of intersecting or overlapping multidimensional Regions. This
data structure represents each Region as a node within the graph and
intersecting Regions between them as edges within the graph.

Note:
  Within this script, we make the distinction between
  two similar terms: 'overlap' and 'intersect'.

  overlap:
    The intersection between exactly two Regions.
  intersect:
    The intersection between two or more Regions
    It is more general. An overlap is an intersect,
    but an intersect is not an overlap.

Classes:
- NxGraph
"""

from typing import Any, Callable, Dict, Generic, Iterator, List, Tuple, TypeVar

from networkx import networkx as nx
from networkx.readwrite import json_graph

from sources.abstract.ioable import IOable
from sources.datastructs.rigraphs.rigraph import RIGraph
from sources.datastructs.shapes.region import Region, RegionPair


class NxGraph(RIGraph[nx.Graph], IOable):
  """
  Wrapper for a NetworkX graph of intersecting and overlapping Regions.
  Provides a programming interface for accessing and constructing
  the NetworkX data representation.

  Extends:
    RIGraph[nx.Graph]
    IOable
  """

  def __init__(self, dimension: int, graph: nx.Graph = None):
    """
    Initializes the NetworkX graph representation of
    intersecting and overlapping Regions.

    Args:
      dimension:
        The number of dimensions in all of the Regions
        within the graph; the dimensionality of all Regions.
      graph:
        The internal NetworkX graph representation or
        implementation for a graph of intersecting or
        overlapping Regions.
    """
    assert isinstance(dimension, int) and dimension > 0
    assert graph == None or isinstance(graph, nx.Graph)

    self.dimension = dimension

    if graph == None:
      self.G = nx.Graph(dimension=dimension)
    else:
      self.G = graph

  ### Properties: Getters

  @property
  def regions(self) -> Iterator[Tuple[str, Region]]:
    """
    Returns an Iterator of Regions within the graph
    along with the Region ID or node ID within the graph
    as a Tuple.

    Returns:
      An Iterator of Regions and their IDs.
    """
    return self.G.nodes(data='region')

  @property
  def overlaps(self) -> Iterator[Tuple[str, str, Region]]:
    """
    Returns an Iterator of overlapping Regions within the graph
    along with the two Region IDs or node IDs within the graph
    for which the two Regions are involved as a Tuple.

    Returns:
      An Iterator of overlapping Regions and
      the Region IDs of the two Regions involved.
    """
    return self.G.edges(data='intersect')

  ### Methods: Insertion

  def put_region(self, region: Region):
    """
    Add the given Region as a newly created node in the graph.

    Args:
      region:
        The Region to be added.
    """
    self.G.add_node(region.id, region=region)

  def put_overlap(self, overlap: RegionPair):
    """
    Add the given pair of Regions as a newly created edge in the graph.
    The two regions must be intersecting or overlapping.

    Args:
      overlap:
        The pair of Regions to be added
        as an intersection.
    """
    assert isinstance(overlap, Tuple) and len(overlap) == 2
    assert all([isinstance(r, Region) for r in overlap])

    a, b = overlap
    self.G.add_edge(a.id, b.id, intersect=a.intersect(b, 'reference'))

  ### Methods: Temporary Overlaps

  def put_temporary_overlap(self, overlap: RegionPair):
    """
    Add the given pair of Regions as a newly created edge in the graph.
    The two regions must be overlapping in at least one dimension.
    If two regions are has an edge between them, increment to overlap weight.

    Args:
      overlap:
        The pair of Regions to be added
        as a temporary overlap.
    """
    G = self.G

    assert isinstance(overlap, Tuple) and len(overlap) == 2
    assert all([isinstance(r, Region) for r in overlap])

    rid = lambda r: r.id
    overlap = tuple([rid(r) for r in overlap])

    if overlap in G.edges:
      edge = G.edges[overlap]
      assert 'overlaps' in edge and edge['overlaps'] < self.dimension
      edge['overlaps'] += 1
    else:
      G.add_edge(*overlap, overlaps=1, intersect=None)

  def finalize_overlap(self, overlap: Tuple[str, str]):
    """
    Update the edge associated with given pair of Region IDs in the graph,
    with the computed intersection Region between the two Regions.
    If the Regions do not overlap, remove the edge between the two Regions.

    Args:
      overlap:
        The Region IDs to finalize the edge
        into a permanent intersection or remove if
        not intersecting.
    """
    G = self.G

    assert isinstance(overlap, Tuple) and len(overlap) == 2
    assert all([isinstance(r, str) and r in G.nodes for r in overlap])
    assert overlap in G.edges; edge = G.edges[overlap]
    assert 'overlaps' in edge; overlaps = edge['overlaps']

    def intersect(a, b) -> Region:
      assert isinstance(a, Region) and isinstance(b, Region)
      ab = a.intersect(b, 'reference')
      assert isinstance(ab, Region)
      return ab

    if self.dimension == overlaps:
      a, b = tuple([G.nodes[r]['region'] for r in overlap])
      edge['intersect'] = intersect(a, b)
      del edge['overlaps']
    else:
      G.remove_edge(*overlap)

  ### Class Methods: Serialization

  @classmethod
  def to_object(cls, object: 'NxGraph', format: str = 'json', **kwargs) -> Any:
    """
    Generates an object (dict, list, or tuple) from the given NxGraph object
    that can be converted or serialized.

    Args:
      object:   The NxGraph object to be converted to an
                object (dict, list, or tuple).
      format:   The output serialization format: 'json'.
      kwargs:   Additional arguments to be used to
                customize and tweak the object generation
                process.

    kwargs:
      json_graph:
        Allowed graph formats: 'node_link' or 'adjacency'.
        If not provided, defaults to: 'node_link'.

    Returns:
      The generated object (dict, list, or tuple).

    Raises:
      ValueError: If json_graph is unsupported format.
    """
    assert isinstance(object, NxGraph) and isinstance(object.G, nx.Graph)
    assert isinstance(object.dimension, int) and object.dimension > 0

    def to_data(G, datafmt):
      method_name = f'{datafmt}_data'
      if hasattr(json_graph, method_name):
        method = getattr(json_graph, method_name)
        assert isinstance(method, Callable)
        return method(G)
      else:
        raise ValueError(f'Unsupported json_graph format.')

    datafmt = kwargs['json_graph'] if 'json_graph' in kwargs else 'node-link'
    data = {
      'dimension': object.dimension,
      'json_graph': datafmt,
      'graph': to_data(object.G, datafmt)
    }

    return data

  ### Class Methods: Deserialization

  @classmethod
  def from_object(cls, object: Any, **kwargs) -> 'NxGraph':
    """
    Construct a new NxGraph object from the conversion of the given object.

    Args:
      object:   The object (dict, list, or tuple)
                to be converted into an NxGraph object.
      kwargs:   Additional arguments for customizing
                and tweaking the NxGraph object
                generation process.

    kwargs:
      json_graph:
        Allowed graph formats: 'node_link' or 'adjacency'.
        If not provided, defaults to: 'node_link'.

    Returns:
      The newly constructed NxGraph object.

    Raises:
      ValueError: If json_graph is unsupported format.
    """
    types = { 'graph': Dict, 'json_graph': str, 'dimension': int }

    assert isinstance(object, Dict)
    assert all([k in object and isinstance(object[k], t) for k, t in types.items()])
    assert object['dimension'] > 0

    def to_graph(data: Dict, datafmt: str) -> nx.Graph:
      method_name = f'{datafmt}_graph'
      if hasattr(json_graph, method_name):
        method = getattr(json_graph, method_name)
        assert isinstance(method, Callable)
        return method(data)
      else:
        raise ValueError(f'Unsupported json_graph format.')

    def to_regions(G: nx.Graph, regions: List[str], edge: Tuple[str, str]) -> List[Region]:
      assert isinstance(regions, List) and len(regions) >= 2
      assert all([isinstance(r, str) for r in regions])
      assert all([r in regions for r in edge])
      assert all([r in G.node for r in regions])

      return list(map(lambda r: G.node[r]['region'], regions))

    nxgraph = NxGraph(object['dimension'])
    nxgraph.G = to_graph(object['graph'], object['json_graph'])
    G = nxgraph.G

    assert nxgraph.dimension == G.graph['dimension']

    # Rematerialize Regions
    for node, region_data in G.nodes(data='region'):
      region = Region.from_object(region_data)
      assert region.dimension == nxgraph.dimension
      G.node[node]['region'] = region

    # Resolve backlinks amongst the edge, Region intersections
    for (u, v, region_data) in G.edges(data='intersect'):
      region = Region.from_object(region_data)
      assert region.dimension == nxgraph.dimension

      if 'intersect' in region:
        region['intersect'] = to_regions(G, region['intersect'], (u, v))
      if 'union' in region:
        region['union'] = to_regions(G, region['union'], (u, v))

      G.edges[u, v]['intersect'] = region

    return nxgraph
