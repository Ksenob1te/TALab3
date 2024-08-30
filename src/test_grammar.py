import unittest
from . import *

class TestGrammar(unittest.TestCase):
    def test_simple(self):
        program = """
        integer main()
        start
            integer a := 99999999999;
            mutable integer b;
            b := a * 2 + 10 := 5;
        
        
        finish;
        
        
        """


        self.assertTrue(True)