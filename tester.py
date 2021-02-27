import unittest

tests = unittest.TestLoader().discover("tests", pattern="*.py")
result = unittest.TextTestRunner(verbosity=2).run(tests)
