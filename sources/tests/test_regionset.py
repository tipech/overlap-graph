#!/usr/bin/env python

#
# tests/test_regionset.py - Unit tests for datastructs/regionet.py
#
# This script implements the following tests:
#   - test_create_regionset
#   - test_regionset_dimension_mismatch
#   - test_regionset_outofbounds
#   - test_regionset_from_random
#   - test_regionset_to_json
#

from io import StringIO
from typing import List, Iterable
from unittest import TestCase
from ..datastructs.regionset import RegionSet
from ..datastructs.region import Region

class TestRegionSet(TestCase):

  def _test_regionset(self, regionset: RegionSet, nregions: int, bounds: Region, regions: Iterable[Region]):
    #print(f'{regionset}')
    self.assertEqual(regionset.size, nregions)
    self.assertTrue(bounds.encloses(regionset.minbounds))
    for i, region in enumerate(regions):
      #print(f'{region}')
      self.assertEqual(region, regionset[i])
      self.assertEqual(region, regionset[region.id])
      self.assertTrue(region in regionset)
      self.assertTrue(region.id in regionset)
      self.assertTrue(bounds.encloses(region))

  def test_create_regionset(self):
    bounds = Region([0, 0], [100, 100])
    regionset = RegionSet(bounds = bounds)
    regions = bounds.random_regions(10)
    for region in regions:
      regionset.add(region)
    self._test_regionset(regionset, len(regions), bounds, regions)

  def test_regionset_dimension_mismatch(self):
    regionset = RegionSet(dimension = 2)
    with self.assertRaises(AssertionError):
      regionset.add(Region([0]*3,[1]*3))

  def test_regionset_outofbounds(self):
    regionset = RegionSet(bounds = Region([0, 0], [10, 10]))
    with self.assertRaises(AssertionError):
      regionset.add(Region([-1, -1],[5, 5]))

  def test_regionset_from_random(self):
    nregions = 50
    bounds = Region([0]*2, [10]*2)
    sizepc_range = Region([0]*2, [0.5]*2)
    regionset = RegionSet.from_random(nregions, bounds, sizepc_range = sizepc_range, precision = 1)
    self._test_regionset(regionset, nregions, bounds, regionset)

  def test_regionset_tofrom_json(self):
    nregions = 10
    bounds = Region([0]*2, [100]*2)
    sizepc_range = Region([0]*2, [0.5]*2)
    regionset = RegionSet.from_random(nregions, bounds, sizepc_range = sizepc_range, precision = 1)

    with StringIO() as output:
      regionset.to_json(output, compact = True)
      before = output.getvalue()
      #print(before)
      output.seek(0)
      newregionset = RegionSet.from_json(output)
      self._test_regionset(newregionset, nregions, bounds, regionset)

      output.truncate(0)
      output.seek(0)
      newregionset.to_json(output, compact = True)
      after = output.getvalue()
      #print(after)
      self.assertEqual(before, after)