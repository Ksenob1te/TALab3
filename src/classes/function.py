from typing import Dict, Type, Union, List, Callable, Tuple
from types import FunctionType
from ..general import *
from .variable import *
from copy import copy

class Function(Variable):
    value: List[Callable] = None
    return_type: Type[Variable] = None
    parameters: List[Tuple[str, Type[Variable]]] = None
    var_type = FunctionType
    view: List[str] = None

    def __init__(self, name = None, value = None, return_type: Type[Variable] = None, parameters: List[Tuple[str, Type[Variable]]] = None, view: List[str] = None):
        if view is None:
            view = []
        super().__init__(name)
        self.view = view + [self.name]
        self.return_type = return_type
        self.parameters = parameters
        self.value = value

    def __setattr__(self, key, value: 'Function | List[Callable]'):
        if key == "value":
            if isinstance(value, Function):
                value = value.value
                self.return_type = value.return_type
                self.parameters = value.parameters
                self.view = value.view

            if value is not None and type(value) is not list:
                raise ValueError(f"Value must be of type '{self.var_type}', not '{type(value)}'.")
            for func in value:
                if not callable(func):
                    raise ValueError(f"Value must be a list of callables, not '{type(func)}'.")
        bison_log(f"set: {self.name} {key} = {value}")
        super().__setattr__(key, value, skip_check=True)
        return self

    def __copy__(self):
        result: 'Function' = super().__copy__()
        result.return_type = self.return_type
        result.parameters = self.parameters
        result.view = self.view
        return result
