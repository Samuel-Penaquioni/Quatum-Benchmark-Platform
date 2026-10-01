import unittest
from benchmark import microseconds_to_seconds, nanoseconds_to_seconds


class TestConversions(unittest.TestCase):
    def test_conversions(self):

        self.assertEqual(microseconds_to_seconds(1000.0), 0.001)
        self.assertEqual(nanoseconds_to_seconds(1000000.0), 0.001)


if __name__ == '__main__':
    unittest.main()
