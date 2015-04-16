import unittest
import functools
import operator
import itertools

import bloomfilter
from bloomfilter import bloom_hash

class MyString(str):
    @bloom_hash
    def foo(self):
        return sum(ord(c) for c in self)

    @bloom_hash
    def bar(self):
        return self.__hash__()

    @bloom_hash
    def baz(self):
        return functools.reduce(operator.mul, (ord(c) for c in self))

    @bloom_hash
    def qux(self):
        return 1


strings = ['lily', 'oleander', 'scarlet pimpernel', 'spanish oyster']
strings = [MyString(s) for s in strings]

class TooManyArgHash:
    @bloom_hash
    def too_many_arg_hash(self, foo, bar):
        return 1


class BadValueHash:
    @bloom_hash
    def bad_value_hash(self):
        return 'not a number =('


class TestBloomHash(unittest.TestCase):
    def test_bad_call_hash(self):
        bf = bloomfilter.BloomFilter(10, TooManyArgHash)
        o = TooManyArgHash()
        with self.assertRaises(bloomfilter.BloomFilterHashFunctionException):
            o.too_many_arg_hash()

    def test_bad_value_hash(self):
        bf = bloomfilter.BloomFilter(10, BadValueHash)
        o = BadValueHash()
        with self.assertRaises(bloomfilter.BloomFilterHashFunctionException):
            o.bad_value_hash()

    def test_bloom_hash_gather(self):
        gathered = set(bloom_hash._gather_hash_funcs(MyString))
        mystring_funcs = {MyString.foo, MyString.bar, MyString.baz,
            MyString.qux}
        self.assertSetEqual(gathered, mystring_funcs)


class TestBloomFilter(unittest.TestCase):
    def test_empty(self):
        bf = bloomfilter.BloomFilter(10, MyString)
        self.assertFalse(any(bf[s] for s in strings))

    def test_membership(self):
        for perm in itertools.permutations(strings, len(strings)):
            bf = bloomfilter.BloomFilter(10, MyString)
            for s in perm:
                bf[s] = True
                self.assertTrue(bf[s])

    def test_bad_bits_per_table(self):
        with self.assertRaises(bloomfilter.BloomFilterException):
            bloomfilter.BloomFilter(0, MyString)
        with self.assertRaises(bloomfilter.BloomFilterException):
            bloomfilter.BloomFilter(-1234, MyString)

    def test_class_wo_bloom_hashes(self):
        class Foo:
            pass
        with self.assertRaises(bloomfilter.BloomFilterException):
            bloomfilter.BloomFilter(10, Foo)


if __name__ == '__main__':
    unittest.main()
