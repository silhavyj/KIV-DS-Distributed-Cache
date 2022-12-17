class Cache:
    
    def __init__(self):
        self._lock = Lock()
        self._data = {}


    def put(self, key, value):
        with self._lock:
            self._data[key] = value
    
    
    def get(self, key):
        with self._lock:
            if key in self._data:
                return self._data[key]
        return None
    
    
    def delete(self, key):
        with self._lock:
            if key in self._data:
                self._data.pop(key)
                return True
        return False