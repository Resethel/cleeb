from __future__ import annotations

import json
import operator
from typing import Callable, Literal


class Filter:
    """Represents a filter to apply to the data."""
    operator_map = {
        "==": operator.eq,
        "!=": operator.ne,
        ">": operator.gt,
        ">=": operator.ge,
        "<": operator.lt,
        "<=": operator.le
    }

    def __init__(
            self,
            key: str,
            operator: Literal['==', '!=', '>', '>=', '<', '<='] | Callable[[str, str], bool],
            value: str,
    ) -> None:
        self.value    : str = value
        self.key      : str = key
        self.operator = operator
    # End def __init__

    @property
    def operator(self) -> Callable:
        """Get the operator."""
        return self.__op

    @operator.setter
    def operator(self, operator_: Literal['==', '!=', '>', '>=', '<', '<='] | Callable[[str, str], bool]) -> None:
        """Set the operator."""
        if isinstance(operator_, str):
            if operator_ in Filter.operator_map:
                self.__op = Filter.operator_map[operator_]
            else:
                raise ValueError(f"Invalid operator '{operator_}'")

        elif isinstance(operator_, Callable):
            if operator_ not in Filter.operator_map.values():
                raise ValueError(f"Invalid operator '{operator_}'")
            self.__op = operator_

        else:
            raise TypeError(f"Expected 'operator' to be of type 'str' or 'Callable', not '{type(operator_)}'")
    # End def op

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def validate(self):
        """Validate the filter."""
        pass
    # End def validate

    # ------------------------------------------------------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------------------------------------------------------

    def serialize(self, method: Literal['json', 'dict'] = 'json', **kwargs) -> str | dict:
        """Serialize the filter."""
        if method == 'json':
            return json.dumps(self._to_dict(), **kwargs)
        if method == 'dict':
            return self._to_dict()
        raise ValueError(f"Invalid method '{method}'")
    # End def serialize

    @staticmethod
    def deserialize(data: str | dict, method: Literal['json', 'dict'] = 'json', **kwargs) -> Filter:
        """Deserialize the filter."""
        if method == 'json':
            return Filter._from_dict(json.loads(data, **kwargs))
        if method == 'dict':
            return Filter._from_dict(data)
        raise ValueError(f"Invalid method '{method}'")
    # End def deserialize

    def _to_dict(self) -> dict:
        return {
            "__type__" : "__Filter__",
            "key" : self.key,
            "op" : list(Filter.operator_map.keys())[list(Filter.operator_map.values()).index(self.op)],
            "value" : self.value
        }
    # End def _to_dict

    @staticmethod
    def _from_dict(data: dict) -> Filter:
        if data.get("__type__", None) != "__Filter__":
            raise ValueError(f"Invalid type '{data.get('__type__', None)}'")

        return Filter(
            key=data["key"],
            operator=data["op"],
            value=data["value"]
        )
    # End def _from_dict
