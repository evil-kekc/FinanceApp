import unittest

from config.bot_config import BASE_DIR
from databases.db import Database, Category, GetExpenses


class TestDatabase(unittest.TestCase):
    db_path = fr'{BASE_DIR}/tests/test.db'
    create_db_script = fr'{BASE_DIR}/databases/create_db.sql'

    user_id = 1
    is_admin = True
    username = 'tester'
    password = 'password'

    def setUp(self):
        self.db = Database(self.db_path, self.create_db_script)

    def test_get_categories(self):
        expected_output = [
            Category('🛒 Продукты', 'products'),
            Category('☕️Кофе', 'coffee'),
            Category('🍽️ Обед', 'dinner'),
            Category('🍔 Кафе', 'cafe'),
            Category('🚌 Общ. Транспорт', 'transport'),
            Category('🚕 Такси', 'taxi'),
            Category('☎️Телефон', 'phone'),
            Category('📚 Книги', 'books'),
            Category('📡 Интернет', 'internet'),
            Category('✅ Подписки', 'subscriptions'),
            Category('Прочее', 'other'),
        ]
        self.assertEqual(list(self.db.get_categories()), expected_output)

    def test_check_user_exists(self):
        self.db.add_user(self.user_id, self.is_admin, self.username, self.password)
        result = self.db.check_user(1)
        self.assertEqual(result, True)

    def test_check_user_not_exists(self):
        result = self.db.check_user(2)
        self.assertEqual(result, False)

    def test_check_user_by_username(self):
        self.db.add_user(self.user_id, self.is_admin, self.username, self.password)
        result = self.db.check_user(user_id=self.user_id, username=self.username)
        self.assertEqual(result, True)

    def test_check_user_by_username_and_password(self):
        self.db.add_user(self.user_id, self.is_admin, self.username, self.password)
        result = self.db.check_user_by_username_and_password(username=self.username, password=self.password)
        self.assertEqual(result, True)

    def test_get_user_id_py_username(self):
        self.db.add_user(self.user_id, self.is_admin, self.username, self.password)
        result = self.db._get_user_id_by_username(username=self.username)
        self.assertEqual(result, self.user_id)

    def test_add_expense_by_user_id(self):
        self.db.add_user(self.user_id, self.is_admin, self.username, self.password)
        result = self.db.add_expense(user_id=self.user_id, amount=5, category_codename='products')
        self.assertEqual(result, True)

    def test_add_expense_by_user_name(self):
        self.db.add_user(self.user_id, self.is_admin, self.username, self.password)
        result = self.db.add_expense(username=self.username, amount=5, category_codename='products')
        self.assertEqual(result, True)

    def test_add_user(self):
        result = self.db.add_user(self.user_id, self.is_admin, self.username, self.password)
        self.assertEqual(result, True)

    def test_update_last_active(self):
        self.db.add_user(self.user_id, self.is_admin, self.username, self.password)
        result = self.db.update_last_active(self.user_id)
        self.assertEqual(result, True)

    def test_get_sum_of_all_expenses_all_by_username(self):
        self.db.add_user(self.user_id, self.is_admin, self.username, self.password)
        self.db.add_expense(user_id=self.user_id, amount=5, category_codename='products')
        self.db.add_expense(user_id=self.user_id, amount=5, category_codename='books')
        result = self.db.get_sum_of_expenses(username=self.username)
        first_output = GetExpenses(category='products', amount=5.0)
        second_output = GetExpenses(category='books', amount=5.0)
        first_result = result.__next__()
        second_result = result.__next__()
        self.assertEqual(first_result, first_output)
        self.assertEqual(second_result, second_output)

    def test_get_sum_of_products_expenses_per_month_by_username(self):
        self.db.add_user(self.user_id, self.is_admin, self.username, self.password)
        self.db.add_expense(user_id=self.user_id, amount=5, category_codename='products')
        result = self.db.get_sum_of_expenses(username=self.username, category='products', timedelta='month').__next__()
        first_output = 5.0
        self.assertEqual(result, first_output)

    def test_get_sum_of_products_expenses_per_week_by_username(self):
        self.db.add_user(self.user_id, self.is_admin, self.username, self.password)
        self.db.add_expense(user_id=self.user_id, amount=5, category_codename='products')
        result = self.db.get_sum_of_expenses(username=self.username, category='products', timedelta='week').__next__()
        first_output = 5.0
        self.assertEqual(result, first_output)

    def test_get_sum_of_products_expenses_per_day_by_username(self):
        self.db.add_user(self.user_id, self.is_admin, self.username, self.password)
        self.db.add_expense(user_id=self.user_id, amount=5, category_codename='products')
        result = self.db.get_sum_of_expenses(username=self.username, category='products', timedelta='day').__next__()
        first_output = 5.0
        self.assertEqual(result, first_output)

    def test_get_sum_of_all_expenses_all(self):
        self.db.add_user(self.user_id, self.is_admin, self.username, self.password)
        self.db.add_expense(user_id=self.user_id, amount=5, category_codename='products')
        self.db.add_expense(user_id=self.user_id, amount=5, category_codename='books')
        result = self.db.get_sum_of_expenses(self.user_id)
        first_output = GetExpenses(category='products', amount=5.0)
        second_output = GetExpenses(category='books', amount=5.0)
        first_result = result.__next__()
        second_result = result.__next__()
        self.assertEqual(first_result, first_output)
        self.assertEqual(second_result, second_output)

    def test_get_sum_of_products_expenses_per_month(self):
        self.db.add_user(self.user_id, self.is_admin, self.username, self.password)
        self.db.add_expense(user_id=self.user_id, amount=5, category_codename='products')
        result = self.db.get_sum_of_expenses(self.user_id, category='products', timedelta='month').__next__()
        first_output = 5.0
        self.assertEqual(result, first_output)

    def test_get_sum_of_products_expenses_per_week(self):
        self.db.add_user(self.user_id, self.is_admin, self.username, self.password)
        self.db.add_expense(user_id=self.user_id, amount=5, category_codename='products')
        result = self.db.get_sum_of_expenses(self.user_id, category='products', timedelta='week').__next__()
        first_output = 5.0
        self.assertEqual(result, first_output)

    def test_get_sum_of_products_expenses_per_day(self):
        self.db.add_user(self.user_id, self.is_admin, self.username, self.password)
        self.db.add_expense(user_id=self.user_id, amount=5, category_codename='products')
        result = self.db.get_sum_of_expenses(self.user_id, category='products', timedelta='day').__next__()
        first_output = 5.0
        self.assertEqual(result, first_output)

    def test_get_category_name_by_codename(self):
        result = self.db._get_category_name_by_codename(codename='products')
        self.assertEqual(result, '🛒 Продукты')

    def test_get_full_category_name_by_substring(self):
        result = self.db.get_full_category_codename_by_substring(substring='Продукты')
        self.assertEqual(result, 'products')

    def tearDown(self):
        self.db.delete_db(self.db_path)


if __name__ == '__main__':
    unittest.main()
