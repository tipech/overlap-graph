#!/usr/bin/env python

"""
Random Number Generators

Implements the Randoms class, a static class that provides factory methods
that each return Callable (lambdas) that are preconfigured to generate random
values based on a particular distribution or random number generation
function. The only missing parameters is the lower and upper bounds of the
values generated and the sample size of the output.

Types:
- ShapeSize
- NDArray
- RandomFn

Classes:
- Randoms
"""

from typing import Callable, Dict, List, Union

from numpy import ndarray, mean, random


ShapeSize = Union[None, int, List[int]]
NDArray   = ndarray
RandomFn  = Callable[[ShapeSize, float, float], NDArray]


class Randoms:
  """
  Static class that provides factory methods that each return Callable
  (lambdas) that are preconfigured to generate random values based on a
  particular distribution or random number generation function. The only
  missing parameters is the lower and upper bounds of the values generated
  and the sample size of the output.
  """

  @classmethod
  def get(cls, name: str, **kwargs) -> RandomFn:
    """
    Returns a function that draws samples from the specified distribution or
    random number generation function that corresponds with the given method
    name. Passes the given arguments as parameter for that factory method.

    Args:
      name:
        The name of random number generator for
        factory method that generated random
        number generators.
      kwargs:
        arguments as parameter for that factory method.

    Returns:
      The factory method that generated random
      number generators.

      Args:
        size:
          The number of random values to be generated.
        lower:
          The lower bounding value of the range from
          which random values are to be generated.
        upper:
          The upper bounding value of the range from
          which random values are to be generated.

      Returns:
        The randomly generated values.
    """
    return getattr(cls, name)(**kwargs)

  @classmethod
  def list(cls) -> List[str]:
    """
    Returns the list of available random number
    generators (distributions).

    Returns:
      The list of available random number
      generators (distributions).
    """
    excluded = ['get', 'list']
    israndng = lambda f: all([callable(getattr(cls, f)), f not in excluded,
                              not f.startswith('_')])

    return [f for f in dir(cls) if israndng(f)]

  ### Class Methods: Random Number Generators

  @classmethod
  def uniform(cls) -> RandomFn:
    """
    Returns a function that draws samples from a uniform distribution.
    Samples are uniformly distributed over the half-open interval [low, high)
    (includes low, but excludes high). In other words, any value within the
    given interval is equally likely to be drawn by uniform.

    Returns:
      A factory function that draws samples
      from a uniform distribution.
    """
    def uniform_rng(size: int = 1, lower: float = 0, upper: float = 1):
      return random.uniform(lower, upper, size)

    return uniform_rng

  @classmethod
  def triangular(cls, mode: float = 0.5) -> RandomFn:
    """
    Returns a function that draws samples from the triangular distribution
    over the interval [left, right]. The triangular distribution is a
    continuous probability distribution with lower limit left, peak at mode,
    and upper limit right. Unlike the other distributions, these parameters
    directly define the shape of the probability distribution function (pdf).

    Args:
      mode:
        The peak value of the triangular
        distribution as a percentage of the
        total length.

    Returns:
      A factory function that draws samples
      from a triangular distribution.
    """
    def triangular_rng(size: int = 1, left: float = 0, right: float = 1):
      return random.triangular(left, (right - left)*mode + left, right, size)

    return triangular_rng
