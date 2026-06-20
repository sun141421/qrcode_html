# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A single-file QR Code generator (`index.html`) — pure HTML+JS, zero external dependencies. Implements the ISO/IEC 18004 QR Code standard from scratch in the browser. Supports UTF-8 (Chinese), versions 1-40, and all 4 error correction levels (L/M/Q/H).

## Architecture

The entire application lives in one file, `index.html`, with three sections:

1. **CSS** (lines 7-136) — Responsive centered card UI with gradient background, color pickers, size/ECC selectors.
2. **QR Engine** (`const QR = (() => {...})()` inside `<script>`, lines 196-593) — The QR code encoder, fully self-contained:
   - GF(256) finite field arithmetic (exponential/log tables)
   - Reed-Solomon error correction encoding
   - `ECC_SPEC` table (v1-40) with block counts and data codewords per ECC level
   - Data encoding for Numeric/Alphanumeric/Byte modes
   - Matrix construction: finder patterns, timing, alignment, format/version info
   - 8 mask pattern evaluation with penalty scoring
   - Public API: `QR.generate(text, ecc)` returns `{ matrix, size, version }`
3. **UI Controller** (lines 595-661) — DOM bindings, canvas rendering, PNG download

## Key Code Locations

- **GF(256) & Reed-Solomon**: `gfMul`, `rsGenPoly`, `rsEncode` (~lines 200-228)
- **Capacity table**: `ECC_SPEC` (~lines 232-274) — `[n1,d1,n2,d2]` per version per ECC level
- **Version selection**: `canEncode` / `chooseVersion` (~lines 297-341) — dynamically computes bit capacity from `ECC_SPEC` per ECC level, no hardcoded char limits
- **EC codeword table**: `ecPer` (~lines 411-415) — pre-computed RS codewords per block indexed by `[ecIdx][ver-1]`
- **Matrix builder**: `buildMatrix` (~lines 453-598) — all pattern placement, data interleaving, mask selection
- **Render**: `render` function (~lines 614-637) — draws to canvas with quiet zone and configurable colors

## How to Run

Just open the file in a browser — no build step, no server required:

```bash
start index.html          # Windows
open index.html           # macOS
```

## Known Issues / Gotchas

- The `set` helper (~line 458) silently skips cells already reserved — this is relied upon for correct layering order.
- 8-bit mode uses manual UTF-8 byte encoding (not `TextEncoder`), which may behave differently on ancient browsers.
- Finder pattern `fillFP` (~lines 459-468) correctly parenthesizes the `edge` condition as `(c === 0 || c === 6) && r >= 0 && r <= 6`.
