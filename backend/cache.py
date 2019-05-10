import math
from cache_components import *


class Cache:
    def __init__(self, cache_size, block_size, nway, address_length):
        # cache_size is in bytes (64K = 64000)
        # block_size is also in bytes
        # nway is the number of blocks per set

        self.cache_size_ = int(cache_size)
        self.block_size_ = int(block_size)
        self.nway_set_ = int(nway)
        self.address_length_ = int(address_length)

        # calculate the number of blocks
        self.total_blocks_ = self.cache_size_/self.block_size_
        self.set_count_ = math.floor(self.total_blocks_/self.nway_set_)

        # calculate bit indices for markers
        self.offset_size_ = math.log2(self.block_size_)
        self.index_size_ = math.log2(self.set_count_)
        self.tag_size_ = address_length - self.offset_size_ - self.index_size_

        # create the cache
        self.cache_table_ = []
        self.create_cache()

        # initialize performance monitoring
        self.hit_count_ = 0
        self.miss_count_ = 0
        self.replace_count_ = 0

    def create_cache(self):
        # add error check: set count cannot exceed block count
        for x in range(0, self.set_count_):
            self.cache_table_.append(Set(x))
            for y in range(0, self.block_size_):
                self.cache_table_[x].add_block(Block(y))

    def find_block(self, address):
    # parameter address is a binary number of string type

        tag_bin = ''
        index_bin = ''
        offset_bin = ''

        # parse the binary string for tag, index, and offset
        for x in range (0, self.address_length_):
            if x < self.tag_size_:
                tag_bin += address[x]
            elif x >= self.tag_size_ and x < self.tag_size_ + self.index_size_:
                index_bin += address[x]
            elif x >= self.tag_size_ + self.index_size_:
                offset_bin += address[x]

        # convert binary values to decimal values
        tag = int(tag_bin, 2)
        index = int(index_bin, 2)
        offset = int(offset_bin, 2)

        data_item = None
        result = ""
        # search the cache
        for x in self.cache_table_:
            if x.get_set_number() == index:
                result, data_item = x.get_block(tag, offset)

        if result == "HIT":
            self.hit_count_ += 1
        elif result == "REPLACE":
            self.replace_count_ += 1
        else:
            self.miss_count_ += 1

        return result, data_item
