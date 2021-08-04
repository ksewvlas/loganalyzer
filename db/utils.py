from typing import Union, List
from copy import deepcopy
from collections.abc import Mapping

from asyncpg import Record


def from_record_to_dict(data: Union[List[Record], Record]):
    if not data:
        return {}

    if isinstance(data, (tuple, list)):
        return [dict(record) for record in data]

    return dict(data)


def nested_update(data, updated) -> dict:
    data = deepcopy(data)

    for k, v in updated.items():
        if isinstance(v, Mapping):
            data[k] = nested_update(data.get(k, {}), v)
        else:
            data[k] = v

    return updated
