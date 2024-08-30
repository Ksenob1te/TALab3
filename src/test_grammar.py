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

        program = """
                integer main()
                start
                    integer a := "hello";
                    return 0;
                finish;        
                """
        with open("temp.help", "w") as f:
            f.write(program)
        with self.assertRaises(ValueError):
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

    def test_init_array(self):
        program = """
                integer main()
                start
                    array of integer a;
                    array of integer b[5];
                    mutable array of integer c[10];
                    return 0;
                finish;
                """
        with open("temp.help", "w") as f:
            f.write(program)
        compiled = methods._function_call(compile_script("temp.help"), parameters=[])
        self.assertEqual(int(compiled), 0)

        program = """
                integer main()
                start
                    mutable array of integer c;
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
                    array of integer b[5];
                    b[0] := 0;
                    b[1] := 1;
                    b[2] := 2;
                    b[3] := 3;
                    b[4] := 4;
                    b.append(5);
                    return ?b;
                finish;
                """
        with open("temp.help", "w") as f:
            f.write(program)
        compiled = methods._function_call(compile_script("temp.help"), parameters=[])
        self.assertEqual(int(compiled), 10)

        program = """
                integer main()
                start
                    mutable array of integer b[5];
                    b.append(5);
                    return 0;
                finish;
                """
        with open("temp.help", "w") as f:
            f.write(program)

        with self.assertRaises(RuntimeError):
            methods._function_call(compile_script("temp.help"), parameters=[])

    def test_array_index(self):
        program = """
                integer main()
                start
                    array of integer b[5];
                    b[0] := 0;
                    b[1] := 1;
                    b[2] := 2;
                    b[3] := 3;
                    b[4] := 4;
                    return b[0] + b[1] + b[2] + b[3] + b[4];
                finish;
                """
        with open("temp.help", "w") as f:
            f.write(program)
        compiled = methods._function_call(compile_script("temp.help"), parameters=[])
        self.assertEqual(int(compiled), 10)

        program = """
                integer main()
                start
                    array of integer b[5];
                    return b[5];
                finish;
                """
        with open("temp.help", "w") as f:
            f.write(program)
        with self.assertRaises(RuntimeError):
            methods._function_call(compile_script("temp.help"), parameters=[])

        program = """
                integer main()
                start
                    string b = "hello";
                    return b[0];
                finish;
                """
        with open("temp.help", "w") as f:
            f.write(program)
        compiled = methods._function_call(compile_script("temp.help"), parameters=[])
        self.assertEqual(str(compiled), "h")

        program = """
                integer main()
                start
                    string b = "hello";
                    return b[5];
                finish;
                """
        with open("temp.help", "w") as f:
            f.write(program)

        with self.assertRaises(RuntimeError):
            methods._function_call(compile_script("temp.help"), parameters=[])

    def test_pointer_value(self):
        program = """
                integer main()
                start
                    integer num := 10;
                    mutable pointer integer a := &num;
                    return *a;
                finish;
                """
        with open("temp.help", "w") as f:
            f.write(program)
        compiled = methods._function_call(compile_script("temp.help"), parameters=[])
        self.assertEqual(int(compiled), 10)

        program = """
                integer main()
                start
                    integer num := 10;
                    pointer integer a := &num;
                    *a := 20;
                    return num;
                finish;
                """
        with open("temp.help", "w") as f:
            f.write(program)
        compiled = methods._function_call(compile_script("temp.help"), parameters=[])
        self.assertEqual(int(compiled), 20)

    def test_len_operator(self):
        program = """
                integer main()
                start
                    integer num := 10;
                    return ?num;
                finish;
                """
        with open("temp.help", "w") as f:
            f.write(program)
        compiled = methods._function_call(compile_script("temp.help"), parameters=[])
        self.assertEqual(int(compiled), 1)

        program = """
                integer main()
                start
                    array of integer num[5];
                    num.append(5);
                    return ?num;
                finish;
                """
        with open("temp.help", "w") as f:
            f.write(program)
        compiled = methods._function_call(compile_script("temp.help"), parameters=[])
        self.assertEqual(int(compiled), 10)

    def test_arithmetic(self):
        program = """
                integer main()
                start
                    integer a := 10;
                    integer b := 20;
                    mutable integer c;
                    c := b := a;
                    return b;
                finish;
                """
        with open("temp.help", "w") as f:
            f.write(program)

        compiled = methods._function_call(compile_script("temp.help"), parameters=[])
        self.assertEqual(int(compiled), 10)

    def test_while(self):
        program = """
                integer main()
                start
                    integer counter := 0;
                    array of integer a[1];
                    while (counter < 10)
                    start
                        a.append(counter);
                        counter := counter + 1;
                    finish;
                    return ?a;
                finish;
                """
        with open("temp.help", "w") as f:
            f.write(program)
        compiled = methods._function_call(compile_script("temp.help"), parameters=[])
        self.assertEqual(int(compiled), 11)

    # def test_checkzero(self):
    #     program = """
    #             integer main()
    #             start
    #                 integer counter := 0;
    #                 array of integer a[1];
    #                 while (counter < 10)
    #                 start
    #                     a.append(counter);
    #                     counter := counter + 1;
    #                 finish;
    #                 return ?a;
    #             finish;
    #             """
    #     with open("temp.help", "w") as f:
    #         f.write(program)
    #     compiled = methods._function_call(compile_script("temp.help"), parameters=[])
    #     self.assertEqual(int(compiled), 11)

    def test_recursive(self):
        program = """
                integer test()
                start
                    integer a := 10;
                    integer recursive()
                    start
                        checkzero (a)
                            return 0;
                        instead
                            a := a - 1;
                        call recursive;
                        return 0;
                    finish;
                    return call recursive;
                finish;
        
                integer main()
                start
                    return call test;
                finish;
                """
        with open("temp.help", "w") as f:
            f.write(program)
        compiled = methods._function_call(compile_script("temp.help"), parameters=[])
        self.assertEqual(int(compiled), 0)

    def test_fibonacci(self):
        program = """
                integer test(integer n)
                start
                    integer numf := 0;
                    integer nums := 1;
                    integer nextnumber := nums;
                    integer counter := 0;
                    mutable integer temp;
                    while (counter < n) start
                        counter := counter + 1;
                        temp := nums;
                        nums := nextnumber;
                        numf := temp;
                        nextnumber := numf + nums;
                    finish;
                    return nums;
                finish;

                integer main(integer n)
                start
                    return call test with n;
                finish;
                """
        with open("temp.help", "w") as f:
            f.write(program)
        compiled = methods._function_call(compile_script("temp.help"), parameters=[Integer(value=9)])
        self.assertEqual(int(compiled), 55)

