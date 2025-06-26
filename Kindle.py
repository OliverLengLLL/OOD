#Support 3 format: pdf, epub, mobi
#How to obtain book: upload/ download
#Paid ebooks

"""
Kindle:
-upload book
-download book
-read book
-remove book

How to read different format => Factory Design Pattern

We can have:
ReaderFactory
PDF
MOBI
EPUB
CHINESE
ENGLISH
"""

from enum import Enum
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import uuid
from datetime import datetime

class Format(Enum):
    PDF = "pdf"
    MOBI = "mobi"
    EPUB = "epub"

class Language(Enum):
    ENGLISH = "english"
    CHINESE = "chinese"

class BookStatus(Enum):
    FREE = "free"
    PAID = "paid"


class Book:
    def __init__(self, title: str, author: str, format: Format, content: str, language: Language = Language.ENGLISH, price: float = 0.0, status: BookStatus = BookStatus.FREE):
        self.id = str(uuid.uuid4())
        self.title = title
        self.author = author
        self.format = format
        self.content = content
        self.language = language
        self.price = price
        self.status = status
        self.upload_time = datetime.now()

    def __str__(self):
        return f"{self.title} by {self.author} ({self.format.value}) - ${self.price}"

class Reader(ABC):
    @abstractmethod
    def read(self, book: Book) -> str:
        pass

    @abstractmethod
    def get_supported_format(self) -> Format:
        pass

class PDFReader(Reader):
    def read(self, book: Book) -> str:
        if book.format != Format.PDF:
            raise ValueError("PDFReader can only read PDF format")
        return f"Reading PDF: {book.title}\nContent: {book.content[:100]}..."
    
    def get_supported_format(self) -> Format:
        return Format.PDF

class EPUBReader(Reader):
    def read(self, book: Book) -> str:
        if book.format != Format.EPUB:
            raise ValueError("EPUBReader can only read EPUB format")
        return f"Reading EPUB: {book.title}\nContent: {book.content[:100]}..."
    
    def get_supported_format(self) -> Format:
        return Format.EPUB

class MOBIReader(Reader):
    def read(self, book: Book) -> str:
        if book.format != Format.MOBI:
            raise ValueError("MOBIReader can only read MOBI format")
        return f"Reading MOBI: {book.title}\nContent: {book.content[:100]}..."
    
    def get_supported_format(self) -> Format:
        return Format.MOBI

class ReaderFactory:
    _readers = {
        Format.PDF: PDFReader,
        Format.EPUB: EPUBReader,
        Format.MOBI: MOBIReader
    }

    @classmethod
    def create_reader(cls, format: Format) -> Reader:
        if format not in cls._readers:
            raise ValueError(f"Unsupported format: {format}")
        return cls._readers[format]()
    
    @classmethod
    def get_supported_formats(cls) -> List[Format]:
        return list(cls._readers.keys())

class PaymentProcessor:
    def __init__(self):
        self.transactions: List[Dict] = []

    def process_payment(self, user_id: str, book: Book) -> bool:
        if book.status == BookStatus.FREE:
            return True
        
        transaction = {
            "transaction_id": str(uuid.uuid4()),
            "user_id": user_id,
            "book_id": book.id,
            "amount": book.price,
            "timestamp": datetime.now(),
            "status": "completed"
        }

        self.transactions.append(transaction)
        print(f"Payment processed: ${book.price} for '{book.title}'")
        return True

class BookStore:
    def __init__(self):
        self.available_books: Dict[str, Book] = {}
    
    def add_book(self, book: Book):
        self.available_books[book.id] = book
    
    def search_book(self, title: str) -> Optional[Book]:
        for book in self.available_books.values():
            if title.lower() in book.title.lower():
                return book
        return None
    
    def get_book_by_id(self, book_id: str) -> Optional[Book]:
        return self.available_books.get(book_id)
    
    def list_books(self) -> List[Book]:
        return list(self.available_books.values())


class Kindle:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.library: Dict[str, Book] = {}  # User's personal library
        self.reader_factory = ReaderFactory()
        self.payment_processor = PaymentProcessor()
        self.book_store = BookStore()

    def upload_book(self, title: str, author: str, format: Format, content: str, language: Language = Language.ENGLISH) -> str:
        book = Book(title, author, format, content, language)
        self.library[book.id] = book
        print(f"Book uploaded successfully: {book.title}")
        return book.id
    
    def download_book(self, book_id) -> bool:
        book = self.book_store.search_book(book_id)
        if not book:
            if not book:
                print("Book not found in store")
                return False
        
        if not self.payment_processor.process_payment(self.user_id, book):
            print("Payment failed")
            return False
        
        self.library[book_id] = book
        print(f"Book downloaded successfully: {book.title}")
        return True
    
    def read_book(self, book_id: str) -> Optional[str]:
        book = self.library[book_id]
        if not book:
            print("Book not found in your library")
            return None
        try:
            reader = self.reader_factory.create_reader(book.format)
            content = reader.read(book)
            print(content)
            return content
        except ValueError as e:
            print(f"Error reading book: {e}")
            return None

    def remove_book(self, book_id: str) -> bool:
        """Remove a book from personal library"""
        if book_id in self.library:
            book = self.library.pop(book_id)
            print(f"Book removed: {book.title}")
            return True
        else:
            print("Book not found in your library")
            return False
    
    def list_library(self) -> List[Book]:
        """List all books in personal library"""
        return list(self.library.values())
    
    def search_store(self, title: str) -> Optional[Book]:
        """Search for books in the store"""
        return self.book_store.search_book(title)
    

def demo_kindle_system():
    # Initialize Kindle for a user
    kindle = Kindle("user123")
    
    # Populate bookstore with some books
    store_books = [
        Book("The Python Guide", "John Doe", Format.PDF, "Python programming content...", Language.ENGLISH, 15.99, BookStatus.PAID),
        Book("Free Programming Book", "Jane Smith", Format.EPUB, "Free programming content...", Language.ENGLISH, 0.0, BookStatus.FREE),
        Book("中文编程指南", "李明", Format.MOBI, "中文编程内容...", Language.CHINESE, 12.99, BookStatus.PAID)
    ]
    
    for book in store_books:
        kindle.book_store.add_book(book)
    
    print("=== Kindle System Demo ===\n")
    
    # 1. Upload a personal book
    print("1. Uploading personal book:")
    book_id = kindle.upload_book("My Notes", "Me", Format.PDF, "Personal notes content...", Language.ENGLISH)
    
    # 2. List available books in store
    print("\n2. Available books in store:")
    for book in kindle.book_store.list_books():
        print(f"  - {book}")
    
    # 3. Download a free book
    print("\n3. Downloading free book:")
    free_book = kindle.search_store("Free Programming")
    if free_book:
        kindle.download_book(free_book.id)
    
    # 4. Download a paid book
    print("\n4. Downloading paid book:")
    paid_book = kindle.search_store("Python Guide")
    if paid_book:
        kindle.download_book(paid_book.id)
    
    # 5. List personal library
    print("\n5. My Library:")
    for book in kindle.list_library():
        print(f"  - {book}")
    
    # 6. Read books
    print("\n6. Reading books:")
    for book in kindle.list_library():
        print(f"\nReading: {book.title}")
        kindle.read_book(book.id)
        print("-" * 50)
    
    # 7. Remove a book
    print("\n7. Removing a book:")
    if kindle.list_library():
        kindle.remove_book(kindle.list_library()[0].id)
    
    # 8. Final library state
    print("\n8. Final library state:")
    for book in kindle.list_library():
        print(f"  - {book}")

if __name__ == "__main__":
    demo_kindle_system()