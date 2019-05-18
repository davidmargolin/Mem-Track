from memory_components import *

class FrameTable:
    frame_table_ = []

    def __init__(self, size_ram, bytes_pword, words_pblock):
        if size_ram % 4 != 0:
            print ("Ram must be a multiple of 4")
            return
        self.size_ram_ = size_ram # in bytes
        self.bytes_pword_ = bytes_pword # num of bytes in a word
        self.words_pblock_ = words_pblock # num of words in a block
        self.total_blocks_ = size_ram / (bytes_pword * words_pblock)
        self.total_words_ = size_ram  / bytes_pword
        self.available_blocks_ = self.total_blocks_

        # create memory
        self.generate_table()

    def generate_table(self):
        for x in range(0, self.total_blocks_):
            # None is the location of the process PID
            self.frame_table_.append([None, Word(self.word_size_)])

    def write_memory(self, pid, words_list):
        if self.available_blocks == 0: # check if memory is full
            if not self.replace_process(pid, words_list): # if mem is full replace an inactive process
                return 0
        else:
            for word in range(0, len(words_list)):
                if not self.reserve_memory(pid, word):
                    return 0


    def reserve_memory(self, pid, data):
        word_index = 0
        # data  should be a list of bytes
        for word in range(0, len(self.frame_table_)):
            if self.frame_table_[word][0] is None:
                for relative_word in range(word, (word+self.word_size_)):
                    self.frame_table_[relative_word][0] = pid
                    self.frame_table_[relative_word][1].set_word(data)
                    word_index += 1
                self.available_blocks -= 1
                return byte
            else:
                byte = byte + (self.word_size_ - 1)
        return 0

    def replace_process(self, pid, word):

        





