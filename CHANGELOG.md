# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-02

### Added
- Smart Manufacturing Digital Twin System design document (v1.1)
  - OPC UA information model with complete NodeId definitions for 7 devices
  - Python digital twin class hierarchy (DigitalTwinBase, CNCTwin, RobotTwin, AGVTwin, WarehouseTwin)
  - Data Shadow model (Happy/Nil/Empty/Error four-state)
  - Double DQN reinforcement learning scheduling engine
  - Purdue model industrial security architecture (Level 0-5)
  - Unified production/simulation architecture (ADR-8)
  - Physics-based ODE simulation with RK4 integration
  - MES-PLC interaction sequences (happy path, fault recovery, robot loading, AGV transport)
  - 10 fault scenario analyses with FMEA scoring
  - 8 Architecture Decision Records (ADRs)
  - 43 test cases across 10 test files
  - 4-phase implementation roadmap (Week 1-18)
  - 52-term glossary covering OPC UA, digital twins, RL scheduling, industrial security

### Architecture Decisions
- ADR-1: OPC UA over MQTT + Sparkplug B for device communication
- ADR-2: Python asyncio for digital twin runtime
- ADR-3: Double DQN for dynamic scheduling
- ADR-4: Purdue model + OPC UA DMZ security architecture
- ADR-5: PostgreSQL + TimescaleDB hybrid storage
- ADR-6: Data Shadow four-state model
- ADR-7: JSON over OPC UA for application layer
- ADR-8: Unified production/simulation architecture

### Project Setup
- CLAUDE.md with project guidance
- GitHub Issues backlog configuration
- Default triage labels (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix)
- Single-context domain docs layout
