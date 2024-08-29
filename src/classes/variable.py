from typing import Dict, Type, Union, List
from ..general import *
from copy import copy

class Break:
    def __call__(self, *args, **kwargs):
        return self

class Result:
    value: Type['Variable'] = None
    def __init__(self, value):
        self.value = value

    def __call__(self, *args, **kwargs):
        return self

class Variable:
    _memory_index: int = 0
    memory_id: int = None
    value = None
    name: str = None
    var_type = None
    size_iden: int = 1
    is_const: bool = False

    def __init__(self, name: str = None):
        self.name = name
        self.memory_id = Variable._memory_index
        Variable._memory_index += 1

    def __setattr__(self, key, value, skip_check: bool = False):
        if skip_check:
            super().__setattr__(key, value)
            return self
        if key == "value":
            if value is not None and type(value) is not self.var_type:
                raise ValueError(f"Value must be of type '{self.var_type}', not '{type(value)}'.")
        if self.is_const and key is "value":
            raise ValueError(f"Cannot modify constant variable '{self.name}'.")
        bison_log(f"set: {self.name} {key} = {value}")
        super().__setattr__(key, value)
        return self

    def __getitem__(self, item):
        raise ValueError(f"Invalid operation for type '{type(self)}'.")

    def __eq__(self, other):
        if type(self) != type(other):
            raise RuntimeError(f"Cannot compare variables of different types '{type(self)}' and '{type(other)}'.")
        if hasattr(self, "value_type") and hasattr(other, "value_type") and self.value_type != other.value_type:
            raise RuntimeError(f"Cannot compare variables of different types '{self.value_type}' and '{other.value_type}'.")
        if self.value != other.value:
            return Integer(value=0)
        else:
            return Integer(value=1)

    def __lt__(self, other):
        if type(self) != type(other):
            raise RuntimeError(f"Cannot compare variables of different types '{type(self)}' and '{type(other)}'.")
        if hasattr(self, "value_type") and hasattr(other, "value_type") and self.value_type != other.value_type:
            raise RuntimeError(f"Cannot compare variables of different types '{self.value_type}' and '{other.value_type}'.")
        if self.value < other.value:
            return Integer(value=1)
        else:
            return Integer(value=0)

    def __gt__(self, other):
        if type(self) != type(other):
            raise RuntimeError(f"Cannot compare variables of different types '{type(self)}' and '{type(other)}'.")
        if hasattr(self, "value_type") and hasattr(other, "value_type") and self.value_type != other.value_type:
            raise RuntimeError(f"Cannot compare variables of different types '{self.value_type}' and '{other.value_type}'.")
        if self.value > other.value:
            return Integer(value=1)
        else:
            return Integer(value=0)

    def __bool__(self):
        return bool(self.value)

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        result.memory_id = Variable._memory_index
        Variable._memory_index += 1
        result.name = None
        return result

    def dereference(self):
        raise ValueError(f"Invalid operation for type '{type(self)}'.")

    def size(self):
        return Integer(value=self.size_iden)


class String(Variable):
    value: Union[str, None] = None
    var_type = str


    def __init__(self, name: str = None, value: str = None):
        super().__init__(name)
        self.value = value

    def __getitem__(self, item):
        if type(item) is Integer:
            item = item.value
        if type(item) is not int:
            raise ValueError(f"Invalid type '{type(item)}' for indexing string.")
        if item >= len(self.value) or item < 0:
            raise RuntimeError(f"String index out of bounds.")
        return self.value[item]

    def __add__(self, other: 'String'):
        if self.value is None or other.value is None:
            raise ValueError(f"Trying to add undefined variable '{self.memory_id}' to '{other.memory_id}'.")
        result_int = String(None, self.value + other.value)
        return result_int

    def __setattr__(self, key, value):
        if key == "value":
            if value is not None and type(value) is type(self):
                self.is_const = value.is_const
                value = value.value
        return super().__setattr__(key, value)

    def append(self, value: 'String'):
        if type(value) is not String:
            raise ValueError(f"Invalid type '{type(value)}' for appending to string.")
        self.value += value.value
        return self.value


class Integer(Variable):
    value: Union[int, None] = None
    var_type = int

    def __init__(self, name: str = None, value: int = None):
        super().__init__(name)
        self.value = value

    def __setattr__(self, key, value):
        if key == "value":
            if value is not None and type(value) is type(self):
                self.is_const = value.is_const
                value = value.value
        return super().__setattr__(key, value)

    def __add__(self, other: 'Integer'):
        if self.value is None or other.value is None:
            raise ValueError(f"Trying to add undefined variable '{self.memory_id}' to '{other.memory_id}'.")
        result_int = Integer(None, self.value + other.value)
        return result_int

    def __sub__(self, other: 'Integer'):
        if self.value is None or other.value is None:
            raise ValueError(f"Trying to subtract undefined variable '{self.memory_id}' from '{other.memory_id}'.")
        result_int = Integer(None, self.value - other.value)
        return result_int

    def __mul__(self, other: 'Integer'):
        if self.value is None or other.value is None:
            raise ValueError(f"Trying to multiply undefined variable '{self.memory_id}' by '{other.memory_id}'.")
        result_int = Integer(None, self.value * other.value)
        return result_int

    def __truediv__(self, other: 'Integer'):
        if self.value is None or other.value is None:
            raise ValueError(f"Trying to divide undefined variable '{self.memory_id}' by '{other.memory_id}'.")
        result_int = Integer(None, int(self.value) // int(other.value))
        return result_int

    def __mod__(self, other: 'Integer'):
        if self.value is None or other.value is None:
            raise ValueError(f"Trying to modulo undefined variable '{self.memory_id}' by '{other.memory_id}'.")
        result_int = Integer(None, self.value % other.value)
        return result_int

    def __int__(self: 'Integer'):
        if self.value is not None:
            return self.value
        else:
            raise ValueError(f"Trying to get int from undefined variable '{self.memory_id}'.")


class Pointer(Variable):
    class Link:
        value: Union[Type[Variable], None] = None
        value_type: Type[Variable] = None
        position: int = None
        is_const: bool = False

        def __init__(self, value: Type[Variable] = None, value_type: Type[Variable] = None, position: int = 0, is_const : bool = False):
            self.value = value
            self.value_type = value_type
            self.is_const = is_const
            self.position = position

        # def __add__(self, other):
        #     if type(other) is not int:
        #         raise ValueError(f"Invalid type '{type(other)}' for incrementing pointer value")
        #     if self.position + other >= self.value.size_iden or self.position + other < 0:
        #         raise RuntimeError(f"Pointer incrementation out of bounds.")
        #     return self.position + other
        #
        # def __sub__(self, other):
        #     if type(other) is not int:
        #         raise ValueError(f"Invalid type '{type(other)}' for decrementing pointer value")
        #     if self.position + other >= self.value.size_iden or self.position + other < 0:
        #         raise RuntimeError(f"Pointer decrementation out of bounds.")
        #     return self.position

    value: Union[Link, None] = None
    var_type = "pointer"

    def __copy__(self):
        is_const = self.is_const
        self.is_const = False
        result = super().__copy__()
        result.value = copy(self.value)
        self.is_const = is_const
        return result

    def __init__(self, name: str = None, value: 'Pointer.Link' = None, value_type: Type[Variable] = None,
                 is_const: bool = False, is_value_const: bool = False):
        self.var_type = Pointer.Link
        super().__init__(name)
        if value is not None:
            self.value = value
        else:
            self.value = Pointer.Link(value_type=value_type, is_const=is_value_const)
        if is_value_const:
            self.value.is_const = True
        self.is_const = is_const

    def set_reference(self, value: Type[Variable]):
        if self.is_const:
            raise ValueError(f"Cannot write to constant pointer '{self.name}'.")
        self.value.position = 0
        if value is not None and value.var_type is not self.value.value_type:
            raise ValueError(f"Pointer value must be of type '{self.value.value_type}', not '{type(value)}'.")
        self.value.value = value


    @classmethod
    def create_ref(cls, value: Type[Variable]) -> 'Pointer':
        if callable(value):
            value = value()
        return Pointer(value=Pointer.Link(value=value))


    def dereference(self, is_writing: bool = False) -> Type[Variable]:
        # TODO: think about how to create const pointers
        if self.value is None:
            raise ValueError(f"Pointer '{self.name}' is not initialized.")
        if self.value.is_const and is_writing:
            raise ValueError(f"Cannot write to constant pointer '{self.name}'.")
        if type(self.value.value) is Array:
            return self.value.value[self.value.position]
        return self.value.value

    def __setattr__(self, key, value):
        if key == "value":
            if value is not None and type(value) is type(self):
                self.is_const = value.is_const
                value = value.value
                if self.value:
                    value.is_const = self.value.is_const
            if type(value) is not Pointer.Link:
                raise ValueError(f"Pointer value must be of type 'Pointer.Link', not '{type(value)}'.")
            if self.value and self.value.value_type and type(value.value) is not self.value.value_type:
                raise ValueError(f"Pointer value type must be of type '{self.value.value_type}', not '{type(value.value)}'.")
        return super().__setattr__(key, value)

    def __add__(self, other):
        if type(other) is not Integer:
            raise ValueError(f"Invalid type '{type(other)}' for incrementing pointer value")
        other: int = other.value
        result: 'Pointer' = Pointer(value=copy(self.value), is_const=self.is_const)
        if result.value.position + other >= result.value.value.size_iden or result.value.position + other < 0:
            raise RuntimeError(f"Pointer incrementation out of bounds.")
        result.value.position += other
        return result

    def __sub__(self, other):
        if type(other) is not Integer:
            raise ValueError(f"Invalid type '{type(other)}' for incrementing pointer value")
        other: int = other.value
        result: 'Pointer' = Pointer(value=copy(self.value), is_const=self.is_const)
        if result.value.position - other >= result.value.value.size_iden or result.value.position - other < 0:
            raise RuntimeError(f"Pointer decrementation out of bounds.")
        result.value.position -= other
        return result


    def __check_type(self, other):
        if type(self) != type(other):
            raise RuntimeError(f"Cannot compare variables of different types '{type(self)}' and '{type(other)}'.")
        if self.value is None or other.value is None:
            raise RuntimeError(f"Trying to compare undefined variable '{self.memory_id}' with '{other.memory_id}'.")
        if self.value.value_type != other.value.value_type:
            raise RuntimeError(f"Cannot compare pointers of different types '{self.value.value_type}' and '{other.value.value_type}'.")
        if self.value.value is None or other.value.value is None:
            raise RuntimeError(f"Trying to compare undefined pointers '{self.memory_id}' with '{other.memory_id}'.")

    def __eq__(self, other):
        self.__check_type(other)
        if self.value.value.memory_id != self.value.value.memory_id:
            return Integer(value=0)
        else:
            return Integer(value=1)

    def __gt__(self, other):
        self.__check_type(other)
        if self.value.value.memory_id > self.value.value.memory_id:
            return Integer(value=1)
        else:
            return Integer(value=0)

    def __lt__(self, other):
        self.__check_type(other)
        if self.value.value.memory_id < self.value.value.memory_id:
            return Integer(value=1)
        else:
            return Integer(value=0)



class Array(Variable):
    value: Union[List[Type[Variable]], None] = None
    var_type = list
    value_type: Type[Variable] = None
    is_static: bool = False
    current_size: int = 0
    size_iden: int = 10
    quant: int = 10

    def __init__(self, name: str = None, is_static: bool = False, value_type: Type[Variable] = None, size: int = 10):
        super().__init__(name)
        self.current_size = int(size)
        self.is_static = is_static
        self.value_type = value_type
        self.size_iden = int(size)
        self.quant = int(size) if int(size) != 0 else 10
        self.value = [value_type(name=f"{self.name}_{i}") for i in range(int(size))]

    def __getitem__(self, item: Union[int, Integer]) -> Type[Variable]:
        if callable(item):
            item = item()
        if type(item) is Integer:
            item = item.value
        if type(item) is not int:
            raise ValueError(f"Invalid type '{type(item)}' for indexing array.")
        if item >= self.current_size or item < 0:
            raise RuntimeError(f"Array index out of bounds.")
        return self.value[item]

    def __setattr__(self, key, value):
        if key == "value":
            if value is not None and type(value) is type(self):
                if value.value_type and self.value_type and value.value_type != self.value_type:
                    raise ValueError(f"Array value must be of type '{self.value_type}', not '{value.value_type}'.")
                self.is_static = value.is_static
                self.current_size = value.current_size
                self.value_type = value.value_type
                self.size_iden = value.size_iden
                self.quant = value.quant
                value = value.value
        return super().__setattr__(key, value)

    def size(self):
        return Integer(value=self.size_iden)

    def append(self, value: Type[Variable]):
        if type(value) != self.value_type:
            raise ValueError(f"Array value must be of type '{self.value_type}', not '{type(value)}'.")
        if self.current_size >= self.size_iden:
            if self.is_static:
                raise RuntimeError(f"Cannot change size of static array '{self.name}'.")
            self.value += [self.value_type(name=f"{self.name}_{self.size_iden + i}") for i in range(self.quant)]
            self.size_iden += self.quant
        self.value[self.current_size] = copy(value)
        self.current_size += 1
        return self.value


