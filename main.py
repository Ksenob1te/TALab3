import logging
import math
import sys
from src.classes.storage import *
from src.methods import methods

from bison import BisonParser
from six.moves import input

logging.basicConfig(level=logging.INFO, filename="logger.log",
                    format=f"%(asctime)s %(levelname)s %(message)s")

from src.general import *

class CommitedOperation:
    func = None
    args = None
    non_wrap_funcs = [methods._while, methods._if]

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.kwargs = kwargs
        self.args = args

    def __call__(self):
        if self.func in self.non_wrap_funcs:
            return self.func(*self.args, **self.kwargs)
        result_args = []
        for arg in self.args:
            if callable(arg):
                result_args.append(arg())
            else:
                result_args.append(arg)
        new_kwargs = {}
        for key, value in self.kwargs.items():
            if callable(value):
                new_kwargs[key] = value()
            else:
                new_kwargs[key] = value
        return self.func(*result_args, **new_kwargs)


class Parser(BisonParser):
    # ------------------------------
    # bison parser rules
    # ------------------------------
    options = [
        "%define api.pure full",
        "%define api.push-pull push",
        "%lex-param {yyscan_t scanner}",
        "%parse-param {yyscan_t scanner}",
        "%define api.value.type {void *}",
    ]

    # ----------------------------------------------------------------
    # lexer tokens - these must match those in your lex script (below)
    # ----------------------------------------------------------------
    tokens = [
        'START', 'FINISH', 'WHILE', 'INSTEAD', 'BREAK', 'CHECKZERO',
        'NUMBER', 'STR',
        'INTEGER', 'STRING', 'POINTER', 'ARRAY', 'MUTABLE',
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD', 'SEM', "REF", 'APPEND',
        'LPAREN', 'RPAREN',
        'LBRACKET', 'RBRACKET',
        'EQUALS', "SIZE", 'OP_EQUAL', 'OP_GREATER', 'OP_LESS',
        'IDENTIFIER',
        'HELP',

    ]

    # ------------------------------
    # precedences
    # ------------------------------
    precedences = (
        ('left', ('OP_EQUAL', 'OP_GREATER', 'OP_LESS')),
        ('left', ('MINUS', 'PLUS')),
        ('left', ('TIMES', 'DIVIDE', 'MOD')),
    )

    # --------------------------------------------
    # basename of binary parser engine dynamic lib
    # --------------------------------------------
    bisonEngineLibName = "calc1-engine"

    @staticmethod
    def check_exceptions(values):
        for v in values:
            if isinstance(v, Exception):
                raise v

    start = "main"

    # TODO: break

    def on_function(self, target, option, names, values):
        """
        function :
        """
        print("HELP")
        print(global_storage)
        return False

    def on_main(self, target, option, names, values):
        """
        main :
             | main operation
        """
        if option != 0:
            if values[0] is not False:
                return values[0] + [values[1]]
            return [values[1]]
        else:
            return False

    def on_checkzero(self, target, option, names, values):
        """
        checkzero : CHECKZERO parenexp group
                  | CHECKZERO parenexp operation
                  | CHECKZERO parenexp group instead
                  | CHECKZERO parenexp operation instead
        """
        self.check_exceptions(values)
        if option == 0:
            return CommitedOperation(methods._if, values[1], values[2])
        elif option == 1:
            return CommitedOperation(methods._if, values[1], [values[2]])
        elif option == 2:
            return CommitedOperation(methods._if, values[1], values[2], values[3])
        else:
            return CommitedOperation(methods._if, values[1], [values[2]], values[3])


    def on_while(self, target, option, names, values):
        """
        while : WHILE parenexp group
              | WHILE parenexp operation
              | WHILE parenexp group instead
              | WHILE parenexp operation instead
        """
        self.check_exceptions(values)
        if option == 0:
            return CommitedOperation(methods._while, values[1], values[2])
        elif option == 1:
            return CommitedOperation(methods._while, values[1], [values[2]])
        elif option == 2:
            return CommitedOperation(methods._while, values[1], values[2], values[3])
        else:
            return CommitedOperation(methods._while, values[1], [values[2]], values[3])


    def on_instead(self, target, option, names, values):
        """
        instead : INSTEAD group
                | INSTEAD operation
        """
        if option == 0:
            return values[1]
        else:
            return [values[1]]


    def on_group(self, target, option, names, values):
        """
        group : START set FINISH SEM
        """
        return values[1]

    def on_set(self, target, option, names, values):
        """
        set :
            | set operation
        """
        self.check_exceptions(values)
        if option == 1:
            if values[0] is not False:
                return values[0] + [values[1]]
            return [values[1]]
        else:
            return False

    def on_operation(self, target, option, names, values):
        """
        operation : command
                  | while
                  | checkzero
        """
        self.check_exceptions(values)
        print(target, option, names, values)
        return values[0]


    def on_command(self, target, option, names, values):
        """
        command : var_init SEM
                | var_assign SEM
                | array_assign SEM
                | deref_assign SEM
                | var_append SEM
                | BREAK SEM
        """
        if option == 5:
            return CommitedOperation(Break)
        print(target, option, names, values)
        self.check_exceptions(values)
        return values[0]

    def on_var_init(self, target, option, names, values):
        """
        var_init : int_str_init
                 | pointer_init
                 | array_init
        """
        print(target, option, names, values)
        self.check_exceptions(values)
        return values[0]

    def on_int_str_init(self, target, option, names, values):
        """
        int_str_init : MUTABLE str_or_int IDENTIFIER
                     | str_or_int IDENTIFIER EQUALS exp
                     | MUTABLE str_or_int IDENTIFIER EQUALS exp
        """
        self.check_exceptions(values)
        print(target, option, names, values)

        if option == 0:
            return CommitedOperation(init_variable, type=values[1], name=values[2])
        elif option == 1:
            return CommitedOperation(init_variable, type=values[0], name=values[1], value=values[3])
        elif option == 2:
            return CommitedOperation(init_variable, type=values[1], name=values[2], value=values[4])

    def on_str_or_int(self, target, option, names, values):
        """
        str_or_int : INTEGER
                   | STRING
        """
        return values[0]

    def on_pointer_init(self, target, option, names, values):
        """
        pointer_init : MUTABLE POINTER is_mutable type_exp IDENTIFIER
                     | MUTABLE pointer_init_1 EQUALS exp
                     | pointer_init_1 EQUALS exp
        """
        print(target, option, names, values)
        if option == 0:
            res = {"type": "pointer", "is_const": False,
                   "is_value_const": values[2], "name": values[4], "value_type": values[3]}
        elif option == 1:
            res = values[1]
            res["is_const"] = False
            res["value"] = values[-1]
        else:
            res = values[0]
            res["is_const"] = True
            res["value"] = values[-1]
        return CommitedOperation(init_variable, **res)

    def on_pointer_init_1(self, target, option, names, values):
        """
        pointer_init_1 : POINTER is_mutable type_exp IDENTIFIER
                       | POINTER is_mutable IDENTIFIER
        """
        res = {"type": "pointer", "is_value_const": values[1], "name": values[-1]}
        if option == 0:
            res["value_type"] = values[2]
        return res

    def on_is_mutable(self, target, option, names, values):
        """
        is_mutable :
                   | MUTABLE
        """
        return option == 1

    def on_array_init(self, target, option, names, values):
        """
        array_init : MUTABLE ARRAY type_exp IDENTIFIER
                   | MUTABLE ARRAY type_exp IDENTIFIER LBRACKET exp RBRACKET
                   | ARRAY type_exp IDENTIFIER LBRACKET exp RBRACKET
        """
        if option == 0:
            return CommitedOperation(init_variable, type=values[1], name=values[3], is_static=True, value_type=values[2])
        elif option == 1:
            return CommitedOperation(init_variable, type=values[1], name=values[3], is_static=True, value_type=values[2], size=values[5])
        else:
            return CommitedOperation(init_variable, type=values[0], name=values[2], is_static=False, value_type=values[1], size=values[4])


    def on_var_assign(self, target, option, names, values):
        """
        var_assign : IDENTIFIER EQUALS exp
                   | IDENTIFIER EQUALS var_assign
                   | IDENTIFIER EQUALS array_assign
                   | IDENTIFIER EQUALS deref_assign
        """
        self.check_exceptions(values)
        print(target, option, names, values)
        cur = CommitedOperation(lambda name: global_storage[name], values[0])
        return CommitedOperation(methods._setattr, cur, "value", values[2])

    def on_array_assign(self, target, option, names, values):
        """
        array_assign : array_el EQUALS exp
                     | array_el EQUALS var_assign
                     | array_el EQUALS array_assign
                     | array_el EQUALS deref_assign
        """
        self.check_exceptions(values)
        return CommitedOperation(methods._setattr, values[0], "value", values[2])

    def on_deref_assign(self, target, option, names, values):
        """
        deref_assign : TIMES IDENTIFIER EQUALS exp
                     | TIMES IDENTIFIER EQUALS var_assign
                     | TIMES IDENTIFIER EQUALS array_assign
                     | TIMES IDENTIFIER EQUALS deref_assign
        """
        self.check_exceptions(values)
        ref = CommitedOperation(lambda name: global_storage[name], values[1])
        deref = CommitedOperation(methods._dereference, ref, True)
        return CommitedOperation(methods._setattr, deref, "value", values[3])


    def on_var_type(self, target, option, names, values):
        """
        VAR_TYPE : INTEGER
                 | STRING
                 | POINTER
                 | ARRAY
        """
        return values[0]

    def on_type_exp(self, target, option, names, values):
        """
        type_exp : INTEGER | STRING | POINTER | ARRAY | exp
        """
        name_list = ["integer", "string", "pointer", "array of"]
        current = values[0]
        if callable(current):
            current = current()
        if current not in name_list:
            current = type(current)
        return current

    def on_var_append(self, target, option, names, values):
        """
        var_append : IDENTIFIER APPEND parenexp
        """
        self.check_exceptions(values)
        current = CommitedOperation(lambda name: global_storage[name], values[0])
        return CommitedOperation(methods._append, current, values[2])

    def on_exp(self, target, option, names, values):
        """
        exp : number
            | str
            | parenexp
            | ref
            | deref
            | plusexp
            | minusexp
            | timesexp
            | divexp
            | modexp
            | varexp
            | array_el
            | size
            | op_equal
            | op_greater
            | op_less
        """
        self.check_exceptions(values)
        return values[0]

    def on_number(self, target, option, names, values):
        """
        number : NUMBER
        """
        return CommitedOperation(Integer, value=int(values[0]))

    def on_str(self, target, option, names, values):
        """
        str : STR
        """
        return CommitedOperation(String, value=values[0][1:-1])

    def on_plusexp(self, target, option, names, values):
        """
        plusexp : exp PLUS exp
        """
        return CommitedOperation(lambda a, b: a + b, values[0], values[2])

    def on_minusexp(self, target, option, names, values):
        """
        minusexp : exp MINUS exp
        """
        return CommitedOperation(lambda a, b: a - b, values[0], values[2])

    def on_timesexp(self, target, option, names, values):
        """
        timesexp : exp TIMES exp
        """
        return CommitedOperation(lambda a, b: a * b, values[0], values[2])

    def on_divexp(self, target, option, names, values):
        """
        divexp : exp DIVIDE exp
        """
        return CommitedOperation(lambda a, b: a / b, values[0], values[2])

    def on_modexp(self, target, option, names, values):
        """
        modexp : exp MOD exp
        """
        return CommitedOperation(lambda a, b: a % b, values[0], values[2])

    def on_varexp(self, target, option, names, values):
        """
        varexp : IDENTIFIER
        """
        return CommitedOperation(lambda name: global_storage[name], values[0])

    def on_array_el(self, target, option, names, values):
        """
        array_el : IDENTIFIER LBRACKET exp RBRACKET
        """
        get_el = CommitedOperation(lambda name: global_storage[name], values[0])
        return CommitedOperation(methods._getitem, get_el, values[2])

    def on_ref(self, target, option, names, values):
        """
        ref : REF exp
        """
        # ref = CommitedOperation(lambda name: global_storage[name], values[1])
        return CommitedOperation(Pointer.create_ref, value=values[1])

    def on_deref(self, target, option, names, values):
        """
        deref : TIMES exp
        """
        # ref = CommitedOperation(lambda name: global_storage[name], values[1])
        return CommitedOperation(methods._dereference, values[1])

    def on_size(self, target, option, names, values):
        """
        size : SIZE exp
        """
        return CommitedOperation(methods._size, values[1])

    def on_parenexp(self, target, option, names, values):
        """
        parenexp : LPAREN exp RPAREN
        """
        return values[1]

    def on_op_equal(self, target, option, names, values):
        """
        op_equal : exp OP_EQUAL exp
        """
        return CommitedOperation(lambda a, b: a == b, values[0], values[2])

    def on_op_greater(self, target, option, names, values):
        """
        op_greater : exp OP_GREATER exp
        """
        return CommitedOperation(lambda a, b: a > b, values[0], values[2])

    def on_op_less(self, target, option, names, values):
        """
        op_less : exp OP_LESS exp
        """
        return CommitedOperation(lambda a, b: a < b, values[0], values[2])

    # -----------------------------------------
    # raw lex script, verbatim here
    # -----------------------------------------
    with open("./src/grammar/recognizer.l", "r") as lexer:
        lex_read = lexer.read()
    lexscript = lex_read


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog="PyBison CALC1 Example")
    parser.add_argument("-k", "--keepfiles", action="store_true",
                        help="Keep temporary files used in building parse engine lib")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose messages while parser is running")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Enable garrulous debug messages from parser engine")
    args = parser.parse_args()

    p = Parser(keepfiles=args.keepfiles, verbose=args.verbose)
    print("IM WORKING")

    with open('./test.help', 'r') as content_file:
        content = content_file.read()
    r = p.parse_string(content, debug=False)
    print(r)
    if isinstance(r, Exception):
        raise r
    if r is False:
        raise ValueError("Error in parsing")
    for statement in r:
        statement()
    print(global_storage["abc"].value)
    # print(global_storage["c"].value)
