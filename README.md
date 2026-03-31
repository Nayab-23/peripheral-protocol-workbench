# Peripheral Protocol Workbench

`peripheral-protocol-workbench` is the planned Week 4 communication-systems repo for the embedded month. It focuses on packet definitions, serial-style transport abstractions, replay, and fault injection so protocol work can continue even when hardware is missing.

## Current Scope

- typed frame model with checksum validation
- loopback transport abstraction
- simulator-side replay and fault injection helpers
- tests for encode/decode and replay behavior

## Week 4 Direction

- UART-style serial transport
- simulated I2C/SPI/CAN-like message modeling
- dashboard or CLI session inspection
- recorded replay sessions and injected error cases

## Quick Start

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .[dev]
pytest
python scripts/replay_demo.py
python scripts/replay_session.py <session_file> [--inject-bad-checksum]
```
