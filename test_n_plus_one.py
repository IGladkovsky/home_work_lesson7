from decimal import Decimal
from sqlalchemy import select, event
from sqlalchemy.orm import selectinload
from app.database import SessionLocal, engine
from app.models import User, Order


def create_test_data():
    with SessionLocal() as session:
        for i in range(5):
            user = User(email=f"user{i}@example.com", balance=Decimal("1000.00"))
            session.add(user)
            session.flush()

            for j in range(3):
                order = Order(user_id=user.id, amount=Decimal(f"{100 + j * 10}.00"), status="pending")
                session.add(order)

        session.commit()


def naive_approach():
    with SessionLocal() as session:
        users = session.scalars(select(User)).all()

        for user in users:
            print(f"User: {user.email}, Orders: {[order.amount for order in user.orders]}")

    print()


def selectinload_approach():
    with SessionLocal() as session:
        stmt = select(User).options(selectinload(User.orders))
        users = session.scalars(stmt).all()

        for user in users:
            print(f"User: {user.email}, Orders: {[order.amount for order in user.orders]}")

    print()


def count_queries():
    query_count = {"count": 0}

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        query_count["count"] += 1

    event.listen(engine, "before_cursor_execute", before_cursor_execute)
    return query_count


def main():
    create_test_data()

    # Наивный вариант
    counter = count_queries()
    naive_approach()
    print(f"Количество SQL-запросов (наивный): {counter['count']}\n")

    # Оптимизированный вариант
    counter = count_queries()
    selectinload_approach()
    print(f"Количество SQL-запросов (selectinload): {counter['count']}\n")


if __name__ == "__main__":
    main()