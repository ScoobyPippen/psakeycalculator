# PSA Seed/Key Calculator (Python)

This repository contains a clean-room Python port of the PSA challenge/response
algorithm that many PSA ECUs use to derive an unlock key (response) from a 4-byte
seed (challenge) and a 2-byte PIN (application key). The goal is to make the
math easy to audit, easy to reuse, and easy to package for desktops or scripts.

## Project layout

- `psa_seed.py` – core algorithm (`transform`, `compute_response`) with strict
  input validation and documented secrets.
- `psa_seed_cli.py` – command-line utility for one-off calculations.
- `psa_seed_gui.py` – PyQt5 desktop calculator with copy-to-clipboard support.

## Requirements

- Python 3.10 or newer.
- PyQt5 (`pip install PyQt5`) is required only if you intend to launch the GUI.
  The core module and CLI rely solely on the standard library.

## Quick start

### CLI

```bash
python psa_seed_cli.py 11111111 D91C
```

The tool prints the 8-character hexadecimal response or exits with an error if
the seed/PIN are not valid hex strings of the expected length.

### GUI

```bash
python psa_seed_gui.py
```

Enter any 8-hex seed and 4-hex PIN, click **Compute Response**, and copy the
result with the provided button. Invalid input triggers an in-app warning.

## Algorithm deep dive

The PSA algorithm relies on two secret triplets:

| Name  | Modulus (`s₀`) | Subtractor (`s₁`) | Multiplier (`s₂`) |
|-------|----------------|-------------------|-------------------|
| `SEC_1` | `0xB2`          | `0x3F`            | `0xAA`            |
| `SEC_2` | `0xB1`          | `0x02`            | `0xAB`            |

The `transform` helper mirrors the OEM implementation:

$$
	ext{transform}(d, s) = \left(((d \bmod s_0) \cdot s_2) - \left(\left\lfloor\frac{d}{s_0}\right\rfloor \cdot s_1\right)\right) \bmod 2^{16}
$$

If the intermediate subtraction becomes negative, the code wraps it by adding
$(s_0 \cdot s_2) + s_1$ before applying the final `0xFFFF` mask. This exactly
matches the arithmetic in the original C/C# sources.

`compute_response(seed_hex, pin_hex)` performs the following steps:

1. **Normalize input** – Trim whitespace, uppercase, and verify the seed has 8
   hex characters (4 bytes) while the PIN has 4 hex characters (2 bytes).
2. **Pack bytes** – `seed[0..3]` and `pin[0..1]` are parsed into integers. We
   reuse the OEM mixing pattern: `pin_value = pin0<<8 | pin1`, `seed_mix_03 =
   seed0<<8 | seed3`, `seed_mix_12 = seed1<<8 | seed2`.
3. **Upper 16 bits** – `res_msb = transform(pin_value, SEC_1) | transform(seed_mix_03, SEC_2)`.
4. **Lower 16 bits** – `res_lsb = transform(seed_mix_12, SEC_1) | transform(res_msb, SEC_2)`.
5. **Final response** – `(res_msb << 16) | res_lsb`, formatted as an uppercase
   8-character string.

Because the secrets are encoded as `dataclass` instances, alternative constant
sets (for other OEMs) can be injected without touching the algorithm.

## Validation & testing

- Every interface calls the same `compute_response`, guaranteeing consistent
  results across CLI, GUI, or future integrations.
- Parsing helpers reject malformed hex strings early, closely mirroring the
  safety checks from the embedded reference implementation.
- To sanity-check locally:

  ```bash
  python - <<'PY'
  from psa_seed import compute_response
  print(compute_response("11111111", "D91C"))
  PY
  ```

## License & attribution

This repo preserves Ludwig V.'s GPLv3 license notice from the original release.
The Python port was authored here so that more tooling (CLI, GUI, web services)
can rely on a single, well-commented implementation.

Happy hacking!
