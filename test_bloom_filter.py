import unittest
import functools
import operator
import itertools

import bloomfilter
from bloomfilter import bloom_hash

class MyString(str):
    @bloom_hash
    def foo(self, size):
        return sum(ord(c) for c in self) % size

    @bloom_hash
    def bar(self, size):
        return +self.__hash__() % size

    @bloom_hash
    def baz(self, size):
        return functools.reduce(operator.mul, (ord(c) for c in self)) % size

    @bloom_hash
    def qux(self, size):
        return 0

strings = ['lily', 'oleander', 'scarlet pimpernel', 'spanish oyster']
strings = [MyString(s) for s in strings]


class TestBloomHash(unittest.TestCase):
    def hash_value_raises_hash_func_exception(self, return_val, maxsize=10):
        class BadHash:
            @bloom_hash
            def bad_hash(self, foo, bar):
                return return_val

        bf = bloomfilter.BloomFilter(maxsize, BadHash)
        obj = BadHash()
        with self.assertRaises(bloomfilter.BloomFilterHashFunctionException):
            obj.bad_hash()

    def test_bad_call_hash(self):
        self.hash_value_raises_hash_func_exception(0)

    def test_non_numeric_hash(self):
        self.hash_value_raises_hash_func_exception('not a numbner')

    def test_negative_hash(self):
        self.hash_value_raises_hash_func_exception(-1)

    def test_too_large_hash(self):
        self.hash_value_raises_hash_func_exception(10, 10)

    def test_bloom_hash_gather(self):
        gathered = set(bloom_hash._gather_hash_funcs(MyString))
        funcs = {MyString.foo, MyString.bar, MyString.baz, MyString.qux}
        self.assertSetEqual(gathered, funcs)

    def test_subclassed_obj(self):
        class Foo(MyString):
            pass
        gathered = set(bloom_hash._gather_hash_funcs(Foo))
        funcs = {Foo.foo, Foo.bar, Foo.baz, Foo.qux}
        self.assertSetEqual(gathered, funcs)

    def test_dynamic_class(self):
        def dynamic_bloom_hash_func(ret_val):
            return bloom_hash(lambda fself, maxsize: retval)

        Dynamic = type('Dynamic', (object,),
            {'a': dynamic_bloom_hash_func(123),
             'b': dynamic_bloom_hash_func(345),
             'c': dynamic_bloom_hash_func(522),})

        gathered = set(bloom_hash._gather_hash_funcs(Dynamic))
        funcs = {Dynamic.a, Dynamic.b, Dynamic.c}
        self.assertSetEqual(gathered, funcs)


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
                self.assertTrue(s in bf)

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
