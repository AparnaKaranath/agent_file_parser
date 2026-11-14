# Library Manager

A small library system that shows abstraction, inheritance, polymorphism and encapsulation in Python. Run it with `python main.py`.

## Deliverables

### 1. Why is `LibraryItem` abstract, and what happens if `DVD` forgets to write `late_fee()`?

`LibraryItem` is only a general idea of an item, and each kind of item charges a different late fee, so it inherits from `ABC` and marks `late_fee()` with `@abstractmethod`. This means `LibraryItem("x", 1)` cannot be created, and every child class is forced to provide its own `late_fee()`. If `DVD` forgot to write it, `DVD` would also be abstract, and creating one would raise `TypeError: Can't instantiate abstract class DVD without an implementation for abstract method 'late_fee'` as soon as the object is made, not later when the fee is calculated.

### 2. What happens when you read `item.__available` from outside the class, and why do we use `is_available()` instead?

Reading `book.__available` outside the class raises `AttributeError: 'Book' object has no attribute '__available'`. This is because Python renames (name-mangles) attributes that start with two underscores to `_LibraryItem__available`. We use `is_available()` so other code can read the status without changing it directly; the status should only change through `mark_borrowed()` and `mark_returned()`, which keeps the object in a valid state and lets the class change how it stores availability without breaking other code.

### 3. What is the difference between `LibraryItem.total_items` and `self.title`?

`LibraryItem.total_items` is a class attribute: there is one copy shared by every item, and `__init__` increases it through the class name, so it counts all books, magazines and DVDs created (3 in `main.py`). `self.title` is an instance attribute: each object stores its own value, so the book's title is `"Python 101"` while the DVD's title is `"Inception"`.
