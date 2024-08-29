from ..classes import *

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
    else:
        if instead is not None:
            for statement in instead:
                break_check = statement()
                if isinstance(break_check, Break):
                    return Break()
    return None