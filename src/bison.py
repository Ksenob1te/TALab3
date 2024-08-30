import builtins
import logging
from .classes.storage import *
from .classes.function import Function
from .methods import methods

from bison import BisonParser
from six.moves import input

logging.basicConfig(level=logging.INFO, filename="logger.log",
                    format=f"%(asctime)s %(levelname)s %(message)s")

from .general import *

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
            if callable(value) and value != FunctionType:
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
        'TOP', 'BOTTOM', 'LEFT', 'RIGHT', 'TIMESHIFT', 'BIND',
        'START', 'FINISH', 'WHILE', 'INSTEAD', 'BREAK', 'CHECKZERO', 'CALL', 'WITH', 'COMMA', 'RETURN',
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
        ('right', ('LBRACKET', 'RBRACKET'))
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

    start = "global_thread"

    def on_global_thread(self, target, option, names, values):
        """
        global_thread :
                      | global_thread function_init
        """
        self.check_exceptions(values)
        print(target, option, names, values)
        if option != 0:
            if values[0] is not False:
                return values[0] + [values[1]]
            return [values[1]]
        else:
            return False

    def on_function_init(self, target, option, names, values):
        """
        function_init : str_or_int IDENTIFIER LPAREN func_params RPAREN group
                      | POINTER IDENTIFIER LPAREN func_params RPAREN group
                      | ARRAY IDENTIFIER LPAREN func_params RPAREN group
        """
        print(target, option, names, values)
        kwargs = {
            "name": values[1],
            "type": FunctionType,
            "value": values[5],
            "value_type": values[0],
            "parameters": values[3]
        }
        return CommitedOperation(init_variable, **kwargs)

    def on_func_params(self, target, option, names, values):
        """
        func_params :
                    | var_type IDENTIFIER
                    | func_params COMMA var_type IDENTIFIER
        """
        print(target, option, names, values)
        transform_dict = {"string": String, "integer": Integer, "pointer": Pointer, "array of": Array}
        if option == 0:
            return []
        elif option == 2:
            return values[0] + [(values[3], transform_dict[values[2]])]
        elif option == 1:
            return [(values[1], transform_dict[values[0]])]

    def on_group(self, target, option, names, values):
        """
        group : START set FINISH SEM
        """
        print(target, option, names, values)
        return values[1]

    def on_set(self, target, option, names, values):
        """
        set :
            | set operation
        """
        print(target, option, names, values)
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
                  | function_init
        """
        self.check_exceptions(values)
        print(target, option, names, values)
        return values[0]

    # def on_main(self, target, option, names, values):
    #     """
    #     main :
    #          | main operation
    #     """
    #     if option != 0:
    #         if values[0] is not False:
    #             return values[0] + [values[1]]
    #         return [values[1]]
    #     else:
    #         return False

    def on_checkzero(self, target, option, names, values):
        """
        checkzero : CHECKZERO paren group
                  | CHECKZERO paren operation
                  | CHECKZERO paren group instead
                  | CHECKZERO paren operation instead
        """
        print(target, option, names, values)
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
        while : WHILE paren group
              | WHILE paren operation
              | WHILE paren group instead
              | WHILE paren operation instead
        """
        print(target, option, names, values)
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
        print(target, option, names, values)
        if option == 0:
            return values[1]
        else:
            return [values[1]]


    def on_command(self, target, option, names, values):
        """
        command : var_init SEM
                | var_assign SEM
                | array_assign SEM
                | deref_assign SEM
                | var_append SEM
                | return SEM
                | BREAK SEM
                | TIMESHIFT exp SEM
                | BIND exp SEM
                | TOP SEM
                | BOTTOM SEM
                | LEFT SEM
                | RIGHT SEM
                | function_call SEM
        """
        print(target, option, names, values)
        if option == 6:
            return CommitedOperation(Break)
        elif option == 7:
            return CommitedOperation(methods._timeshift, values[1])
        elif option == 8:
            return CommitedOperation(methods._bind, values[1])
        elif option == 9:
            return CommitedOperation(methods._top)
        elif option == 10:
            return CommitedOperation(methods._bottom)
        elif option == 11:
            return CommitedOperation(methods._left)
        elif option == 12:
            return CommitedOperation(methods._right)
        else:
            self.check_exceptions(values)
            return values[0]

    def on_return(self, target, option, names, values):
        """
        return : RETURN exp
        """
        print(target, option, names, values)
        return CommitedOperation(Result, values[1])

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
        print(target, option, names, values)
        return values[0]

    def on_pointer_init(self, target, option, names, values):
        """
        pointer_init : MUTABLE POINTER MUTABLE type_exp IDENTIFIER EQUALS exp
                     | MUTABLE POINTER type_exp IDENTIFIER EQUALS exp
                     | MUTABLE POINTER MUTABLE type_exp IDENTIFIER
                     | MUTABLE POINTER type_exp IDENTIFIER
                     | MUTABLE POINTER MUTABLE IDENTIFIER EQUALS exp
                     | MUTABLE POINTER IDENTIFIER EQUALS exp
                     | POINTER MUTABLE type_exp IDENTIFIER EQUALS exp
                     | POINTER type_exp IDENTIFIER EQUALS exp
                     | POINTER MUTABLE type_exp IDENTIFIER
                     | POINTER type_exp IDENTIFIER
                     | POINTER MUTABLE IDENTIFIER EQUALS exp
                     | POINTER IDENTIFIER EQUALS exp
        """
        res = {"type": "pointer", "is_const": False, "is_value_const": False, "name": None, "value_type": None, "value": None}
        if option not in [0, 1, 2, 3, 4, 5]:
            res["is_const"] = True
        if option in [0, 2, 4, 6, 8, 10]:
            res["is_value_const"] = True
        if option in [0, 1, 4, 5, 6, 7, 10, 11]:
            res["value"] = values[-1]
        if option == 0:
            res["name"] = values[4]
            res["value_type"] = values[3]
        elif option == 1:
            res["name"] = values[3]
            res["value_type"] = values[2]
        elif option == 2:
            res["name"] = values[4]
            res["value_type"] = values[3]
        elif option == 3:
            res["name"] = values[3]
            res["value_type"] = values[2]
        elif option == 4:
            res["name"] = values[3]
        elif option == 5:
            res["name"] = values[2]
        elif option == 6:
            res["name"] = values[3]
            res["value_type"] = values[2]
        elif option == 7:
            res["name"] = values[2]
            res["value_type"] = values[1]
        elif option == 8:
            res["name"] = values[3]
            res["value_type"] = values[2]
        elif option == 9:
            res["name"] = values[2]
            res["value_type"] = values[1]
        elif option == 10:
            res["name"] = values[2]
        else:
            res["name"] = values[1]

        return CommitedOperation(init_variable, **res)

    # def on_pointer_init_1(self, target, option, names, values):
    #     """
    #     pointer_init_1 : POINTER is_mutable type_exp IDENTIFIER
    #                    | POINTER is_mutable IDENTIFIER
    #     """
    #     res = {"type": "pointer", "is_value_const": values[1], "name": values[-1]}
    #     if option == 0:
    #         res["value_type"] = values[2]
    #     return res

    # def on_is_mutable(self, target, option, names, values):
    #     """
    #     is_mutable :
    #                | MUTABLE
    #     """
    #     print(target, option, names, values)
    #     return option == 1

    def on_array_init(self, target, option, names, values):
        """
        array_init : MUTABLE ARRAY type_exp IDENTIFIER
                   | MUTABLE ARRAY type_exp IDENTIFIER LBRACKET exp RBRACKET
                   | ARRAY type_exp IDENTIFIER LBRACKET exp RBRACKET
        """
        print(target, option, names, values)
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
        print(target, option, names, values)
        return CommitedOperation(methods._setattr, values[0], "value", values[2])

    def on_deref_assign(self, target, option, names, values):
        """
        deref_assign : TIMES IDENTIFIER EQUALS exp
                     | TIMES IDENTIFIER EQUALS var_assign
                     | TIMES IDENTIFIER EQUALS array_assign
                     | TIMES IDENTIFIER EQUALS deref_assign
        """
        self.check_exceptions(values)
        print(target, option, names, values)
        ref = CommitedOperation(lambda name: global_storage[name], values[1])
        deref = CommitedOperation(methods._dereference, ref, True)
        return CommitedOperation(methods._setattr, deref, "value", values[3])


    def on_var_type(self, target, option, names, values):
        """
        var_type : str_or_int
                 | POINTER
                 | ARRAY
        """
        return values[0]

    def on_type_exp(self, target, option, names, values):
        """
        type_exp : INTEGER | STRING | POINTER | ARRAY | exp
        """
        name_list = ["integer", "string", "pointer", "array of"]
        print(target, option, names, values)
        current = values[0]
        if callable(current):
            current = current()
        if current not in name_list:
            current = type(current)
        return current

    def on_var_append(self, target, option, names, values):
        """
        var_append : IDENTIFIER APPEND paren
        """
        self.check_exceptions(values)
        print(target, option, names, values)
        current = CommitedOperation(lambda name: global_storage[name], values[0])
        return CommitedOperation(methods._append, current, values[2])

    def on_exp(self, target, option, names, values):
        """
        exp : number
            | str
            | paren
            | ref
            | deref
            | plus
            | minus
            | times
            | div
            | mod
            | var
            | array_el
            | size
            | op_equal
            | op_greater
            | op_less
            | function_call
            | TOP
            | BOTTOM
            | LEFT
            | RIGHT
        """
        print(target, option, names, values)
        if option == 17:
            return CommitedOperation(lambda: methods._top)
        elif option == 18:
            return CommitedOperation(lambda: methods._bottom)
        elif option == 19:
            return CommitedOperation(lambda: methods._left)
        elif option == 20:
            return CommitedOperation(lambda: methods._right)
        else:
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

    def on_plus(self, target, option, names, values):
        """
        plus : exp PLUS exp
        """
        return CommitedOperation(lambda a, b: a + b, values[0], values[2])

    def on_minus(self, target, option, names, values):
        """
        minus : exp MINUS exp
        """
        return CommitedOperation(lambda a, b: a - b, values[0], values[2])

    def on_times(self, target, option, names, values):
        """
        times : exp TIMES exp
        """
        return CommitedOperation(lambda a, b: a * b, values[0], values[2])

    def on_div(self, target, option, names, values):
        """
        div : exp DIVIDE exp
        """
        return CommitedOperation(lambda a, b: a / b, values[0], values[2])

    def on_mod(self, target, option, names, values):
        """
        mod : exp MOD exp
        """
        return CommitedOperation(lambda a, b: a % b, values[0], values[2])

    def on_var(self, target, option, names, values):
        """
        var : IDENTIFIER
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

    def on_paren(self, target, option, names, values):
        """
        paren : LPAREN exp RPAREN
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

    def on_function_call(self, target, option, names, values):
        """
        function_call : CALL exp
                      | CALL exp WITH function_call_params
        """
        # var = CommitedOperation(lambda name: global_storage[name], )
        if option == 1:
            return CommitedOperation(methods._function_call, func_var=values[1], parameters=values[3])
        else:
            return CommitedOperation(methods._function_call, func_var=values[1], parameters=[])

    def on_function_call_params(self, target, option, names, values):
        """
        function_call_params :
                             | exp
                             | function_call_params COMMA exp
        """
        if option == 0:
            return []
        elif option == 1:
            return [values[0]]
        else:
            return values[0] + [values[2]]

    # -----------------------------------------
    # raw lex script, verbatim here
    # -----------------------------------------
    with open("./src/grammar/recognizer.l", "r") as lexer:
        lex_read = lexer.read()
    lexscript = lex_read
