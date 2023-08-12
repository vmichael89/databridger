import unittest
from unittest.mock import patch, Mock
from databridger.database import Database


class TestDatabase(unittest.TestCase):

    def setUp(self):
        # This will run before every test
        # Here you can set up things that are required for the testing environment
        pass

    def tearDown(self):
        # This will run after every test
        # Useful for cleanup actions
        pass

    @patch("databridger.database.psycopg2.connect")
    def test_database_initialization(self, mock_connect):
        # Test if the Database class initializes without errors
        mock_connect.return_value = Mock()
        db = Database()
        self.assertIsInstance(db, Database)

    @patch("databridger.database.psycopg2.connect")
    def test_query_execution(self, mock_connect):
        # Test if a query executes without error and returns expected result
        mock_connect.return_value = Mock()
        mock_connect.return_value.cursor.return_value.fetchall.return_value = [("test",)]
        mock_connect.return_value.cursor.return_value.description = [
            (None, None, None, None, None, None, "test_column")]

        db = Database()
        result = db.query("SELECT 'test'")

        expected_result = pd.DataFrame([("test",)], columns=["test_column"])
        pd.testing.assert_frame_equal(result, expected_result)

    # ... Add more tests for other methods and edge cases ...


if __name__ == '__main__':
    unittest.main()
