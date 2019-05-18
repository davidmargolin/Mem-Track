

class PageTable:
    def __init__(self, pid, size, virtual_add_space):
        # size in Kbs
        self.page_table_ = []
        self.size_ = size
        self.pid_ = pid
        self.create_page_table(self)

    def create_page(self):
        page = Page(self.size_)


        