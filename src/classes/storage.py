from typing import Dict, Type, Union, List
from ..general import *
from .variable import Variable, Integer, String, Pointer, Array, Break


class Storage:
    memory_storage: Dict[int, Type[Variable]] = None
    name_storage: Dict[str, Type[Variable]] = None
    view_set: List[str] = None

    def __init__(self):
        self.memory_storage = {}
        self.name_storage = {}

    def add_variable(self, var: Type[Variable]):
        if var.memory_id in self.memory_storage:
            raise ValueError(f"Variable with id {var.memory_id} already exists.")
        self.memory_storage[var.memory_id] = var
        if var.name in self.name_storage:
            previous_var = self.name_storage[var.name]
            del self.memory_storage[previous_var.memory_id]
        self.name_storage[var.name] = var

    def __getitem__(self, item: Union[int, str]) -> Type[Variable]:
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
            if item not in self.name_storage:
                raise ValueError(f"Variable with name '{item}' does not exist.")
            return self.name_storage[item]
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
        "array of": Array
    }
    type_dict = {
        str: String,
        int: Integer,
        Pointer.Link: Pointer,
        list: Array
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
    else:
        value = kwargs.get("value", None)
        resulted_var: Type[Variable] = var_type(var_name, value)
    global_storage.add_variable(resulted_var)
    bison_log(f"initialized: {kwargs}")