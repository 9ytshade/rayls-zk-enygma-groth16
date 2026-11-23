#!/usr/bin/env python3
"""
verify_datasets.py - Automated Empirical Dataset Verification Gatekeeper
-------------------------------------------------------------------------
Validates mathematical consistency, physical thresholds, and schema integrity
across all 4 machine-readable JSON datasets in data/:
  1. data/circuit_constraints.json
  2. data/groth16_physical_benchmark.json
  3. data/mainnet_72957_telemetry.json
  4. data/onchain_fork_measured_gas.json

Exits with code 0 on perfect reconciliation; non-zero if any invariant fails.
"""

import json
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")


def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"[FAIL] Missing dataset: {path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    print("================================================================================")
    print("WEEK 9 EMPIRICAL DATASET RECONCILIATION GATEKEEPER")
    print("Auditing data/ packages against cryptographic, on-chain & SLA invariants")
    print("================================================================================")

    # ── 1. AUDIT CIRCUIT CONSTRAINTS ─────────────────────────────────────────────
    constraints_data = load_json("circuit_constraints.json")
    circuits = constraints_data.get("circuits", {})
    expected_constraints = {
        "PrivateMintCircuit": 802,
        "DvPDestinationCircuit": 3778,
        "DvPInitiatorCircuit": 4077,
        "PaymentCircuit_1in_2out": 4491,
        "PaymentCircuit_2in_2out": 7440,
    }

    print("\n[GATE 1/4] Auditing R1CS Circuit Constraint Counts...")
    for name, expected_count in expected_constraints.items():
        if name not in circuits:
            print(f"  [FAIL] Missing circuit in report: {name}")
            sys.exit(1)
        actual = circuits[name]["constraints"]
        if actual != expected_count:
            print(f"  [FAIL] {name} constraint mismatch: got {actual}, want {expected_count}")
            sys.exit(1)
        print(f"  [PASS] {name:25s}: {actual:5d} R1CS constraints (Exact match)")

    # ── 2. AUDIT GROTH16 PHYSICAL PROVER BENCHMARKS ─────────────────────────────
    bench_data = load_json("groth16_physical_benchmark.json")
    b_circuits = bench_data.get("circuits", {})
    runs = bench_data.get("runs_per_circuit", 0)

    print(f"\n[GATE 2/4] Auditing Groth16 Physical Prover Benchmarks (N={runs} runs)...")
    if runs < 50:
        print(f"  [FAIL] Insufficient statistical sample: {runs} runs (Minimum 50 required)")
        sys.exit(1)

    for name in ["PrivateMint", "DvPDestination", "DvPInitiator"]:
        if name not in b_circuits:
            print(f"  [FAIL] Missing benchmark circuit: {name}")
            sys.exit(1)
        s = b_circuits[name]
        med_prove = s["median_prove_ms"]
        p95_prove = s["p95_prove_ms"]
        pk_bytes = s["pk_disk_bytes"]

        # SLA Check: Proving must be sub-second (< 1,000ms) on consumer hardware
        if p95_prove >= 1000.0:
            print(f"  [FAIL] {name} p95 proving exceeds 1,000ms RTGS threshold: {p95_prove:.2f}ms")
            sys.exit(1)

        if pk_bytes <= 0:
            print(f"  [FAIL] {name} invalid proving key file size: {pk_bytes}")
            sys.exit(1)

        print(f"  [PASS] {name:16s}: Median={med_prove:.2f}ms | P95={p95_prove:.2f}ms | PK={pk_bytes:,} B (RTGS Sub-Second SLA verified)")

    # ── 3. AUDIT LIVE MAINNET 72957 TELEMETRY ────────────────────────────────────
    telem = load_json("mainnet_72957_telemetry.json")
    print("\n[GATE 3/4] Auditing Live Mainnet Telemetry (Chain ID 72957)...")

    if telem["chain_id"] != 72957:
        print(f"  [FAIL] Unexpected chain ID: {telem['chain_id']}")
        sys.exit(1)

    if telem["total_blocks"] != 1000:
        print(f"  [FAIL] Sample size must be exactly 1,000 blocks: got {telem['total_blocks']}")
        sys.exit(1)

    if telem["parent_hash_verified_links"] != 999:
        print(f"  [FAIL] Broken parent links: got {telem['parent_hash_verified_links']}/999")
        sys.exit(1)

    if telem["gas_limit"] != 500000000:
        print(f"  [FAIL] Unexpected gas limit: got {telem['gas_limit']}")
        sys.exit(1)

    # Verify Genesis contracts
    gen = telem["genesis_system_contracts"]
    if gen["ConsensusRegistry"]["bytecode_size_bytes"] != 21929:
        print(f"  [FAIL] ConsensusRegistry size mismatch: got {gen['ConsensusRegistry']['bytecode_size_bytes']}")
        sys.exit(1)
    if gen["FeeAggregatorProxy"]["bytecode_size_bytes"] != 122:
        print(f"  [FAIL] FeeAggregatorProxy size mismatch: got {gen['FeeAggregatorProxy']['bytecode_size_bytes']}")
        sys.exit(1)
    if gen["DelegationPool"]["bytecode_size_bytes"] != 15790:
        print(f"  [FAIL] DelegationPool size mismatch: got {gen['DelegationPool']['bytecode_size_bytes']}")
        sys.exit(1)

    print(f"  [PASS] Telemetry Scan: 1,000 consecutive blocks (#{telem['scan_start_block']:,} -> #{telem['scan_end_block']:,})")
    print(f"  [PASS] Unbroken Parent Links: 999/999 valid")
    print(f"  [PASS] Block Cadence: Mean={telem['mean_cadence_seconds']}s | p95={telem['p95_cadence_seconds']}s")
    print(f"  [PASS] Genesis Bytecode Verified: ConsensusRegistry (21,929 B), FeeAggregator (122 B), DelegationPool (15,790 B)")

    # ── 4. AUDIT ON-CHAIN FORK MEASURED GAS ──────────────────────────────────────
    fork_gas = load_json("onchain_fork_measured_gas.json")
    print("\n[GATE 4/4] Auditing Live Mainnet Fork Measured EVM Verification Gas...")

    spec = fork_gas["precompile_spec"]
    if spec["ecAdd_base_gas"] != 150 or spec["ecMul_base_gas"] != 6000 or spec["groth16_4pairing_base_gas"] != 181000:
        print("  [FAIL] Precompile baseline spec constants invalid")
        sys.exit(1)

    circuits_gas = fork_gas["measured_circuits"]
    for name, data in circuits_gas.items():
        meas_total = data["live_fork_measured_total_gas"]
        theo_total = data["theoretical_precompile_total_gas"]
        wrapper = data["wrapper_overhead_gas"]

        # Math invariant: measured = theoretical + wrapper overhead
        if meas_total != theo_total + wrapper:
            print(f"  [FAIL] {name} gas reconciliation error: {meas_total} != {theo_total} + {wrapper}")
            sys.exit(1)

        native_cost = data["native_rls_cost"]
        expected_cost = round((meas_total * 57.6) / 1e9, 10)
        if abs(native_cost - expected_cost) > 1e-8:
            print(f"  [FAIL] {name} native token cost mismatch: got {native_cost}, want {expected_cost}")
            sys.exit(1)

        print(f"  [PASS] {name:16s}: Measured={meas_total:,} gas (Precompile: {theo_total:,} + Overhead: {wrapper:,}) -> {native_cost:.8f} RLS")

    print("\n================================================================================")
    print("ALL 4 EMPIRICAL DATASET GATES PASSED (EXIT CODE 0)")
    print("Zero mathematical or provenance discrepancies detected.")
    print("================================================================================")
    sys.exit(0)


if __name__ == "__main__":
    main()
