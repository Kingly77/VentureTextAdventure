class Tags:
    def __init__(self, tags: set = None):
        self.tags = tags or set()

    def add_tag(self, tag: str):
        self.tags.add(tag)

    def has_tag(self, tag: str):
        return tag in self.tags

    def __repr__(self):
        return f"<Tags with: {self.tags}>"
