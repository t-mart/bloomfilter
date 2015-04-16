# -*- coding: utf-8 -*-

"""bloomfilter

1. ``import bloomfilter``.
2. Mark your own hash functions with ``@bloom_hash``.
3. Instantiate a ``BloomFilter``.
4. Use ``bloom_filter[key]`` to query and ``bloom_filter[key] = True`` to set.

"""
from bitarray import bitarray
from functools import update_wrapper

class BloomFilterException(Exception):
    """A problem occured creating a BloomFilter."""

class BloomFilterHashFunctionException(BloomFilterException):
    """A hash function does not meet requirements."""

def zeroed_bitarray(initial):
    """Convience function to create a zero-ed out bitarray of initial size."""
    ba = bitarray(initial)
    ba.setall(False)
    return ba

class bloom_hash:
    _BLOOM_HASH_ID = '__bloom_hash__'

    def __init__(self, func):
        """Mark func to be used when creating hashes in a BloomFilter.

        This is accomplished by setting func.__bloom_hash__ = True
        """
        self.func = func
        setattr(self, bloom_hash._BLOOM_HASH_ID, True)
        update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        try:
            return self.func(*args, **kwargs)
        except TypeError:
            raise BloomFilterHashFunctionException(
                'hash function %s must be an instance method that takes only '
                '1 additional argument (the output range)' % self.func)

    @staticmethod
    def _gather_hash_funcs(cls):
        """Return a list of valid hash functions from the attributes of cls.

        An attribute is a valid hash function when the attribute itself has
        attribute.__bloom_hash__ = True
        """
        for attr in dir(cls):
            actual_attr = getattr(cls, attr)
            if getattr(actual_attr, bloom_hash._BLOOM_HASH_ID, False):
                yield actual_attr

class BloomFilter:
    def __init__(self, bits_per_table, cls):
        """Create a Bloom Filter data structure."""
        if bits_per_table <= 0:
            raise BloomFilterException(
                'bloom filter must have a positive number of bits per '
                'underlying table')
        self.bits_per_table = bits_per_table
        self.cls = cls
        self._hash_funcs = list(bloom_hash._gather_hash_funcs(self.cls))
        if not self._hash_funcs:
            raise BloomFilterException(
                'no bloom_hash functions found in %s' % cls)
        self._tables = [zeroed_bitarray(self.bits_per_table)
            for _ in range(len(self._hash_funcs))]

    def _iter_func_and_table(self, key):
        for hash_func, table in zip(self._hash_funcs, self._tables):
            yield hash_func, table

    def __getitem__(self, key):
        """Check the BloomFilter for set membership of key.

        May return false positives. See README for discussion.
        """
        # return membership of key (may return false positives!)
        for hash_func, table in self._iter_func_and_table(key):
            index = self._get_hash(hash_func, key)
            try:
                if not table[index]:
                    return False
            except IndexError:
                raise BloomFilterHashFunctionException(
                    'hash function %s returned a value %d that can\'t be used '
                    'as an index to table (bits_per_table=%d). Ensure your '
                    'hash functions are distributing throughout the range '
                    '[0, bits_per_table].' % (hash_func.__wrapped__, index,
                                              self.bits_per_table))
        return True

    __contains__ = __getitem__

    def __setitem__(self, key, value):
        """Set key in the Bloom Filter. value is ignored."""
        for hash_func, table in self._iter_func_and_table(key):
            index = self._get_hash(hash_func, key)
            table[index] = True

    def _get_hash(self, hash_func, key):
        try:
            num = int(hash_func(key, self.bits_per_table))
        except ValueError:
            raise BloomFilterHashFunctionException(
                'hash function %s did not return an integer' %
                hash_func.__wrapped__)
        return num
