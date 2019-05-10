class Byte:
    byte_ = int()

    def set_byte(self, data):
        self.byte_ = data

    def get_byte(self):
        return self.byte_


class Block:
    def __init__(self, block_number):
        self.tag_ = block_number
        self.valid_ = False
        self.data_ = []
        self.timer_ = 0

    def set_tag(self, tag):
        self.tag_ = tag

    def get_tag(self):
        return self.tag_

    def set_valid(self, valid):
        self.valid_ = valid

    def get_valid(self):
        return self.valid_

    def set_data(self, data):
        self.data_ = []
        for x in range(0, len(data)):
            self.data_ = data[x]

    def get_data(self, offset):
        if len(self.data_) > 0:
            return self.data_[offset].get_byte()

    def reset_timer(self):
        self.timer_ = 0

    def increment_timer(self):
        self.timer_ += 1

    def get_timer(self):
        return self.timer_


class Set:
    def __init__(self, set_number):
        self.block_list_ = []
        self.set_number_ = set_number

    def add_block(self, block_number):
        self.block_list_.append(Block(block_number))

    def get_set_number(self):
        return self.set_number_

    def get_block(self, tag):
        full_set = True
        result = ""

        if len(self.block_list_) > 0:
            for x in self.block_list_:
                x.increment_timer()
                if x.get_valid() is False:
                    full_set = False
                    continue
                if x.get_tag == tag and x.get_valid() is True:
                    result = "HIT"
                    data_item = x.get_data
                    x.reset_timer()

            if result == "HIT":
                return result, data_item
            elif full_set is False:
                return "MISS", None
            else:
                return "REPLACE", None

