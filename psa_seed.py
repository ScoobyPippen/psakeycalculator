"""Core PSA seed/key challenge-response logic implemented in Python."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Tuple

HEX_DIGITS = frozenset("0123456789ABCDEF")


@dataclass(frozen=True)
class Secrets:
    """Container for the three secret constants used by the PSA transform."""

    modulus: int
    subtractor: int
    multiplier: int

    def as_tuple(self) -> Tuple[int, int, int]:
        return self.modulus, self.subtractor, self.multiplier


SEC_1 = Secrets(0xB2, 0x3F, 0xAA)
SEC_2 = Secrets(0xB1, 0x02, 0xAB)


def _unpack_sec(sec: Secrets | Sequence[int]) -> Tuple[int, int, int]:
    if isinstance(sec, Secrets):
        return sec.as_tuple()
    if len(sec) != 3:
        raise ValueError("Secret tuples must contain exactly three integers")
    return int(sec[0]), int(sec[1]), int(sec[2])


def transform(data: int, sec: Secrets | Sequence[int]) -> int:
    """Apply the PSA transformation to a 16-bit integer and return the result."""

    modulus, subtractor, multiplier = _unpack_sec(sec)
    data &= 0xFFFF
    result = ((data % modulus) * multiplier) - ((data // modulus) * subtractor)
    if result < 0:
        result += (modulus * multiplier) + subtractor
    return result & 0xFFFF


def _clean_hex(value: str, expected_len: int, label: str) -> str:
    value = value.strip().upper()
    if len(value) != expected_len or any(ch not in HEX_DIGITS for ch in value):
        raise ValueError(f"{label} must be {expected_len} hexadecimal characters")
    return value


def _bytes_from_hex(hex_string: str) -> Tuple[int, ...]:
    return tuple(int(hex_string[i : i + 2], 16) for i in range(0, len(hex_string), 2))


def compute_response(
    seed_hex: str,
    pin_hex: str,
    *,
    sec_1: Secrets | Sequence[int] = SEC_1,
    sec_2: Secrets | Sequence[int] = SEC_2,
) -> str:
    """Compute the PSA response for a given 4-byte seed and 2-byte pin."""

    seed_hex = _clean_hex(seed_hex, 8, "Seed")
    pin_hex = _clean_hex(pin_hex, 4, "PIN")

    seed_bytes = _bytes_from_hex(seed_hex)
    pin_bytes = _bytes_from_hex(pin_hex)

    pin_value = (pin_bytes[0] << 8) | pin_bytes[1]
    seed_mix_03 = (seed_bytes[0] << 8) | seed_bytes[3]
    seed_mix_12 = (seed_bytes[1] << 8) | seed_bytes[2]

    res_msb = transform(pin_value, sec_1) | transform(seed_mix_03, sec_2)
    res_lsb = transform(seed_mix_12, sec_1) | transform(res_msb & 0xFFFF, sec_2)

    return f"{((res_msb & 0xFFFF) << 16) | (res_lsb & 0xFFFF):08X}"


__all__ = ["compute_response", "transform", "Secrets", "SEC_1", "SEC_2"]
