# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing


class SimpleObject(typing.TypedDict):
    idx: str
    name: str


class TypedObject(SimpleObject):
    type: str


def simple_object(obj) -> SimpleObject:
    if obj.name:
        name = obj.name
    else:
        name = obj.long_name if hasattr(obj, "long_name") else "undefined"

    return {"idx": obj.uuid, "name": str(name)}


def typed_object(obj) -> TypedObject:
    return simple_object(obj) | {"type": obj.xtype}  # type: ignore[return-value]
