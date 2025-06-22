#!/usr/bin/env python3

import os
from pathlib import Path
from abc import ABC, abstractmethod
from typing import List, Optional
import time

class FileInfo:
    """Represents file metadata and information."""
    
    def __init__(self, path: str, name: str, size_bytes: int):
        self.path = path
        self.name = name
        self.size_bytes = size_bytes
        self._extension = self._extract_extension(name)
    
    def _extract_extension(self, filename: str) -> str:
        """Extract file extension without the dot."""
        parts = filename.split('.')
        return parts[-1].lower() if len(parts) > 1 else ""
    
    @property
    def extension(self) -> str:
        return self._extension
    
    @property
    def size_mb(self) -> float:
        return self.size_bytes / (1024 * 1024)
    
    @property
    def size_kb(self) -> float:
        return self.size_bytes / 1024
    
    def __str__(self) -> str:
        return f"{self.path} ({self.size_mb:.2f} MB, .{self.extension})"
    
    def __repr__(self) -> str:
        return f"FileInfo('{self.path}', {self.size_bytes} bytes)"


class FileFilter(ABC):
    """Abstract base class for file filters using Strategy pattern."""
    
    @abstractmethod
    def matches(self, file_info: FileInfo) -> bool:
        """Check if file matches this filter criteria."""
        pass
    
    @abstractmethod
    def description(self) -> str:
        """Return human-readable description of this filter."""
        pass


class SizeFilter(FileFilter):
    """Filter files by maximum size."""
    
    def __init__(self, max_size_mb: float):
        self.max_size_mb = max_size_mb
    
    def matches(self, file_info: FileInfo) -> bool:
        return file_info.size_mb <= self.max_size_mb
    
    def description(self) -> str:
        return f"Files <= {self.max_size_mb} MB"


class ExtensionFilter(FileFilter):
    """Filter files by file extension."""
    
    def __init__(self, extension: str):
        # Remove leading dot if present
        self.extension = extension.lower().lstrip('.')
    
    def matches(self, file_info: FileInfo) -> bool:
        return file_info.extension == self.extension
    
    def description(self) -> str:
        return f"Files with .{self.extension} extension"


class NameFilter(FileFilter):
    """Filter files by name pattern (simple contains check)."""
    
    def __init__(self, pattern: str, case_sensitive: bool = False):
        self.pattern = pattern if case_sensitive else pattern.lower()
        self.case_sensitive = case_sensitive
    
    def matches(self, file_info: FileInfo) -> bool:
        name = file_info.name if self.case_sensitive else file_info.name.lower()
        return self.pattern in name
    
    def description(self) -> str:
        sensitivity = "case-sensitive" if self.case_sensitive else "case-insensitive"
        return f"Files containing '{self.pattern}' ({sensitivity})"


class CompositeFilter(FileFilter):
    """Combines multiple filters with AND/OR logic."""
    
    def __init__(self, use_and: bool = True):
        self.filters: List[FileFilter] = []
        self.use_and = use_and
    
    def add_filter(self, file_filter: FileFilter):
        self.filters.append(file_filter)
    
    def matches(self, file_info: FileInfo) -> bool:
        if not self.filters:
            return True
        
        if self.use_and:
            return all(f.matches(file_info) for f in self.filters)
        else:
            return any(f.matches(file_info) for f in self.filters)
    
    def description(self) -> str:
        if not self.filters:
            return "No filters"
        
        operator = " AND " if self.use_and else " OR "
        descriptions = [f.description() for f in self.filters]
        return f"({operator.join(descriptions)})"


class FileFinder:
    """Main file finder class that traverses directories and applies filters."""
    
    def __init__(self):
        self.filters: List[FileFilter] = []
    
    def add_filter(self, file_filter: FileFilter):
        """Add a filter to the finder."""
        self.filters.append(file_filter)
    
    def clear_filters(self):
        """Remove all filters."""
        self.filters.clear()
    
    def find_files(self, root_path: str, max_depth: Optional[int] = None) -> List[FileInfo]:
        """
        Find files in the given directory that match all filters.
        
        Args:
            root_path: Directory to search in
            max_depth: Maximum recursion depth (None for unlimited)
        
        Returns:
            List of FileInfo objects matching all filters
        """
        results = []
        root = Path(root_path)
        
        if not root.exists():
            raise FileNotFoundError(f"Directory not found: {root_path}")
        
        if not root.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {root_path}")
        
        try:
            self._scan_directory(root, results, 0, max_depth)
        except PermissionError as e:
            print(f"Permission denied: {e}")
        
        return results
    
    def _scan_directory(self, directory: Path, results: List[FileInfo], 
                       current_depth: int, max_depth: Optional[int]):
        """Recursively scan directory for matching files."""
        if max_depth is not None and current_depth > max_depth:
            return
        
        try:
            for item in directory.iterdir():
                if item.is_file():
                    try:
                        stat = item.stat()
                        file_info = FileInfo(
                            str(item),
                            item.name,
                            stat.st_size
                        )
                        
                        if self._passes_all_filters(file_info):
                            results.append(file_info)
                    
                    except (OSError, PermissionError):
                        # Skip files we can't access
                        continue
                
                elif item.is_dir():
                    # Recursively scan subdirectories
                    self._scan_directory(item, results, current_depth + 1, max_depth)
        
        except PermissionError:
            # Skip directories we can't access
            pass
    
    def _passes_all_filters(self, file_info: FileInfo) -> bool:
        """Check if file passes all active filters."""
        return all(f.matches(file_info) for f in self.filters)


class ResultFormatter:
    """Formats and displays search results."""
    
    @staticmethod
    def print_results(files: List[FileInfo], applied_filters: List[FileFilter]):
        """Print formatted search results."""
        print("=" * 60)
        print("File Finder Results")
        print("=" * 60)
        
        if applied_filters:
            print("Applied filters:")
            for filter_obj in applied_filters:
                print(f"  - {filter_obj.description()}")
            print()
        
        print(f"Found {len(files)} matching files:")
        print()
        
        if files:
            # Print header
            print(f"{'Path':<50} | {'Size (MB)':<10} | {'Extension':<10}")
            print("-" * 75)
            
            # Print files
            for file_info in files:
                print(f"{file_info.path:<50} | {file_info.size_mb:<10.2f} | .{file_info.extension:<10}")
        else:
            print("No files found matching the criteria.")
        
        print()
    
    @staticmethod
    def save_results_to_file(files: List[FileInfo], output_file: str):
        """Save results to a text file."""
        with open(output_file, 'w') as f:
            f.write("File Finder Results\n")
            f.write("=" * 60 + "\n\n")
            
            for file_info in files:
                f.write(f"{file_info.path}\t{file_info.size_mb:.2f}MB\t.{file_info.extension}\n")


class FileFinderApp:
    """Main application class with convenient methods for common use cases."""
    
    def __init__(self):
        self.finder = FileFinder()
        self.formatter = ResultFormatter()
    
    def find_small_files(self, root_path: str, max_size_mb: float):
        """Find files smaller than specified size."""
        try:
            self.finder.clear_filters()
            size_filter = SizeFilter(max_size_mb)
            self.finder.add_filter(size_filter)
            
            results = self.finder.find_files(root_path)
            self.formatter.print_results(results, [size_filter])
            return results
        
        except Exception as e:
            print(f"Error scanning directory: {e}")
            return []
    
    def find_files_by_extension(self, root_path: str, extension: str):
        """Find files with specified extension."""
        try:
            self.finder.clear_filters()
            ext_filter = ExtensionFilter(extension)
            self.finder.add_filter(ext_filter)
            
            results = self.finder.find_files(root_path)
            self.formatter.print_results(results, [ext_filter])
            return results
        
        except Exception as e:
            print(f"Error scanning directory: {e}")
            return []
    
    def find_small_text_files(self, root_path: str, max_size_mb: float = 5.0):
        """Find small .txt files (combines size and extension filters)."""
        try:
            self.finder.clear_filters()
            size_filter = SizeFilter(max_size_mb)
            txt_filter = ExtensionFilter("txt")
            
            self.finder.add_filter(size_filter)
            self.finder.add_filter(txt_filter)
            
            results = self.finder.find_files(root_path)
            self.formatter.print_results(results, [size_filter, txt_filter])
            return results
        
        except Exception as e:
            print(f"Error scanning directory: {e}")
            return []
    
    def find_files_with_pattern(self, root_path: str, pattern: str, max_size_mb: Optional[float] = None):
        """Find files containing a pattern in their name, optionally with size limit."""
        try:
            self.finder.clear_filters()
            name_filter = NameFilter(pattern)
            filters = [name_filter]
            
            self.finder.add_filter(name_filter)
            
            if max_size_mb:
                size_filter = SizeFilter(max_size_mb)
                self.finder.add_filter(size_filter)
                filters.append(size_filter)
            
            results = self.finder.find_files(root_path)
            self.formatter.print_results(results, filters)
            return results
        
        except Exception as e:
            print(f"Error scanning directory: {e}")
            return []


def main():
    """Example usage of the file finder."""
    app = FileFinderApp()
    
    # Adjust search path as needed
    search_path = os.path.expanduser("~/Documents")  # or "/home/user/documents"
    
    if not os.path.exists(search_path):
        search_path = "."  # Use current directory if ~/Documents doesn't exist
    
    print(f"Searching in: {search_path}")
    print()
    
    # Example 1: Find files < 5MB
    print("1. Finding files < 5MB:")
    app.find_small_files(search_path, 5.0)
    
    # Example 2: Find .txt files
    print("\n2. Finding .txt files:")
    app.find_files_by_extension(search_path, "txt")
    
    # Example 3: Find small .txt files
    print("\n3. Finding .txt files < 5MB:")
    app.find_small_text_files(search_path, 5.0)
    
    # Example 4: Find files with "test" in name
    print("\n4. Finding files containing 'test':")
    app.find_files_with_pattern(search_path, "test")


if __name__ == "__main__":
    main


class Filter:
    def __init__(self):
        pass

    def apply(self, file):
        pass

class SizeFilter(Filter):
    def __init__(self, size):
        self.size = size

    def apply(self, file):
        return file.size > self.size

class ExtensionFilter(Filter):
    def __init__(self, ext):
        self.extension = ext
    def apply(self, file):
        return file.extension == self.extension

class File:
    def __init__(self, name, size):
        self.name = name
        self.isDirectory = False if '.' in name else True
        self.size = size
        self.extension = name.split(".")[1] if '.' in name else ""
        self.children = []

    def __repr__(self):
        return "{" + self.name + "}"

class FileSystem:

    def __init__(self):
        self.filters = []

    def addFilter(self, f):

        if isinstance(f, Filter):
            self.filters.append(f)


    # This implementation is OR implementation of filter. 
    def traverse(self, root):

        result = []
        def traverseUtil(root):
            for r in root.children:
                if r.isDirectory:
                    traverseUtil(r)
                else:
                    for _f in self.filters:
                        if _f.apply(r):
                            print("result:", result)
                            result.append(r)
        #return result
        traverseUtil(root)
        return result

f1 = File("StarTrek.txt", 5)
f2 = File("StarWars.xml", 10)
f3 = File("JusticeLeague.txt", 15)
f4 = File("IronMan.txt", 9)
f5 = File("Spock.jpg", 1)
f6 = File("BigBangTheory.txt", 50)
f7 = File("MissionImpossible", 10)
f8 = File("BreakingBad", 11)
f9 = File("root", 100)

f9.children = [f7, f8]
f7.children = [f1, f2, f3]
f8.children = [f4, f5, f6]

filter1 = SizeFilter(5)
filter2 = ExtensionFilter("txt")

fs = FileSystem()
fs.addFilter(filter1)
fs.addFilter(filter2)
print(fs.traverse(f9))