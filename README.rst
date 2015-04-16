bloomfilter
===========

A probabalistic, space-efficient set membership data structure.

Quickstart
----------

1. ``import bloomfilter``.
2. Mark your own hash functions with ``@bloom_hash``.
3. Instantiate a ``BloomFilter``.
4. Use ``bloom_filter[key]`` to query and ``bloom_filter[key] = True`` to set.

Description
-----------

A Bloom filter is a data structure that allows you to probabilistically
determine whether an item is a member of a set. It is like a Python dict, except
that there is no storage of values (as in key-value pairs), which cuts down on
the space needed to hold this data structure. **In essence, the trade off is
less space for less accuracy in determining set membership.**

Bloom filters are often used in conjunction with proper key-value stores that
may be (relatively) expensive to access, such as a remote Redis server. Instead
of building a request and sending/receiving over a network, Bloom filters can
quickly and space-efficiently provide an answer as to whether that effort is
necessary.

Bloom filters can return false positives: returning that a key **is** in the set
when it has actually never been seen before. False negatives, however, are not
possible. You will always be able to know if "key might be in set" or "key is in
set". The rate of false positives can be decreased by tuning the size of the
underlying tables.

For more details on implementation and analysis, read `the well-written
wikipedia article <https://en.wikipedia.org/wiki/Bloom_filter>`_.

Example
-------

.. code-block:: python

    from bloomfilter import bloom_hash, BloomFilter

    class Record(str):
        @bloom_hash
        def hasha(self, maxsize):
            return sum(ord(c) for c in self) % maxsize

        @bloom_hash
        def hashb(self, maxsize):
            return self.__hash__() % maxsize

    bf = BloomFilter(bits_per_table=2**10, cls=Record)

    a = Record('foo')
    bf[a] # => False
    bf[a] = True
    bf[a] # => True

Querying for/Setting a Key
--------------------------

Query a BloomFilter by simply calling it's __getitem__ method with your key,
commonly realized as ``my_bloom_filter[key]``.

To set a key in a BloomFilter, call __setitem__ with your key and a value, like
``my_bloom_filter[key] = True``. **The value is ignored, but you must provide
one** so that Python understands your intent for assignment. Remember, in a Bloom
Filter, we don't store values, only provide set membership responses. If you're
curious, BloomFilter stores a binary 0 (not set) or 1 (set) in the underlying
tables.

``bloom_hash`` Requirements
---------------------------

Wrap your object hash functions with the ``@bloom_hash`` decorator. This marks
your hash functions so that BloomFilter can call them when querying or setting
a key.

**The number of hash functions you provide will be the number
of underlying tables in your Bloom filter.** More tables can lead to more
accuracy, but will cost most space.

BloomFilter's are agnostic of the objects they record, so your hash functions
have three requirements to ensure their generality.

1. Hash functions must be object methods with only one positional argument
   max_size, indicating the range [0, max_size] of the hash .  Therefore, hash
   functions will have access to the conventional ``self`` of an object, so you
   can use its data to generate a hash, and the max_size allows methods to
   create uniform distributions, if you'd like.
2. Hash functions must return an integer less than or equal to the
   BloomFilter.bits_per_table. They are used for indexing into an underlying
   table.
3. ``@bloom_hash`` must be applied to your class's hash functions **before**
   ``BloomFilter`` initialization. Your hash functions are tightly linked to the
   underlying tables, so any addition/removal/modification of will break any
   guarantees.

Hash Function Properties
------------------------

Ideally, hash functions will distribute evenly over the [0, max_size] range,
which is why the max_size argument is given to hash functions. It is up to the
user to return well-distributed values over the entire range.

It is my recommendation to use peer-reviewed hash functions that have properties
appropriate to your application.

Most popular hash functions have the added boon of providing hash spaces that
are much larger than any table sizes you will make with a Bloom filter. So,
returning hashes like ``SHA512(my_data) % max_size`` will be sufficient for most
purposes.
