# PLC System Design & Communication

**Course:** SYI700 System Integration — University West
**Author:** Aanu Olakunle

## Overview

This project implements a Beckhoff PLC-based control system for an automated coffee preparation process. The PLC orchestrates communication between four subsystems — **SCADA**, **Universal Robot (UR)**, **AGV**, and **Crane Robot** — using OPC UA and ADS communication protocols.

The system coordinates the full coffee order lifecycle: receiving an order via SCADA, commanding the UR to place a cup, dispatching the AGV between stations, filling the cup via the Crane, and delivering the finished order.

## System Architecture

```
┌─────────┐  ADS   ┌─────────────┐  OPC UA  ┌─────────┐
│  SCADA  │◄──────►│             │◄────────►│   UR    │
└─────────┘        │   Beckhoff  │          └─────────┘
                   │     PLC     │
┌─────────┐  ADS   │  (TwinCAT3) │  OPC UA  ┌─────────┐
│  Crane  │◄──────►│             │◄────────►│   AGV   │
└─────────┘        └─────────────┘          └─────────┘
```

### Communication Protocols

| Subsystem | Protocol | Direction |
|-----------|----------|-----------|
| SCADA | ADS | Bidirectional |
| Universal Robot (UR) | OPC UA | Bidirectional |
| AGV | OPC UA | Bidirectional |
| Crane Robot | ADS | Bidirectional |

### Signal Convention

- **`ix` prefix** — Input signals received by the PLC (e.g., `ixAGVAtHome`)
- **`qx` prefix** — Output signals sent by the PLC (e.g., `qxMoveAGVToCrane`)
- **`requestReceived`** — Handshake signal used to confirm receipt of commands between PLC and subsystems

## Operation Flow

1. **Setup phase** (`qxStatus = 5`) — All subsystems are moved to home positions (UR, AGV, Crane)
2. **Order received** — SCADA sends order ID (1 = Small Cup, 2 = Large Cup) and start signal
3. **UR places cup** on AGV
4. **AGV moves to Crane** station
5. **Crane fills cup** based on order
6. **AGV moves to UR** station
7. **UR places lid** and delivers cup
8. **Operation complete** (`qxStatus = 200`)

## Project Files

| File | Description |
|------|-------------|
| `agv.py` | OPC UA client for the AGV subsystem — connects to the PLC, subscribes to node changes, and handles AGV movement commands via a handshake protocol |
| `SystemsIntegrationProject.tnzip` | TwinCAT 3 project archive containing the PLC program |
| `Beckhoff_OpcUaServer.der` / `.pem` | Security certificates for OPC UA encrypted communication (Basic256Sha256, SignAndEncrypt) |
| `Black Box - *.png` | Black box diagrams for each subsystem (AGV, Crane, SCADA, UR) |
| `PLC SubSystem Documentation - Full.pdf` | Full PLC subsystem documentation with signal definitions, status codes, and process flow charts |
| `PLC SubTask.pdf` | Subtask description and responsibility breakdown |

## AGV Client (`agv.py`)

The AGV Python client connects to the Beckhoff PLC via OPC UA with encrypted communication:

- **Connection:** `opc.tcp://169.254.70.51:4840` with Basic256Sha256 security
- **Subscription-based:** Monitors PLC node changes in real time (200ms interval)
- **Handshake protocol:** Uses `requestReceived` flag to acknowledge commands before executing movement
- **State machine:** Responds to `qxStatus` codes to determine whether the system is in setup mode or operation mode

### Prerequisites

```bash
pip install opcua
```

### Usage

```bash
python agv.py
```

> Requires network access to the Beckhoff PLC and valid OPC UA certificates.

## Status Codes

### Operation Status (`qxStatus`)

| Code | Description |
|------|-------------|
| 0 | Initializing |
| 5 | Setting up all systems |
| 10 | Ready to start operation |
| 20–40 | UR cup placement sequence |
| 50–70 | AGV move to Crane |
| 80–100 | Crane fill cup |
| 110–130 | AGV move to UR |
| 140–160 | UR place lid |
| 170–190 | UR deliver cup |
| 200 | Operation completed |

### Setup Status (`qxSetupStatus`)

| Code | Description |
|------|-------------|
| 1000 | Initializing |
| 1100–1300 | Move UR to Home |
| 1400–1600 | Move AGV to Home |
| 1700–1900 | Move Crane to Home |

## Tools & Technologies

- **Beckhoff TwinCAT 3** — PLC programming and runtime
- **OPC UA** — Communication with UR and AGV subsystems
- **ADS (Automation Device Specification)** — Communication with SCADA and Crane subsystems
- **Python** (`opcua` library) — OPC UA client implementation
