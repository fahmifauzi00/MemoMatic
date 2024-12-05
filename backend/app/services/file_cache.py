from typing import Dict
import os
import time

class FileCache:
    def __init__(self):
        self._cache: Dict[str, Dict] = {}
        
    def add_file(self, filename: str, file_path: str):
        """Add a file to the cache"""
        self._cache[filename] = {
            'path': file_path,
            'timestamp': time.time()
        }
        
    def get_file_path(self, filename: str) -> str:
        """Get the path of a cached file"""
        if filename in self._cache:
            return self._cache[filename]['path']
        return None
        
    def file_exists(self, filename: str) -> bool:
        """Check if a file exists in cache and on disk"""
        if filename in self._cache:
            file_path = self._cache[filename]['path']
            return os.path.exists(file_path)
        return False
        
    def clean_old_files(self, max_age: int = 24 * 60 * 60):
        """Clean files older than max_age seconds"""
        current_time = time.time()
        for filename, info in list(self._cache.items()):
            if current_time - info['timestamp'] > max_age:
                file_path = info['path']
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except OSError:
                        pass
                del self._cache[filename]

# Create a global instance
file_cache = FileCache()