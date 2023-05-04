import hashlib
import logging
import os
import sqlite3 as sq
from sqlite3 import OperationalError, IntegrityError
from typing import NamedTuple, Generator

from config.bot_config import BASE_DIR, LOGGER

logging.basicConfig(level=logging.INFO, filename=fr'{str(BASE_DIR)}/{LOGGER}',
                    format="%(asctime)s | %(levelname)s | %(funcName)s: %(lineno)d | %(message)s",
                    datefmt='%H:%M:%S')


class Category(NamedTuple):
    """Processing the output of the expense name and its codename"""
    name: str
    codename: str


class GetExpenses(NamedTuple):
    """Processing the output of the expense category and its amount"""
    category: str
    amount: float


class Database:
    def __init__(self, db_file: str, sql_script_file: str):
        self.connection = sq.connect(db_file, check_same_thread=False)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()
        self.sql_script = sql_script_file
        self._create_db()

    def _create_db(self) -> None:
        """Create a tables

        :return: None
        """
        with open(self.sql_script, 'r', encoding='utf-8') as sql_file:
            sql_script = sql_file.read()

        try:
            with self.connection:
                self.cursor.executescript(sql_script)
            logging.info('Database users connected')
        except OperationalError:
            logging.info('Database users already exists')

    def _get_user_id_by_username(self, username: str) -> int:
        """Getting user id by username

        :param username: username
        :return: int user id
        """
        try:
            with self.connection:
                result = self.cursor.execute("SELECT id "
                                             "FROM users "
                                             "WHERE username = ?",
                                             (username,))
                return result.fetchone()[0]
        except Exception as ex:
            logging.error(repr(ex))

    def check_user(self, user_id: int = None, username: str = None) -> bool | int:
        """Checking if a user exists in the database

        :param username: username
        :param user_id: user id
        :return: True if user exists, False if user not exists
        """
        if not username:
            try:
                with self.connection:
                    result = self.cursor.execute(
                        "SELECT id "
                        "FROM users "
                        "WHERE id = ?",
                        (user_id,)
                    )
                    if result.fetchall():
                        return True
                    else:
                        return False
            except Exception as ex:
                logging.error(repr(ex))

        elif username:
            try:
                with self.connection:
                    self.cursor.execute(
                        "SELECT username "
                        "FROM users "
                        "WHERE username = ?",
                        (username,)
                    )
                    result = bool(len(self.cursor.fetchall()))
                    return result
            except Exception as ex:
                logging.error(repr(ex))

    def check_user_by_username_and_password(self, username: str = None, password: str = None) -> bool:
        """Checking if a user exists in the database by username and password

        :param username: username
        :param password: password
        :return: bool
        """
        if username and password:
            try:
                with self.connection:
                    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
                    self.cursor.execute(
                        "SELECT username "
                        "FROM users "
                        "WHERE username = ? AND password = ?",
                        (username, password_hash)
                    )
                    result = bool(len(self.cursor.fetchall()))
                    return result
            except Exception as ex:
                logging.error(repr(ex))

    def get_categories(self) -> Generator:
        """Getting all categories from the database

        :return: category generator object
        """
        try:
            with self.connection:
                result = self.cursor.execute("SELECT name, codename "
                                             "FROM categories")
                for category in result:
                    result = Category(name=category[0].title(), codename=category[1])
                    yield result
        except Exception as ex:
            logging.error(repr(ex))

    def get_full_category_codename_by_substring(self, substring: str) -> str:
        """Getting the codename of the category by the occurrence of a substring in the name of the category

        :param substring: category name
        :return:
        """
        try:
            with self.connection:
                result = self.cursor.execute("SELECT codename "
                                             "FROM categories "
                                             "WHERE name LIKE ?",
                                             (f'%{substring.lower()}',))
                return result.fetchone()[0]
        except Exception as ex:
            logging.error(repr(ex))

    def add_expense(self, amount: float, category_codename: str, user_id: int = None, username: str = None) -> bool:
        """Adding an expense

        :param username: optional parameter username
        :param user_id: optional parameter user id
        :param amount: expense amount
        :param category_codename: expense category code
        :return: bool
        """
        if not user_id:
            user_id = self._get_user_id_by_username(username=username)
        try:
            with self.connection:
                self.cursor.execute(
                    "INSERT INTO expense (id, amount, created, category_codename)"
                    "VALUES (?, ?, datetime('now', 'localtime'), ?)",
                    (user_id, amount, category_codename))
            return True
        except IntegrityError as ex:
            logging.error(repr(ex))

        except Exception as ex:
            logging.error(repr(ex))

    def add_user(self, user_id: int, is_admin: bool, username: str, password: str) -> bool:
        """Adding a user to the database

        :param username: username
        :param password: password
        :param is_admin: bool
        :param user_id: user id
        :return: bool
        """
        try:
            with self.connection:
                password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
                self.cursor.execute(
                    "INSERT INTO users (id, is_admin, is_active, username, password, last_active)"
                    "SELECT ?, ?, ?, ?, ?, datetime('now', 'localtime')"
                    "WHERE NOT EXISTS(SELECT id FROM users WHERE id = ?)",
                    (user_id, is_admin, True, username, password_hash, user_id))

                if self.cursor.rowcount == 0:
                    raise ValueError(f"User with ID [{user_id}] already exists in the database")
                if is_admin:
                    logging.info(f'Add new admin [{user_id}]')
                elif not is_admin:
                    logging.info(f'Add new user [{user_id}]')
            return True
        except ValueError as ex:
            logging.warning(f'{ex}')
            return False

    def update_last_active(self, user_id: int) -> bool:
        """Update last user activity

        :param user_id: user id
        :return: bool
        """
        try:
            with self.connection:
                self.cursor.execute("UPDATE users "
                                    "SET last_active = datetime('now', 'localtime')"
                                    "WHERE id = ? AND EXISTS (SELECT id FROM users WHERE id = ?)",
                                    (user_id, user_id))
            return True
        except Exception as ex:
            logging.error(repr(ex))

    def _get_category_name_by_codename(self, codename: str) -> str:
        """Getting category name by codename

        :param codename: category codename
        :return: str category name
        """
        try:
            with self.connection:
                result = self.cursor.execute("SELECT name "
                                             "FROM categories "
                                             "WHERE codename = ?",
                                             (codename,))
                return result.fetchone()[0].title()
        except Exception as ex:
            logging.error(repr(ex))

    def _get_all_expenses(self, user_id: int, category: str = None) -> Generator:
        """Getting the sum of all user expenses
        :param category: category of expense
        :param user_id: user id
        :return: sum of all user expenses
        """
        categories = [_.codename for _ in self.get_categories()]

        if not category:
            for codename in categories:
                sum_of_expenses = self.cursor.execute("SELECT sum(amount), id "
                                                      "FROM expense "
                                                      "WHERE id = ? AND category_codename = ?",
                                                      (user_id, codename)).fetchall()[0][0]
                if not sum_of_expenses:
                    continue
                codename = self._get_category_name_by_codename(codename=codename)
                result = GetExpenses(category=codename, amount=sum_of_expenses)
                yield result
        else:
            sum_of_expenses = self.cursor.execute("SELECT sum(amount), id "
                                                  "FROM expense "
                                                  "WHERE id = ? AND category_codename = ?",
                                                  (user_id, category)).fetchall()[0][0]
            category = self._get_category_name_by_codename(codename=category)
            result = GetExpenses(category=category, amount=sum_of_expenses)
            yield result

    def _get_period_expenses(self, user_id: int, timedelta: str, category: str = None) -> Generator:
        """Get expenses for a specific period of time

        :param user_id: user id
        :param timedelta: period
        :param category: category of expense
        :return:
        """
        categories = [_.codename for _ in self.get_categories()]

        if not category:
            for codename in categories:
                period_expenses = self.cursor.execute("SELECT sum(amount) "
                                                      "FROM expense "
                                                      "WHERE id = ? AND category_codename = ? "
                                                      "AND created "
                                                      f"BETWEEN datetime('now', '{timedelta}') "
                                                      "AND datetime('now', 'localtime')",
                                                      (user_id, codename)).fetchall()[0][0]
                if not period_expenses:
                    continue
                codename = self._get_category_name_by_codename(codename=codename)
                result = GetExpenses(category=codename, amount=period_expenses)
                yield result
        else:
            period_expenses = self.cursor.execute("SELECT sum(amount) "
                                                  "FROM expense "
                                                  "WHERE id = ? "
                                                  "AND category_codename = ? "
                                                  "AND created "
                                                  f"BETWEEN datetime('now', '{timedelta}') "
                                                  "AND datetime('now', 'localtime')",
                                                  (user_id, category))
            yield period_expenses.fetchall()[0][0]

    def get_sum_of_expenses(self, user_id: int = None, category: str = None, timedelta: str = None,
                            username: str = None) -> Generator:
        """Getting user expenses

        :param username: optional parameter username
        :param timedelta: period
        :param category: category of expense
        :param user_id: user id
        :return: sum of all user expenses
        """
        if not user_id and username:
            user_id = self._get_user_id_by_username(username=username)
        try:
            with self.connection:
                if not timedelta:
                    sum_of_expenses = self._get_all_expenses(user_id, category)
                    return sum_of_expenses

                elif timedelta == 'month':
                    result = self._get_period_expenses(user_id=user_id, timedelta='start of month', category=category)
                    return result

                elif timedelta == 'week':
                    result = self._get_period_expenses(user_id=user_id, timedelta='-6 days', category=category)
                    return result

                elif timedelta == 'day':
                    result = self._get_period_expenses(user_id=user_id, timedelta='start of day', category=category)
                    return result

        except Exception as ex:
            logging.error(repr(ex))

    @staticmethod
    def delete_db(db_file: str):
        """Deleting a database

        :return: None
        """
        if os.path.exists(db_file):
            os.remove(db_file)
            logging.warning("The database file has been deleted.")
        else:
            logging.warning("Database file not found.")
