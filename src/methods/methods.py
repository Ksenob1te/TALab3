from ..classes import *
from ..robot import global_robot

def _setattr(target, name, value):
    if callable(target):
        target = target()
    if callable(name):
        name = name()
    if callable(value):
        value = value()
    value = value.__copy__()
    return target.__setattr__(name, value)

def _getitem(target, item):
    if callable(target):
        target = target()
    if callable(item):
        item = item()
    return target[item]

def _size(target):
    if callable(target):
        target = target()
    return target.size()

def _dereference(target, is_assign: bool = False):
    if callable(target):
        target = target()
    return target.dereference(is_writing=is_assign)

def _append(target, value):
    if callable(target):
        target = target()
    if callable(value):
        value = value()
    return target.append(value)

def _while(condition, body, instead = None):
    was_iterated = False
    marker = Integer(value=0)
    while not (condition() == marker):
        was_iterated = True
        for statement in body:
            break_check = statement()
            if isinstance(break_check, Break):
                return
            if isinstance(break_check, Result):
                return break_check
    if not was_iterated and instead is not None:
        for statement in instead:
            statement()
    return None

def _if(condition, body, instead = None):
    res = condition() if callable(condition) else condition
    marker = Integer(value=0)
    if res == marker:
        for statement in body:
            break_check = statement()
            if isinstance(break_check, Break):
                return Break()
            if isinstance(break_check, Result):
                return break_check
    else:
        if instead is not None:
            for statement in instead:
                break_check = statement()
                if isinstance(break_check, Break):
                    return Break()
                if isinstance(break_check, Result):
                    return break_check
    return None

def _function_call(func_var, parameters):
    if callable(func_var):
        func_var = func_var()
    for i in range(len(parameters)):
        if callable(parameters[i]):
            parameters[i] = parameters[i]()
    func_parameters = func_var.parameters
    if len(parameters) != len(func_parameters):
        raise ValueError(f"Function '{func_var.name}' expects {len(func_parameters)} parameters, got {len(parameters)}.")
    for i in range(len(parameters)):
        if type(parameters[i]) != func_parameters[i][1]:
            raise ValueError(f"Function '{func_var.name}' expects parameter {i} to be of type {func_parameters[i]}, got {type(parameters[i])}.")

    previous_view = global_storage.current_view_set.copy()
    global_storage.add_view(func_var.name)
    global_storage.current_view_set = func_var.view
    for i in range(len(parameters)):
        new_var = copy(parameters[i])
        new_var.name = func_parameters[i][0]
        global_storage.add_variable(new_var)
    return_value: Type[Variable] = None
    for statement in func_var.value:
        return_check = statement()
        if isinstance(return_check, Result):
            return_value = return_check.value
            break
    if return_value is not None:
        return_value = copy(return_value)
    global_storage.remove_view(func_var.name)
    global_storage.current_view_set = previous_view
    return return_value

def _top():
    return Integer(value=global_robot.move_top())

def _bottom():
    return Integer(value=global_robot.move_down())

def _left():
    return Integer(value=global_robot.move_left())

def _right():
    return Integer(value=global_robot.move_right())

def _bind(key):
    if callable(key):
        key = key()
    if type(key) != String:
        raise ValueError(f"Key must be of type String, not {type(key)}.")
    global_robot.bind(key.value)

def _timeshift(value):
    if callable(value):
        value = value()
    if type(value) != Integer and type(value) != String:
        raise ValueError(f"Value must be of type Integer or String, not {type(value)}.")
    value = value.value
    return global_robot.timeshift(value)