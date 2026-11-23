class UserNotFoundException(Exception):
    def __init__(self, user_id):
        self.id = user_id

class NotEnoughBalanceException(Exception):
    def __init__(self, user_id):
        self.id = user_id