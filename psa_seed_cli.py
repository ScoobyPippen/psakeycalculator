"""Command-line interface for the PSA seed/key calculator."""
from __future__ import annotations

import argparse
import sys

from psa_seed import compute_response


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute PSA challenge responses from a seed and PIN."
    )
    parser.add_argument("seed", help="8 hex characters representing the challenge")
    parser.add_argument("pin", help="4 hex characters representing the PIN")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        response = compute_response(args.seed, args.pin)
    except ValueError as exc:
        parser.error(str(exc))

    print(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
