import unittest
from . import *

class TestGrammar(unittest.TestCase):
    def test_init_int(self):
        program = """
        integer main()
        start
            integer a := 99999999999;
            mutable integer b;
            b := a * 2 + 10;
            b := 1 + a;
            return b;
        finish;        
        """
        with open("temp.help", "w") as f:
            f.write(program)
        compiled = methods._function_call(compile_script("temp.help"), parameters=[])
        self.assertEqual(int(compiled), 99999999999 + 1)

        program = """
                integer main()
                start
                    integer a;
                    return 0;
                finish;        
                """
        with open("temp.help", "w") as f:
            f.write(program)
        with self.assertRaises(RuntimeError):
            methods._function_call(compile_script("temp.help"), parameters=[])


    def test_init_str(self):
        program = """
                string main()
                start
                    string a := "hel" + "lo";
                    mutable string b;
                    b := a + " world";
                    return b;
                finish;        
                """
        with open("temp.help", "w") as f:
            f.write(program)
        compiled = methods._function_call(compile_script("temp.help"), parameters=[])
        self.assertEqual(str(compiled), "hello world")

        program = """
                integer main()
                start
                    string a;
                    return 0;
                finish;        
                """
        with open("temp.help", "w") as f:
            f.write(program)
        with self.assertRaises(RuntimeError):
            methods._function_call(compile_script("temp.help"), parameters=[])

    def test_init_pointer(self):
        program = """
                integer main()
                start
                    integer num := 10;
                    mutable pointer integer a;
                    mutable pointer integer b := &num;
                    a := b;
                    *a := 20;
                    pointer c := b;

                    return *b;
                finish;
                """
        with open("temp.help", "w") as f:
            f.write(program)
        compiled = methods._function_call(compile_script("temp.help"), parameters=[])
        self.assertEqual(int(compiled), 20)

        program = """
                integer main()
                start
                    pointer a;
                    return 0;
                finish;
                """
        with open("temp.help", "w") as f:
            f.write(program)
        with self.assertRaises(RuntimeError):
            methods._function_call(compile_script("temp.help"), parameters=[])

        program = """
                integer main()
                start
                    integer numf := 10;
                    integer nums := 20;
                    pointer a := &numf;
                    a := &nums;
                    return 0;
                finish;
                """
        with open("temp.help", "w") as f:
            f.write(program)
        with self.assertRaises(ValueError):
            methods._function_call(compile_script("temp.help"), parameters=[])

        program = """
                integer main()
                start
                    integer numf := 10;
                    integer nums := 20;
                    mutable pointer mutable a := &numf;
                    *a := nums;
                    return 0;
                finish;
                """
        with open("temp.help", "w") as f:
            f.write(program)
        with self.assertRaises(ValueError):
            methods._function_call(compile_script("temp.help"), parameters=[])

        program = """
                integer main()
                start
                    mutable array of integer numf[2];
                    numf[0] := 10;
                    numf[1] := 20;
                    mutable pointer a := &numf;
                    mutable pointer b := a + 1;
                    return *b;
                finish;
                """
        with open("temp.help", "w") as f:
            f.write(program)
        compiled = methods._function_call(compile_script("temp.help"), parameters=[])
        self.assertEqual(int(compiled), 20)

        program = """
                integer main()
                start
                    mutable array of integer numf[2];
                    numf[0] := 10;
                    numf[1] := 20;
                    mutable pointer a := &numf;
                    mutable pointer string b := a + 1;
                    return *b;
                finish;
                """
        with open("temp.help", "w") as f:
            f.write(program)
        with self.assertRaises(ValueError):
            methods._function_call(compile_script("temp.help"), parameters=[])
