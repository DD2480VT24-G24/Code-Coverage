import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from pytensor.utils import flatten


class TestUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.coverage = {f"branch_{i}": False for i in range(3)}

    @classmethod
    def tearDownClass(cls):
        print(cls.coverage)

    def test_flatten_empty_list(self):
        # Test when input is an empty list
        input_list = []
        expected_output = []
        self.assertEqual(flatten(input_list, self.coverage), expected_output)

    def test_flatten_single_element(self):
        # Test when input is a single element
        input_list = [1]
        expected_output = [1]
        self.assertEqual(flatten(input_list, self.coverage), expected_output)

    def test_flatten_nested_list(self):
        # Test when input is a nested list
        input_list = [[1, 2], [3, [4, 5]], 6]
        expected_output = [1, 2, 3, 4, 5, 6]
        self.assertEqual(flatten(input_list, self.coverage), expected_output)

    def test_flatten_nested_tuple(self):
        # Test when input is a nested tuple
        input_tuple = ((1, 2), (3, (4, 5)), 6)
        expected_output = [1, 2, 3, 4, 5, 6]
        self.assertEqual(flatten(input_tuple, self.coverage), expected_output)

    def test_flatten_invalid_input(self):
        input_list = 1
        expected_output = [1]
        self.assertEqual(flatten(input_list, self.coverage), expected_output)


if __name__ == '__main__':
    unittest.main()
