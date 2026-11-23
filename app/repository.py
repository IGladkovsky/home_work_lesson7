from sqlalchemy import select
from sqlalchemy.orm import Session
from decimal import Decimal

from app.models import User, Order


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, email: str, balance: Decimal) -> User:
        user = User(email=email, balance=balance)
        self.session.add(user)
        return user

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.session.scalars(stmt).one_or_none()

    def get_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)


class OrderRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, user_id: int, amount: Decimal, status: str = "pending") -> Order:
        order = Order(user_id=user_id, amount=amount, status=status)
        self.session.add(order)
        return order


class BrokenOrderRepository:
    def __init__(self, session):
        self.session = session

    def create(self, user_id: int, amount: Decimal, status: str = "pending"):
        raise RuntimeError("injected failure")