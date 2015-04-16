# -*- coding: utf-8 -*-

"""
bloomfilter

A probabalistic, space-efficient set membership data structure.

"""
__author__ = 'Tim Martin'
__version__ = '0.0.1'
__license__ = 'MIT'

from .bloomfilter import BloomFilter, bloom_hash, BloomFilterException, \
    BloomFilterHashFunctionException

__all__ = ['BloomFilter', 'bloom_hash', 'BloomFilterException',
    'BloomFilterHashFunctionException']
