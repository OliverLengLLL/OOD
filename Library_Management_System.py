from typing import List, Optional, Dict
from datetime import date, datetime, timedelta

class Student:
    def __init__(self, student_id: str, name: str, email: str):
        self.student_id = student_id
        self.name = name
        self.email = email
        self.total_fine: float = 0.0
        self.max_books = 5

class Book:
    def __init__(self, book_id: str, book_info: 'BookInfo'):
        self.book_id = book_id
        self.book_info = book_info
        self.is_available = True
    
    def borrow(self):
        self.is_available = False
    
    def return_book(self):
        self.is_available = True

class BookInfo:
    def __init__(self, info_id: str, title: str, author: str, isbn: str, genre: str):
        self.info_id = info_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.genre = genre
        self.description = ""
        self.publication_year = 0
    
    def matches_search(self, search_term: str, search_type: str) -> bool:
        search_term_lower = search_term.lower()
        if search_type == "title":
            return search_term_lower in self.title.lower()
        elif search_type == "author":
            return search_term_lower in self.author.lower()
        elif search_type == "isbn":
            return search_term_lower in self.isbn.lower()
        elif search_type == "genre":
            return search_term_lower in self.genre.lower()
        return False

#Relationship which student borrow which book
class BorrowRecord:
    def __init__(self, student: Student, book: Book, startDate: date):
        self.student = student
        self.book = book
        self.start_date = startDate
        self.due_date = startDate + timedelta(days=60)
        self.return_date: Optional[date] = None
        self.is_returned = False
        self.fine_amount = 0.0

    def return_book(self, return_date: date) -> float:
        self.return_date = return_date
        self.is_returned = True
        
        if return_date > self.due_date:
            days_late = (return_date - self.due_date).days
            self.fine_amount = days_late * 1.0 
        
        return self.fine_amount
    
    def is_overdue(self):
        return not self.is_returned and date.today() > self.due_date
    

class Fine:
    def __init__(self, student: Student, book: Book, amount: float, reason: str):
        self.student = student
        self.book = book
        self.amount = amount
        self.reason = reason
        self.date_created = date.today()
        self.is_paid = False
        self.date_paid: Optional[date] = None

    def pay_fine(self):
        self.is_paid = True
        self.date_paid = date.today()
    
class BorrowBookRequest:
    def __init__(self, student: Student, book: Book):
        self.student = student
        self.book = book
        self.request_date = date.today()
        self.status = "pending" 

class ReturnBookRequest:
    def __init__(self, student: Student, book: Book):
        self.student = student
        self.book = book
        self.return_date = date.today()
        self.status = "pending"

class SearchBookRequest:
    def __init__(self, student: Student, search_term: str = "", search_type: str = "title"):
        self.student = student
        self.search_term = search_term
        self.search_type = search_type
        self.request_date = date.today()

class LibrarySystem:
    def __init__(self, books: List[Book], bookInfos: List[BookInfo]):
        self.books = books
        self.bookInfos = bookInfos
        self.students: List[Student] = []
        self.borrow_records: List[BorrowRecord] = []
        self.student_records: Dict[Student, List[BorrowRecord]] = {}
        self.fines: List[Fine] = []
        self.daily_fine_rate = 1.0

    def add_student(self, student: Student):
        self.students.append(student)
        self.student_records[student] = []

    def can_borrow(self, student: Student) -> bool:
        """Check if student can borrow more books"""
        active_records = [record for record in self.student_records.get(student, []) if not record.is_returned]
        return len(active_records) < student.max_books and student.total_fine == 0
    
    def find_student_by_id(self, student_id: str) -> Optional[Student]:
        for student in self.students:
            if student.student_id == student_id:
                return student
        return None
    
    def find_book_by_id(self, book_id: str) -> Optional[Book]:
        for book in self.books:
            if book.book_id == book_id:
                return book
        return None
    
    def find_available_book_by_info(self, book_info: BookInfo) -> Optional[Book]:
        for book in self.books:
            if book.book_info == book_info and book.is_available:
                return book
        return None

    def handleSearchBookRequest(self, searchBookRequest: SearchBookRequest) -> List[BookInfo]:
        results = []

        if not searchBookRequest.search_term:
            return self.bookInfos
        
        for book_info in self.bookInfos:
            if book_info.matches_search(searchBookRequest.search_term, searchBookRequest.search_type):
                results.append(book_info)
        return results

    def handleBorrowBookRequest(self, borrowBookRequest: BorrowBookRequest) -> Book:
        student = borrowBookRequest.student
        requested_book = borrowBookRequest.book

        if not self.can_borrow(student):
            return None
        
        if not requested_book.is_available:
            available_book = self.find_available_book_by_info(requested_book.book_info)
            if not available_book:
                borrowBookRequest.status = "rejected"
                return None
            requested_book = available_book

        borrow_date = borrowBookRequest.request_date
        requested_book.borrow()

        borrow_record = BorrowRecord(student, requested_book, borrow_date)
        self.borrow_records.append(borrow_record)
        self.student_records[student].append(borrow_record)

        borrowBookRequest.status = "appproved"

        return requested_book


    def handleReturnBookRequest(self, return_book_request: ReturnBookRequest) -> int:
        student = return_book_request.student
        book = return_book_request.book
        return_date = return_book_request.return_date

        borrow_record = None
        for record in self.student_records.get(student, []):
            if record.book == book and not record.is_returned:
                borrow_record = record
                break
        
        if not borrow_record:
            return -1 

        fine_amount = borrow_record.return_book(return_date)
        book.return_book()

        if fine_amount > 0:
            days_late = (return_date - borrow_record.due_date).days if return_date > borrow_record.due_date else 0
            fine = Fine(student, book, fine_amount, f"Late return: {days_late} days")
            self.fines.append(fine)
            student.total_fine += fine_amount
    
        return_book_request.status = "completed"

        if return_date > borrow_record.due_date:
            return (return_date - borrow_record.due_date).days
        
        return 0
    
    def pay_student_fine(self, student: Student, amount: float) -> bool:
        """Pay fines for a student"""
        if amount <= 0:
            return False
        
        unpaid_fines = [fine for fine in self.fines if fine.student == student and not fine.is_paid]
        
        remaining_amount = amount
        for fine in unpaid_fines:
            if remaining_amount <= 0:
                break
            
            if remaining_amount >= fine.amount:
                remaining_amount -= fine.amount
                student.total_fine -= fine.amount
                fine.pay_fine()
            else:
                break
        
        return remaining_amount < amount

    def get_overdue_books(self) -> List[Book]:
        """Get all currently overdue books"""
        overdue_books = []
        for book in self.books:
            if not book.is_available and book.is_overdue():
                overdue_books.append(book)
        return overdue_books
    
    def get_student_borrowed_books(self, student: Student) -> List[Book]:
        """Get all books currently borrowed by a student"""
        active_records = [record for record in self.student_records.get(student, []) 
                         if not record.is_returned]
        return [record.book for record in active_records]
    
    def get_available_books(self) -> List[Book]:
        """Get all available books"""
        return [book for book in self.books if book.is_available]
    
    
if __name__ == "__main__":
    # Create book infos
    book_info1 = BookInfo("INFO001", "Python Programming", "John Author", "978-1234567890", "Programming")
    book_info2 = BookInfo("INFO002", "Data Structures", "Jane Author", "978-0987654321", "Computer Science")
    
    # Create book copies
    book1 = Book("BOOK001", book_info1)
    book2 = Book("BOOK002", book_info1)  # Another copy of same book
    book3 = Book("BOOK003", book_info2)
    
    # Create library system
    library = LibrarySystem([book1, book2, book3], [book_info1, book_info2])
    
    # Create students
    student1 = Student("S001", "Alice Smith", "alice@email.com")
    student2 = Student("S002", "Bob Jones", "bob@email.com")
    library.add_student(student1)
    library.add_student(student2)
    
    # Test search
    search_request = SearchBookRequest(student1, "Python", "title")
    search_results = library.handleSearchBookRequest(search_request)
    print(f"Search results: {[info.title for info in search_results]}")
    
    # Test borrow
    borrow_request = BorrowBookRequest(student1, book1)
    borrowed_book = library.handleBorrowBookRequest(borrow_request)
    print(f"Borrowed book: {borrowed_book.book_id if borrowed_book else 'None'}")
    
    # Test return
    return_request = ReturnBookRequest(student1, book1)
    days_overdue = library.handleReturnBookRequest(return_request)
    print(f"Days overdue: {days_overdue}")