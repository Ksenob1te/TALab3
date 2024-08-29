from typing import Dict, Type, Union, List, Callable
from ..general import *
from .variable import *
from copy import copy

class Function(Variable):
    value: Callable = None
    var_type = Callable

    def __init__(self):
        super().__init__()
        self.value = None
