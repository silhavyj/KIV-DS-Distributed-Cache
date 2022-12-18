from threading import Lock

class Cache:
    
    def __init__(self):
        self._lock = Lock() # For mutual exclusion
        self._data = {}     # Dictionary (the data itself)


    def put(self, key, value):
        # Set the value
        with self._lock:
            self._data[key] = value
    
    
    def get(self, key):
        # Retrieve the value
        with self._lock:
            if key in self._data:
                return self._data[key]
        return None
    
    
    def delete(self, key):
        # Delete the value
        with self._lock:
            if key in self._data:
                self._data.pop(key)
                return True
        return False