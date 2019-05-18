from frame_table import *

class MemoryManagement:
    def __init__(self, size_ram, size_page_table, size_cache, size_word, size_block, set_association, address_length):
        self.size_mem = size_ram
        self.size_page_table_ = size_page_table
        self.size_cache_ = size_cache
        self.size_word_ = size_word
        self.size_block_ = size_block
        self.set_assoc_ = set_association
        self.add_len_ = address_length
        self.frame_table_ = FrameTable(size_ram, size_word, size_block)
        self.pid_ = 0

    def create_process(self, instructions):
        if self.frame_table_.write_memory(self.pid_, instructions)











