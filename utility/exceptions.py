class UserAlreadyExistsException(Exception):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User with email {email} already exists.")

class DatabaseException(Exception):
    def __init__(self, message: str = "A database error occurred"):
        self.message = message
        super().__init__(self.message)

class UserNotFoundException(Exception):
    def __init__(self, message: str = "User does not exist"):
        self.message = message
        super().__init__(self.message)
