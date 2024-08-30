from typing import Dict, Type, Union, List, Tuple, Callable
from ..general import *
from .variable import Variable, Integer, String, Pointer, Array, Break, Result
from .function import Function
from types import FunctionType


class Storage:
    memory_storage: Dict[int, Type[Variable]] = None
    name_storage: Dict[Tuple[str, ...], Dict[str, Type[Variable]]] = None
    view_set: List[str] = None
    current_view_set: List[str] = None

    def __init__(self):
        self.memory_storage = {}
        self.name_storage = {}
        self.view_set = []
        self.current_view_set = []

    def add_view(self, view: str):
        self.view_set.append(view)

    def remove_view(self, view: str):
        all_vars = self.name_storage.get(tuple(self.view_set), {}).values()
        for var in all_vars:
            del self.memory_storage[var.memory_id]
        del self.name_storage[tuple(self.view_set)]
        if self.view_set[-1] != view:
            raise ValueError(f"View '{view}' is not the current view.")
        self.view_set.pop()

    def add_variable(self, var: Type[Variable]):
        current_view = tuple(self.view_set)
        self.name_storage[current_view] = self.name_storage.get(current_view, {})
        if var.memory_id in self.memory_storage:
            raise ValueError(f"Variable with id {var.memory_id} already exists.")
        self.memory_storage[var.memory_id] = var
        if var.name in self.name_storage[current_view]:
            previous_var = self.name_storage[current_view][var.name]
            del self.memory_storage[previous_var.memory_id]
        self.name_storage[current_view][var.name] = var

    def __getitem__(self, item: Union[int, str]) -> Type[Variable]:
        view_set = tuple(self.view_set)
        self.name_storage[view_set] = self.name_storage.get(view_set, {})
        if callable(item):
            item = item()
        if type(item) is Integer:
            item = item.value
        if type(item) is String:
            item = item.value
        if type(item) is int:
            if item not in self.memory_storage:
                raise ValueError(f"Variable with address {item} does not exist.")
            return self.memory_storage[item]
        if type(item) is str:
            if item not in self.name_storage[view_set]:
                view_set_temp = self.view_set[:-1]
                while len(view_set_temp) >= 0:
                    if len(view_set_temp) == 0 or view_set_temp[-1] in self.current_view_set:
                        if item in self.name_storage[tuple(view_set_temp)]:
                            return self.name_storage[tuple(view_set_temp)][item]
                    if len(view_set_temp) == 0:
                        raise ValueError(f"Variable with name '{item}' does not exist.")
                    view_set_temp = view_set_temp[:-1]
                # raise ValueError(f"Variable with name '{item}' does not exist.")
            return self.name_storage[view_set][item]
        raise ValueError(f"Invalid item type '{type(item)}'.")


global_storage: Storage = Storage()


def _init_pointer(**kwargs) -> Pointer:
    value: Union[Pointer.Link, None] = kwargs.get("value", None)
    value_type = kwargs.get("value_type", None)
    if value is None and value_type is None:
        raise ValueError("Pointer value or pointer value type must be specified.")
    return Pointer(value=value, value_type=value_type, name=kwargs.get("name", None), is_const=kwargs.get("is_const", False), is_value_const=kwargs.get("is_value_const", False))

def _init_array(**kwargs) -> Array:
    is_static: bool = bool(kwargs.get("is_static", False))
    size: int = int(kwargs.get("size", 10))
    value_type: Type[Variable] = kwargs.get("value_type", None)
    if value_type is None:
        raise ValueError("Array value type not specified.")
    return Array(name=kwargs.get("name", None), is_static=is_static, size=size, value_type=value_type)


def _init_function(**kwargs) -> Function:
    return Function(name=kwargs.get("name", None), value=kwargs.get("value", None), return_type=kwargs.get("value_type", None), parameters=kwargs.get("parameters", None), view=global_storage.view_set.copy())


# builder/factory pattern
def init_variable(**kwargs):
    """
    Initializes a variable with the specified type and value.

    :param kwargs: type, name and value (optional)
    :return:
    """
    global global_storage
    name_dict = {
        "integer": Integer,
        "string": String,
        "pointer": Pointer,
        "array of": Array,
        "function": Function
    }
    type_dict = {
        str: String,
        int: Integer,
        Pointer.Link: Pointer,
        list: Array,
        FunctionType: Function
    }
    # type of variable =========================
    var_type = kwargs.get("type", None)
    if var_type is None:
        raise ValueError("Variable type not specified.")
    if var_type not in type_dict:
        if var_type not in name_dict:
            raise ValueError(f"Variable type '{var_type}' is invalid.")
        else:
            var_type = name_dict[var_type]
    else:
        var_type = type_dict[var_type]
    # variable name ============================
    var_name = kwargs.get("name", None)
    if var_name is None:
        raise ValueError("Variable name not specified.")
    # variable value type ======================
    if "value_type" in kwargs:
        if kwargs["value_type"] in type_dict:
            kwargs["value_type"] = type_dict[kwargs["value_type"]]
        elif kwargs["value_type"] in name_dict:
            kwargs["value_type"] = name_dict[kwargs["value_type"]]
    # ==========================================
    if var_type == Pointer:
        resulted_var: Pointer = _init_pointer(**kwargs)
    elif var_type == Array:
        resulted_var: Array = _init_array(**kwargs)
    elif var_type == Function:
        resulted_var: Function = _init_function(**kwargs)
    else:
        value = kwargs.get("value", None)
        resulted_var: Type[Variable] = var_type(var_name, value)
    global_storage.add_variable(resulted_var)
    bison_log(f"initialized: {kwargs}")
    return resulted_var