class MemoryReader:
    def __init__(self, data):
        self.data = data
        self._offset = 0

    def read(self, n=-1):
        if self._offset >= len(self.data):
            return b''

        if n < 0:
            self._offset = len(self.data)
            return self.data[self._offset:]
        else:
            start = self._offset
            tail = min(len(self.data), start + n)
            self._offset += tail - start
            return self.data[start:tail]