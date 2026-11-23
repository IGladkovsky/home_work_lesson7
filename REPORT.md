## 1. Модели, доступ и репозитории

Модели User и Order созданы. В User есть поле email, balance и связь orders.
В Order есть user_id, amount, status и обратная связь с Users.
Для каждой модели отдельный репозитории

## 2. Начальная миграция

Миграция afc00c031e59 создает таблицу User,Orders(без status)

## 3. Статус заказа и миграции

Миграция 9a9b3125eef3 добавляет колонку status в orders при upgrade,
цепочка upgrade->downgrade->upgrade добавляет, а затем сбрасывает все значаения status

## 4. Атомарное создание заказа

Метод `create_order` выполняет строгую последовательность: проверка суммы (>0), поиск пользователя, проверка достаточности баланса, списание средств и создание заказа со статусом `pending`.

Вся операция обёрнута в `with self.session.begin():` внутри сервисного слоя. Репозитории получают эту сессию и не вызывают `commit()` или `rollback()` самостоятельно.

Реализован тест `service_test.py`. Для имитации сбоя используется `BrokenOrderRepository`, который выбрасывает исключение сразу после попытки сохранения заказа (то есть после списания баланса).
После перехвата исключения данные проверяются в новой сессии. Подтверждено, что баланс пользователя остался неизменным (`1000.00`), а запись о заказе в базе отсутствует. Транзакция успешно откатилась целиком.


## 5. N+1: SQL-журнал для test_n_plus_one.py

### Наивный вариант (ленивая загрузка)

- SELECT users.id, users.email, users.balance FROM users;
- SELECT orders.id, orders.user_id, orders.amount, orders.status FROM orders WHERE orders.user_id = 1;
- SELECT orders.id, orders.user_id, orders.amount, orders.status FROM orders WHERE orders.user_id = 2;
- SELECT orders.id, orders.user_id, orders.amount, orders.status FROM orders WHERE orders.user_id = 3;
- SELECT orders.id, orders.user_id, orders.amount, orders.status FROM orders WHERE orders.user_id = 4;
- SELECT orders.id, orders.user_id, orders.amount, orders.status FROM orders WHERE orders.user_id = 5;
- SELECT orders.id, orders.user_id, orders.amount, orders.status FROM orders WHERE orders.user_id = 6;

Итого: **7 запросов** = 1 (users) + 6 (orders по одному на каждого пользователя).

### Оптимизированный вариант (selectinload)

- SELECT users.id, users.email, users.balance FROM users;
- SELECT orders.user_id, orders.id, orders.amount, orders.status 
FROM orders WHERE orders.user_id IN (1, 2, 3, 4, 5, 6);
Итого: 2 запроса = основной SELECT + один пакетный с `IN`.

### Условия эксперимента
- 6 пользователей, у каждого по 3 заказа (кроме первого — у него 0 заказов).
- Для каждого варианта создана свежая сессия через `with SessionLocal()`.
- Счётчик запросов сброшен перед каждым прогоном через `event.listen(engine, "before_cursor_execute", ...)`.