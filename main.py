from models import Book, Magazine, DVD, Member
book = Book("Python 101", 1, "A. Rao")
magazine = Magazine("Tech Monthly", 2, 42)
dvd = DVD("Inception", 3, 148)
alice = Member("Alice", 101)
bob = Member("Bob", 102, max_items=1)
# 1. Borrowing with error handling
try:
    alice.borrow(book)
    print("Alice borrowed:", book.describe())
    bob.borrow(book)  # should fail: already borrowed
except ValueError as e:
    print("Could not borrow:", e)
# 2. Borrow-limit error and not-borrowed error
try:
    bob.borrow(magazine)
    print("Bob borrowed:", magazine.describe())
    bob.borrow(dvd)  # should fail: Bob's limit is 1
except ValueError as e:
    print("Could not borrow:", e)
try:
    bob.return_item(book)  # should fail: Bob never borrowed the book
except ValueError as e:
    print("Could not return:", e)
# 3. Polymorphism: one loop, no type checks
items = [book, magazine, dvd]
for item in items:
    print(item.describe(), "-> late fee for 3 days: Rs", item.late_fee(3))
# 4. Class attribute shared by all objects
print("Total items created:", Book.total_items)
# 5. Encapsulation: the private attribute is not reachable from outside
try:
    print(book.__available)
except AttributeError as e:
    print("AttributeError:", e)
print("Is the book available?", book.is_available())

