class HardDisk:
    def __init__(self, hd_size, bytes_pword, words_pblock):
        if hd_size % 4 != 0:
            print("Ram must be a multiple of 4")
            return
        self.hd_size_ = hd_size
        self.bytes_pword_ = bytes_pword
        self.words_pblock = words_pblock
        self.total_blocks_ = size_ram / (bytes_pword * words_pblock)
        self.total_words_ = size_ram / bytes_pword
        self.available_blocks_ = self.total_blocks_

    def write_disk(self, ):