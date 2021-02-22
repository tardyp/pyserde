import logging
from dataclasses import dataclass
from ipaddress import IPv4Address
from typing import Dict, List, Optional, Union
from uuid import UUID

import pytest

from serde import deserialize, from_dict, to_dict, SerdeError
from serde import init as serde_init
from serde import logger, serialize
from serde.json import from_json, to_json

logging.basicConfig(level=logging.WARNING)
logger.setLevel(logging.DEBUG)

serde_init(True)


@deserialize
@serialize
@dataclass(unsafe_hash=True)
class PriUnion:
    """
    Union Primitives.
    """

    v: Union[int, str, float, bool]


@deserialize
@serialize
@dataclass(unsafe_hash=True)
class PriOptUnion:
    """
    Union Primitives.
    """

    v: Union[Optional[int], Optional[str], Optional[float], Optional[bool]]


@deserialize
@serialize
@dataclass(unsafe_hash=True)
class ContUnion:
    """
    Union Containers.
    """

    v: Union[Dict[str, int], List[int], List[str]]


def test_union():
    v = PriUnion(10)
    s = '{"v": 10}'
    assert s == to_json(v)
    print(f'foo {v.__serde_hidden__.code}')
    assert v == from_json(PriUnion, s)

    v = PriUnion(10.0)
    s = '{"v": 10.0}'
    assert s == to_json(v)
    assert v == from_json(PriUnion, s)

    v = PriUnion('foo')
    s = '{"v": "foo"}'
    assert s == to_json(v)
    assert v == from_json(PriUnion, s)

    v = PriUnion(True)
    s = '{"v": true}'
    assert s == to_json(v)
    assert v == from_json(PriUnion, s)


def test_union_optional():
    v = PriOptUnion(10)
    s = '{"v": 10}'
    assert s == to_json(v)
    assert v == from_json(PriOptUnion, s)

    v = PriOptUnion(None)
    s = '{"v": null}'
    assert s == to_json(v)
    assert v == from_json(PriOptUnion, s)

    v = PriOptUnion("foo")
    s = '{"v": "foo"}'
    assert s == to_json(v)
    assert v == from_json(PriOptUnion, s)

    v = PriOptUnion(10.0)
    s = '{"v": 10.0}'
    assert s == to_json(v)
    assert v == from_json(PriOptUnion, s)

    v = PriOptUnion(False)
    s = '{"v": false}'
    assert s == to_json(v)
    assert v == from_json(PriOptUnion, s)


def test_union_containers():
    v = ContUnion([1, 2, 3])
    s = '{"v": [1, 2, 3]}'
    assert s == to_json(v)
    assert v == from_json(ContUnion, s)

    v = ContUnion(['1', '2', '3'])
    s = '{"v": ["1", "2", "3"]}'
    assert s == to_json(v)
    assert v == from_json(ContUnion, s)

    v = ContUnion({'a': 1, 'b': 2, 'c': 3})
    s = '{"v": {"a": 1, "b": 2, "c": 3}}'
    assert s == to_json(v)
    # Note: this only works because Dict[str, int] comes first in Union otherwise a List would win
    assert v == from_json(ContUnion, s)


def test_union_with_complex_types():
    @deserialize
    @serialize
    @dataclass
    class A:
        v: Union[int, IPv4Address, UUID]

    a_int = A(1)
    a_int_json = '{"v": 1}'
    assert to_json(a_int) == a_int_json
    assert from_json(A, a_int_json) == a_int
    assert a_int == from_dict(A, to_dict(a_int))

    a_ip = A(IPv4Address("127.0.0.1"))
    a_ip_json = '{"v": "127.0.0.1"}'
    assert to_json(a_ip) == a_ip_json
    assert from_json(A, a_ip_json) == a_ip
    assert a_ip == from_dict(A, to_dict(a_ip))

    a_uid = A(UUID("a317958e-4cbb-4213-9f23-eaff1563c472"))
    a_uid_json = '{"v": "a317958e-4cbb-4213-9f23-eaff1563c472"}'
    assert to_json(a_uid) == a_uid_json
    assert from_json(A, a_uid_json) == a_uid
    assert a_uid == from_dict(A, to_dict(a_uid))


def test_union_with_complex_types_and_reuse_instances():
    @deserialize(reuse_instances_default=True)
    @serialize(reuse_instances_default=True)
    @dataclass
    class A:
        v: Union[int, IPv4Address, UUID]

    a_int = A(1)
    a_int_roundtrip = from_dict(A, to_dict(a_int))
    assert a_int == a_int_roundtrip
    assert a_int.v is a_int_roundtrip.v

    a_ip = A(IPv4Address("127.0.0.1"))
    a_ip_roundtrip = from_dict(A, to_dict(a_ip))
    assert a_ip == a_ip_roundtrip
    assert a_ip.v is a_ip_roundtrip.v

    a_uid = A(UUID("a317958e-4cbb-4213-9f23-eaff1563c472"))
    a_uid_roundtrip = from_dict(A, to_dict(a_uid))
    assert a_uid == a_uid_roundtrip
    assert a_uid.v is a_uid_roundtrip.v


def test_optional_union_with_complex_types():
    @deserialize
    @serialize
    @dataclass
    class A:
        v: Optional[Union[int, IPv4Address, UUID]]

    a = A(123)
    assert a == from_dict(A, to_dict(a))
    assert a == from_dict(A, to_dict(a, reuse_instances=True), reuse_instances=True)

    a_none = A(None)
    assert a_none == from_dict(A, to_dict(a_none))
    assert a_none == from_dict(A, to_dict(a_none, reuse_instances=True), reuse_instances=True)


def test_union_with_complex_types_in_containers():
    @deserialize
    @serialize
    @dataclass
    class A:
        v: Union[List[IPv4Address], List[UUID]]

    a_ips = A([IPv4Address("127.0.0.1"), IPv4Address("10.0.0.1")])
    assert a_ips == from_dict(A, to_dict(a_ips))
    assert a_ips == from_dict(A, to_dict(a_ips, reuse_instances=True), reuse_instances=True)

    a_uids = A([UUID("9c244009-c60d-452b-a378-b8afdc0c2d90"), UUID("5831dc09-20fe-4433-b476-5866b7143364")])
    assert a_uids == from_dict(A, to_dict(a_uids))
    assert a_uids == from_dict(A, to_dict(a_uids, reuse_instances=True), reuse_instances=True)

    a_empty = A([])
    assert a_empty == from_dict(A, to_dict(a_empty))
    assert a_empty == from_dict(A, to_dict(a_empty, reuse_instances=True), reuse_instances=True)


def test_union_exception_if_nothing_matches():
    @deserialize
    @serialize
    @dataclass
    class A:
        v: Union[IPv4Address, UUID]

    with pytest.raises(SerdeError) as ex1:
        from_dict(A, {"v": "not-ip-or-uuid"})
    assert str(ex1.value) == "Can not deserialize 'not-ip-or-uuid' of type str into Union[IPv4Address, UUID]. Reason: badly formed hexadecimal UUID string"

    with pytest.raises(SerdeError) as ex2:
        from_dict(A, {"v": "not-ip-or-uuid"}, reuse_instances=True)
    assert str(ex2.value) == "Can not deserialize 'not-ip-or-uuid' of type str into Union[IPv4Address, UUID]. Reason: badly formed hexadecimal UUID string"

    with pytest.raises(SerdeError) as ex3:
        from_dict(A, {"v": None})
    assert str(ex3.value) == "Can not deserialize None of type NoneType into Union[IPv4Address, UUID]. Reason: one of the hex, bytes, bytes_le, fields, or int arguments must be given"

    with pytest.raises(SerdeError) as ex4:
        to_dict(A("not-ip-or-uuid"))
    assert str(ex4.value) == "Can not serialize 'not-ip-or-uuid' of type str for Union[IPv4Address, UUID]"

    with pytest.raises(SerdeError) as ex5:
        to_dict(A("not-ip-or-uuid"), reuse_instances=True)
    assert str(ex5.value) == "Can not serialize 'not-ip-or-uuid' of type str for Union[IPv4Address, UUID]"

    with pytest.raises(SerdeError) as ex6:
        to_dict(A(None), reuse_instances=True)
    assert str(ex6.value) == "Can not serialize None of type NoneType for Union[IPv4Address, UUID]"


def test_union_in_union():
    @deserialize
    @serialize
    @dataclass
    class A:
        v: Union[UUID, Union[int, str]]

    a_uuid = A(UUID("00611ee9-7ca3-41d3-9607-ea7268e264ea"))
    assert a_uuid == from_dict(A, to_dict(a_uuid))
    assert a_uuid == from_dict(A, to_dict(a_uuid, reuse_instances=True), reuse_instances=True)

    a_int = A(1)
    assert a_int == from_dict(A, to_dict(a_int))
    assert a_int == from_dict(A, to_dict(a_int, reuse_instances=True), reuse_instances=True)

    a_str = A("hello")
    assert a_str == from_dict(A, to_dict(a_str))
    assert a_str == from_dict(A, to_dict(a_str, reuse_instances=True), reuse_instances=True)
