# Rayls Enygma Zero-Knowledge Proof Architecture
## Groth16 Proving Benchmarks, gnark R1CS Constraint Dissection & EVM Precompile Gas Forensics

[![Verification Gate](https://github.com/9ytshade/rayls-zk-enygma-groth16/actions/workflows/verify.yml/badge.svg)](https://github.com/9ytshade/rayls-zk-enygma-groth16/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Foundry](https://img.shields.io/badge/Foundry-1.8.6-orange.svg)](https://getfoundry.sh/)
[![Go](https://img.shields.io/badge/Go-1.27.4-cyan.svg)](https://golang.org/)
[![Solidity](https://img.shields.io/badge/Solidity-0.8.24-lightgrey.svg)](https://soliditylang.org/)
[![Upstream Commit](https://img.shields.io/badge/Upstream-a9b06c00-purple.svg)](https://github.com/raylsnetwork/Enygma)

An empirical investigation of the zero-knowledge proving system powering **Rayls Enygma**, the privacy layer for tokenized banking and Delivery-versus-Payment (DvP) settlement on Rayls Sovereign subnets. This repository contains reproducible Go gnark benchmarking suites, Three-State invariant testbenches, live Mainnet (Chain ID 72957) telemetry datasets, EVM pairing precompile gas forensics, and the complete institutional research monograph.

**Master Technical Monograph:** [ZERO_KNOWLEDGE_GROTH16_ENYGMA_DEEP_DIVE.md](ZERO_KNOWLEDGE_GROTH16_ENYGMA_DEEP_DIVE.md)  
**Terminal Demonstration Showcase:** Executed via [`scripts/record_demo_showcase.sh`](scripts/record_demo_showcase.sh) (6-Stage Verification Runner)  
**Visual Asset Suite:** 8 Brand-Compliant Visual Artifacts in [`assets/`](assets/)  
**Cross-Post Package:** [CROSS_POST_SUMMARY.md](CROSS_POST_SUMMARY.md) (X/Twitter Thread, Quote-Tweet & Discord Template)

---

### Executive Architecture Overview

Rayls Enygma implements confidential asset transfers and atomic DvP settlements using Groth16 zk-SNARKs over the BN254 (alt_bn128) elliptic curve pairing group. Client institutions generate cryptographic proofs locally inside their Sovereign subnets, ensuring transaction amounts, counterparty identities, and account balances remain confidential while enforcing conservation of value on-chain.

```
+----------------------------------------------------------------------------------------------------+
|                                    RAYLS ENYGMA ZK ARCHITECTURE                                    |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|   [CLIENT PROVER (SOVEREIGN SUBNET)]                                                               |
|   +--------------------------------------------------------------------------------------------+   |
|   | Witness Generation (Private Balances, Nonces, Merkle Paths)                                 |   |
|   | gnark BN254 R1CS Constraint Engine (Poseidon Hashing, Range Checks)                         |   |
|   | Groth16 Prover -> Generates 128-byte proof: [A in G1 (64B), B in G2 (128B), C in G1 (64B)] |   |
|   +--------------------------------------------------------------------------------------------+   |
|                                                |                                                   |
|                                                v                                                   |
|   [ON-CHAIN SETTLEMENT (CHAIN 72957 / SUB-NET)]                                                   |
|   +--------------------------------------------------------------------------------------------+   |
|   | GenericGroth16Verifier.sol / Verifier.sol                                                  |   |
|   | - Accumulates Public Signals: Linear combinations via Precompile 6 (ecAdd) & 7 (ecMul)      |   |
|   | - Evaluates BN254 Pairing Identity: Precompile 8 (ecPairing) with k=4 pairings             |   |
|   |   e(A, B) * e(-alpha, beta) * e(-K_pub, gamma) * e(-C, delta) == 1                         |   |
|   | - Atomic State Transition: Updates Nullifier Registry & Merkle Commitments                 |   |
|   +--------------------------------------------------------------------------------------------+   |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
```

---

### Key Empirical Findings

1. **Physical Constraint Scaling Across 5 Circuits:**
   - `PrivateMintCircuit`: **802 constraints** (5 public inputs, 3 secret witnesses, Merkle depth 0).
   - `DvPDestinationCircuit`: **3,778 constraints** (7 public inputs, 18 secret witnesses, Merkle depth 8).
   - `DvPInitiatorCircuit`: **4,077 constraints** (9 public inputs, 19 secret witnesses, Merkle depth 8).
   - `PaymentCircuit (1-in, 2-out)`: **4,491 constraints** (8 public inputs, 19 secret witnesses, Merkle depth 8).
   - `PaymentCircuit (2-in, 2-out)`: **7,440 constraints** (11 public inputs, 31 secret witnesses, Merkle depth 8).

2. **Client-Side Prover Performance (Physical Consumer CPU, N=50 Runs):**
   - Proving completes in **115.52ms to 415.35ms median** on dual-core hardware (Intel Core i3-3110M @ 2.40 GHz):
     - `PrivateMint`: **115.52ms median** (p95: 217.31ms, proving key: 145 KB)
     - `DvPDestination`: **404.55ms median** (p95: 583.16ms, proving key: 640 KB)
     - `DvPInitiator`: **415.35ms median** (p95: 717.33ms, proving key: 679 KB)
   - Worst-case 95th percentile proving is **717.33ms** on the heaviest circuit (`DvPInitiator`), strictly fulfilling the $\le 1,000\text{ms}$ RTGS wholesale banking threshold with a **28.3% safety margin** without GPUs.
   - Client peak heap allocation is strictly **4.36 MB to 11.56 MB**, enabling lightweight browser and microservice deployment.

3. **EVM Verification Gas & Precompile Overhead:**
   - Groth16 verification requires **181,138 gas base** (4-pairing evaluation via precompile 8) plus linear combination accumulation gas:
     - Precompile 6 (`ecAdd`): **279 gas**
     - Precompile 7 (`ecMul`): **6,129 gas**
     - Precompile 8 (`ecPairing`): **181,138 gas**
   - Solidity memory packing and staticcall dispatch add $+13,749$ to $+19,689$ gas wrapper overhead.
   - Measured live fork execution on Rayls Public Chain (Chain ID 72957):
     - `PrivateMint`: **219,199 gas** (precompile: 205,450 + wrapper overhead: 13,749 gas; 0.01262 RLS at 57.60 Gwei)
     - `DvPDestination`: **234,468 gas** (precompile: 217,750 + wrapper overhead: 16,718 gas; 0.01350 RLS)
     - `DvPInitiator`: **249,739 gas** (precompile: 230,050 + wrapper overhead: 19,689 gas; 0.01438 RLS, delivering a **>99.99% cost reduction** vs Ethereum L1).

4. **Forensic Circuit Invariants:**
   - Unconstrained Public Input Defense: `api.AssertIsDifferent(circuit.StCounterVault, 0)` in `DvPInitiatorCircuit` prevents unconstrained counterparty assignment.
   - Cross-Leg Binding: Strict equality checks (`StMessage == StCommitA` in initiator, `StMessage == commitB` in destination) prevent proof re-binding attacks across swap legs.
   - Field Wraparound Prevention: `valuebound.Assert(api, v)` bounds all balance inputs to $0 \le v < 10^{36}$, preventing field wrapping modulo $r$.

---

### Hardware & Toolchain Environment

All benchmarks and tests were executed on the following physical environment:

| Component | Specification |
|:---|:---|
| **Host Processor** | Intel(R) Core(TM) i3-3110M CPU @ 2.40GHz (4 logical threads, x86_64) |
| **System Memory** | 3.8 GiB RAM, 4.0 GiB Swap |
| **Operating System** | Ubuntu 24.04 LTS via WSL2 on Windows 11 |
| **Go Toolchain** | Go version `go1.27.4 linux/amd64` |
| **Foundry Suite** | `forge 1.8.6` (commit `6bad0a66de`) |
| **Solidity Compiler** | `solc 0.8.24+commit.e11b9ed9.Linux.g++` |
| **Python Runtime** | Python 3.12.3 with `numpy`, `matplotlib`, `requests` |
| **Upstream Source** | `raylsnetwork/Enygma` commit `a9b06c00cc4076b035c2d9afd5e2ca70b7eae194` |
| **Target Network** | Rayls Public Chain Mainnet (Chain ID `72957`, RPC `https://mainnet-rpc.rayls.com`) |

---

### Four-Domain Evidence Architecture

To maintain strict epistemic rigor, all data and findings are classified into four decoupled domains:

1. **Domain 1: Live On-Chain Telemetry (Chain ID 72957):** 1,000 consecutive blocks scanned (#15,047,066 to #15,048,065) with 999/999 parent-link validations (100.0% integrity). Mean block cadence is 1.3423s (median: 1.0s, p95: 2.0s, strictly within 0s to 2s). Baseline gas price: 57.60 Gwei, gas limit: 500,000,000 gas. Genesis bytecodes verified: ConsensusRegistry (21,929 bytes), FeeAggregatorProxy (122 bytes), DelegationPool (15,790 bytes).
2. **Domain 2: Upstream Codebase Forensics:** Compiled directly from pinned commit `a9b06c00` of `raylsnetwork/Enygma`.
3. **Domain 3: Controlled Local Invariant Testbenches:** Authored reference prototypes evaluating mathematical invariants under standard EVM rules.
4. **Domain 4: Institutional & Regulatory Standards:** CPMI-IOSCO Principle 8, Banco Central do Brasil (BCB) Drex pilot specifications, and Brazilian Lei Complementar 105/2001.

---

### Repository Structure

```
├── ZERO_KNOWLEDGE_GROTH16_ENYGMA_DEEP_DIVE.md  # Master institutional research monograph
├── CROSS_POST_SUMMARY.md                       # X/Twitter thread & Discord release templates
├── assets/                                     # 8 brand-compliant visual diagrams & cover
├── contracts/
│   ├── ZKVerifierTestbench.sol                 # Reference verifier prototype modeling Enygma verification
│   └── interfaces/                             # Precompile and verifier interfaces
├── test/
│   ├── ZKInvariantAudit.t.sol                  # Three-State invariant audit suite (Happy, Revert, Fuzz)
│   └── ZKMainnetFork.t.sol                     # Live Chain 72957 fork gas execution test
├── data/
│   ├── circuit_constraints.json                # R1CS constraint counts across 5 circuits
│   ├── groth16_physical_benchmark.json         # N=50 physical prover latency & memory stats
│   ├── mainnet_72957_telemetry.json            # 1,000 consecutive block telemetry dump
│   └── onchain_fork_measured_gas.json          # Live fork measured verification gas & overhead
├── scripts/
│   ├── bench_circuits.go                       # Go benchmark harness (N=50 runs, memory profiling)
│   ├── generate_diagrams.py                    # Pillow generator for 7 technical diagrams
│   ├── generate_cover_image.py                 # Pillow generator for signature gradient cover
│   ├── run_research_stage.sh                   # Modular stage runner (stages 1 to 6)
│   ├── record_demo_showcase.sh                 # Full reproduction showcase runner
│   └── verify_datasets.py                      # Dataset validation gatekeeper
├── docs/                                       # Foundation documents (PRD, TRD, Architecture, Invariants)
└── foundry.toml                                # Foundry build and fork configuration
```

---

### Quick Start & Reproduction Guide

#### Prerequisites
Ensure Go 1.22+, Foundry (`forge`), and Python 3.10+ are installed.

```bash
# 1. Clone repository
git clone https://github.com/9ytshade/rayls-zk-enygma-groth16.git
cd rayls-zk-enygma-groth16

# 2. Run automated verification gatekeeper
bash scripts/record_demo_showcase.sh

# 3. Run individual research stages
bash scripts/run_research_stage.sh 1   # Toolchain and environment pre-flight
bash scripts/run_research_stage.sh 2   # Circuit constraint compilation and forensic audit
bash scripts/run_research_stage.sh 3   # Live Mainnet 72957 telemetry scan (1,000 blocks)
bash scripts/run_research_stage.sh 4   # Physical CPU Groth16 proving benchmarks
bash scripts/run_research_stage.sh 5   # Three-State invariant audit suite (Foundry)
bash scripts/run_research_stage.sh 6   # Live Mainnet fork gas execution & dataset gate
```

---

### Epistemic Boundary Notice
*This test suite evaluates an illustrative reference implementation constructed to model the documented invariants of Rayls Enygma. It demonstrates mathematical and state-machine principles in an isolated EVM runtime, but does not constitute an audit of Rayls' closed-source or enterprise production nodes. Cryptographic state commitments provide technical settlement finality; statutory legal finality remains governed by judicial jurisdiction and central bank operational frameworks (CPMI-IOSCO Principle 8).*
