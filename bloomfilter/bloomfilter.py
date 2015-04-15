from bitarray import bitarray
from functools import update_wrapper

class BloomFilterException(Exception):
    pass

class BloomFilterHashFunctionException(BloomFilterException):
    pass

def zeroed_bitarray(initial):
    ba = bitarray(initial)
    ba.setall(False)
    return ba

class bloom_hash:
    _BLOOM_HASH_ID = '__bloom_hash__'

    def __init__(self, func):
        self.func = func
        setattr(self, bloom_hash._BLOOM_HASH_ID, True)
        update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        try:
            return self.func(*args, **kwargs)
        except TypeError:
            raise BloomFilterHashFunctionException(
                'hash function %s must be an instance method that takes no '
                'additional arguments' % self.func)

    @staticmethod
    def _gather_hash_funcs(obj):
        for attr in dir(obj):
            actual_attr = getattr(obj, attr)
            if getattr(actual_attr, bloom_hash._BLOOM_HASH_ID, False):
                yield actual_attr

class BloomFilter:
    def __init__(self, bits_per_table, cls):
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
        # return membership of key (may return false positives!)
        for hash_func, table in self._iter_func_and_table(key):
            index = self._scale_hash_to_table(hash_func, key)
            if not table[index]:
                return False
        return True

    def __setitem__(self, key, value):
        # value doesn't matter here! we're just providing a dict-like interface
        # bloom filters simply record membership
        for hash_func, table in self._iter_func_and_table(key):
            index = self._scale_hash_to_table(hash_func, key)
            table[index] = True

    def _scale_hash_to_table(self, hash_func, key):
        try:
            num = int(hash_func(key))
        except ValueError:
            raise BloomFilterHashFunctionException(
                'hash function %s did not return an integer' % hash_func)
        return num % self.bits_per_table
