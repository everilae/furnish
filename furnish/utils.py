class LockPick:
    """
    Store required keys.
    """
    def __init__(self):
        self.keys = set()

    def __getitem__(self, name):
        self.keys.add(name)
