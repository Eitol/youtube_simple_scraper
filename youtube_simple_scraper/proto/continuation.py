# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: continuation.proto
# plugin: python-betterproto
# protoc --descriptor_set_out=/dev/stdout --python_betterproto_out=:. ./continuation.proto
from dataclasses import dataclass
from typing import List

import betterproto


@dataclass
class ContinuationToken(betterproto.Message):
    video_id: "VideoIdSubMessage" = betterproto.message_field(2)
    field_3: int = betterproto.uint32_field(3)
    sub_messsage_6: "ParamsSubMessage" = betterproto.message_field(6)


@dataclass
class VideoIdSubMessage(betterproto.Message):
    video_id: str = betterproto.string_field(2)


@dataclass
class ParamsSubMessage(betterproto.Message):
    string_1: str = betterproto.string_field(1)
    sub_messsage_4: "ParamsSubSubMessage" = betterproto.message_field(4)
    offset: int = betterproto.uint32_field(5)
    string_8: str = betterproto.string_field(8)


@dataclass
class ParamsSubSubMessage(betterproto.Message):
    video_id: str = betterproto.string_field(4)
    int_6: int = betterproto.uint32_field(6)
    int_15: int = betterproto.uint32_field(15)


@dataclass
class Field1SubMessage(betterproto.Message):
    f1: int = betterproto.uint32_field(1)
    f2: float = betterproto.fixed32_field(2)


@dataclass
class TwinIntMessage(betterproto.Message):
    int_1: int = betterproto.uint32_field(1)
    int_3: int = betterproto.int32_field(3, group="int_2")


@dataclass
class TwinInt12Message(betterproto.Message):
    timestamp: int = betterproto.uint32_field(1)
    int_2: int = betterproto.uint32_field(2)


@dataclass
class Field4SubMessage(betterproto.Message):
    sub_msg: "TwinInt12Message" = betterproto.message_field(1)


@dataclass
class ParamsMessage(betterproto.Message):
    field_1: "Field1SubMessage" = betterproto.message_field(1)
    field_array_2: List["TwinIntMessage"] = betterproto.message_field(2)
    int_3: int = betterproto.uint32_field(3, group="int_2")
    sub_messsage_4: "Field4SubMessage" = betterproto.message_field(4)