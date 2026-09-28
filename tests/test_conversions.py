import unittest


class MyTestCase(unittest.TestCase):
    def test_conversions(self):

        self.assertEqual(self.microseconds_to_seconds(1000.0), 0.001)
        self.assertEqual(self.nanoseconds_to_seconds(1000000.0), 0.001)

    def microseconds_to_seconds(self, microseconds: float) -> float:
        return microseconds * 1e-6

    def nanoseconds_to_seconds(self, nanoseconds: float) -> float:
        return nanoseconds * 1e-9

if __name__ == '__main__':
    unittest.main()
