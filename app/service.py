from app.repository import OrderRepository, UserRepository
from app.exceptions import UserNotFoundException, NotEnoughBalanceException
from app.models import User,Order

class OrderService:
    def __init__(self,session,user_repo,order_repo):
        self.session = session
        self.user_repo = user_repo
        self.order_repo = order_repo

    def create_order(self,user_id,amount):
        if amount <= 0:
            raise ValueError("Сума должна быть положительной")
        with self.session.begin():
            user = self.user_repo.get_by_id(user_id)
            if user is None:
                raise UserNotFoundException(user_id)
            if user.balance < amount:
                raise NotEnoughBalanceException(user.id)
            user.balance -= amount
            return self.order_repo.create(user_id=user.id,amount=amount,status="pending")


