#!/usr/bin/env python3
"""
Week 9 Live Rayls Mainnet (Chain ID 72957) Telemetry & Groth16 Calldata Forensics
---------------------------------------------------------------------------------
Scans N = 1,000 consecutive canonical blocks from https://mainnet-rpc.rayls.com to measure:
  1. Unbroken parentHash continuity across 1,000 blocks (step=1)
  2. Observed inter-block cadence (min, median, p95, mean)
  3. Block gasLimit ceiling (500,000,000 gas headroom) and live gasPrice
  4. Bytecode verification of core Genesis system contracts
  5. Calldata economics of submitting Groth16 proofs (256 bytes) and public inputs (4-8 signals)
     under EIP-2028 rules at current live gas price.

Strictly read-only RPC probe; emits machine-readable JSON capture in data/mainnet_72957_telemetry.json.
"""

import concurrent.futures
import json
import os
import statistics
import time
import urllib.request

RPC_URL = "https://mainnet-rpc.rayls.com"
CHAIN_ID_EXPECTED = 72957
BLOCK_SAMPLE_COUNT = 1000
MAX_WORKERS = 16

GENESIS_SYSTEM_ADDRESSES = {
    "ConsensusRegistry": "0x07E17e17e17e17e17e17e17e17e17e17e17e17e1",
    "FeeAggregatorProxy": "0x07E17e17e17e17e17e17e17e17e17e17e17e17e3",
    "DelegationPool": "0x07e17e17e17e17e17e17e17e17E17e17e17e17e9",
}


def rpc_call(method, params, timeout=15):
    payload = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1}).encode("utf-8")
    req = urllib.request.Request(
        RPC_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) RaylsResearchZK/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        if "error" in data:
            raise RuntimeError(f"RPC error for {method}: {data['error']}")
        return data["result"]


def fetch_block(num):
    for attempt in range(3):
        try:
            blk = rpc_call("eth_getBlockByNumber", [hex(num), False])
            return {
                "number": int(blk["number"], 16),
                "hash": blk["hash"],
                "parentHash": blk["parentHash"],
                "timestamp": int(blk["timestamp"], 16),
                "gasLimit": int(blk["gasLimit"], 16),
                "gasUsed": int(blk["gasUsed"], 16),
                "baseFeePerGas": int(blk.get("baseFeePerGas", "0x0"), 16),
                "txCount": len(blk.get("transactions", [])),
            }
        except Exception:
            time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch block {num} after 3 attempts")


def main():
    print(f"Connecting to Rayls Public Chain Mainnet: {RPC_URL}...")
    chain_id = int(rpc_call("eth_chainId", []), 16)
    if chain_id != CHAIN_ID_EXPECTED:
        raise ValueError(f"Unexpected chain ID: got {chain_id}, want {CHAIN_ID_EXPECTED}")
    print(f"  [PASS] Verified Chain ID: {chain_id}")

    latest_blk = rpc_call("eth_getBlockByNumber", ["latest", False])
    finalized_blk = rpc_call("eth_getBlockByNumber", ["finalized", False])
    gas_price_wei = int(rpc_call("eth_gasPrice", []), 16)
    gas_price_gwei = gas_price_wei / 1e9

    tip_block = int(latest_blk["number"], 16)
    finalized_block = int(finalized_blk["number"], 16)
    start_block = tip_block - BLOCK_SAMPLE_COUNT + 1

    print(f"  [PASS] Canonical Mainnet Tip: #{tip_block:,} | Finalized: #{finalized_block:,}")
    print(f"  [PASS] Current Gas Price: {gas_price_gwei:.2f} Gwei ({gas_price_wei} Wei)")
    print(f"Sampling {BLOCK_SAMPLE_COUNT} consecutive blocks (#{start_block:,} -> #{tip_block:,}) with {MAX_WORKERS} workers...")

    numbers = list(range(start_block, tip_block + 1))
    blocks = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for res in executor.map(fetch_block, numbers):
            blocks.append(res)
            if len(blocks) % 250 == 0 or len(blocks) == BLOCK_SAMPLE_COUNT:
                print(f"  Fetched {len(blocks)}/{BLOCK_SAMPLE_COUNT} blocks...")

    blocks.sort(key=lambda b: b["number"])

    # Parent hash continuity
    unbroken_links = 0
    intervals = []
    gas_limits = []

    for i in range(1, len(blocks)):
        prev = blocks[i - 1]
        curr = blocks[i]
        if curr["parentHash"].lower() == prev["hash"].lower() and curr["number"] == prev["number"] + 1:
            unbroken_links += 1
        dt = curr["timestamp"] - prev["timestamp"]
        intervals.append(dt)
        gas_limits.append(curr["gasLimit"])

    intervals_sorted = sorted(intervals)
    mean_cadence = statistics.mean(intervals)
    median_cadence = statistics.median(intervals)
    p95_cadence = intervals_sorted[int(len(intervals_sorted) * 0.95)]
    min_cadence = intervals_sorted[0]
    max_cadence = intervals_sorted[-1]
    block_gas_limit = gas_limits[-1]

    print(f"\nCadence Analysis (N = {len(intervals)} intervals):")
    print(f"  Mean:   {mean_cadence:.4f} s")
    print(f"  Median: {median_cadence:.2f} s")
    print(f"  p95:    {p95_cadence:.2f} s")
    print(f"  Range:  [{min_cadence}s .. {max_cadence}s]")
    print(f"  Parent Hash Continuity: {unbroken_links}/{len(blocks)-1} valid links")
    print(f"  Block Gas Limit: {block_gas_limit:,} gas")

    # Genesis System Contracts inspection
    print("\nInspecting Genesis System Contracts:")
    contract_bytes = {}
    for name, addr in GENESIS_SYSTEM_ADDRESSES.items():
        code = rpc_call("eth_getCode", [addr, hex(tip_block)])
        byte_len = (len(code) - 2) // 2 if code.startswith("0x") else len(code) // 2
        contract_bytes[name] = {
            "address": addr,
            "bytecode_size_bytes": byte_len,
        }
        print(f"  {name:20s} ({addr}): {byte_len:,} bytes")

    # ZK Calldata Economics: 256-byte Groth16 Proof + Public Inputs (EIP-2028 rules: 16 gas/byte)
    proof_bytes = 256  # 8 uint256 words: [A.x, A.y, B.x0, B.x1, B.y0, B.y1, C.x, C.y]
    proof_calldata_gas = proof_bytes * 16  # 4,096 gas

    calldata_profiles = {
        "PrivateMint": {
            "public_inputs_count": 4,
            "public_input_bytes": 4 * 32,
            "public_input_calldata_gas": 4 * 32 * 16,
            "total_calldata_gas": proof_calldata_gas + (4 * 32 * 16),
            "calldata_cost_rls": ((proof_calldata_gas + (4 * 32 * 16)) * gas_price_wei) / 1e18,
        },
        "DvPDestination": {
            "public_inputs_count": 6,
            "public_input_bytes": 6 * 32,
            "public_input_calldata_gas": 6 * 32 * 16,
            "total_calldata_gas": proof_calldata_gas + (6 * 32 * 16),
            "calldata_cost_rls": ((proof_calldata_gas + (6 * 32 * 16)) * gas_price_wei) / 1e18,
        },
        "DvPInitiator": {
            "public_inputs_count": 8,
            "public_input_bytes": 8 * 32,
            "public_input_calldata_gas": 8 * 32 * 16,
            "total_calldata_gas": proof_calldata_gas + (8 * 32 * 16),
            "calldata_cost_rls": ((proof_calldata_gas + (8 * 32 * 16)) * gas_price_wei) / 1e18,
        },
    }

    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "rpc_endpoint": RPC_URL,
        "chain_id": chain_id,
        "scan_start_block": start_block,
        "scan_end_block": tip_block,
        "pinned_canonical_block": tip_block,
        "finalized_block": finalized_block,
        "pinned_block_hash": blocks[-1]["hash"],
        "total_blocks": BLOCK_SAMPLE_COUNT,
        "consecutive_step": 1,
        "parent_hash_verified_links": unbroken_links,
        "mean_cadence_seconds": round(mean_cadence, 4),
        "median_cadence_seconds": round(median_cadence, 2),
        "p95_cadence_seconds": round(p95_cadence, 2),
        "min_cadence_seconds": min_cadence,
        "max_cadence_seconds": max_cadence,
        "gas_price_wei": gas_price_wei,
        "baseline_gas_price_gwei": gas_price_gwei,
        "gas_limit": block_gas_limit,
        "genesis_system_contracts": contract_bytes,
        "zk_calldata_economics": calldata_profiles,
    }

    out_file = os.path.join(os.path.dirname(__file__), "..", "data", "mainnet_72957_telemetry.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\n[PASS] Machine-readable telemetry saved to {out_file}")


if __name__ == "__main__":
    main()
