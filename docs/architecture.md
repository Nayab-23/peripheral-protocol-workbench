# Architecture

This repo is intentionally simulator-first.

Core layers:

- `protocol.py`
  - binary frame format, checksum, and parse rules
- `transports.py`
  - transport abstraction with a loopback reference implementation
- `simulator.py`
  - replay streams and fault injection helpers
- future serial adapters
  - UART transport, session logging, and fault visualization
