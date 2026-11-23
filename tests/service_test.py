import pytest
from decimal import Decimal
from sqlalchemy import select
from app.database import SessionLocal, engine
from app.models import User, Order
from app.repository import UserRepository,BrokenOrderRepository
from app.service import OrderService
from app.exceptions import UserNotFoundException, NotEnoughBalanceException


def test_create_order_rollback_on_failure():

    with SessionLocal() as session:
        user = User(email="test@example.com", balance=Decimal("1000.00"))
        session.add(user)
        session.commit()
        user_id = user.id

    with SessionLocal() as session:
        user_repo = UserRepository(session)
        broken_order_repo = BrokenOrderRepository(session)
        service = OrderService(session, user_repo, broken_order_repo)

        with pytest.raises(RuntimeError, match="injected failure"):
            service.create_order(user_id, amount=Decimal("500.00"))

    with SessionLocal() as session:
        user = session.get(User, user_id)
        assert user.balance == Decimal("1000.00"), \
            f"Баланс должен был остаться 1000, но стал {user.balance}"

        orders = session.scalars(
            select(Order).where(Order.user_id == user_id)
        ).all()
        assert len(orders) == 0, \
            f"Заказов быть не должно, но найдено {len(orders)}"