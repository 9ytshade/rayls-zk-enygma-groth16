#!/usr/bin/env bash
# run_research_stage.sh - Modular Research Stage Runner for Week 9
# Zero-Knowledge Proof Anatomy: Benchmarking Groth16 Proving on Rayls Enygma Circuits
# Usage: ./scripts/run_research_stage.sh [1|2|3|4|5|6|all]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

PYTHON_BIN="$(command -v python3 || command -v python)"
FORGE_BIN="${HOME}/.foundry/bin/forge"
GO_BIN="${HOME}/.local/go/bin/go"

# Formatting colors
C_RESET="\033[0m"
C_BOLD="\033[1m"
C_YELLOW="\033[1;33m"
C_PURPLE="\033[1;35m"
C_GREEN="\033[1;32m"
C_BLUE="\033[1;34m"

print_header() {
    echo -e "\n${C_BOLD}${C_PURPLE}================================================================================${C_RESET}"
    echo -e "${C_BOLD}${C_YELLOW}$1${C_RESET}"
    echo -e "${C_BOLD}${C_PURPLE}================================================================================${C_RESET}\n"
}

stage_1() {
    print_header "STAGE 1: Upstream Circuit Constraints & Physical Groth16 Prover Benchmarks"
    echo -e "${C_BLUE}Verifying pre-compiled empirical dataset packages...${C_RESET}"
    if [ -f "data/circuit_constraints.json" ] && [ -f "data/groth16_physical_benchmark.json" ]; then
        echo -e "${C_GREEN}[PASS] Circuit constraints package present: data/circuit_constraints.json${C_RESET}"
        echo -e "${C_GREEN}[PASS] Prover physical benchmark package present: data/groth16_physical_benchmark.json${C_RESET}"
    else
        echo -e "${C_YELLOW}Compiling circuits and running physical prover benchmarks (N=50)...${C_RESET}"
        "$GO_BIN" run scripts/bench_circuits.go --iterations 50
    fi
}

stage_2() {
    print_header "STAGE 2: Live Rayls Mainnet 72957 Telemetry & Precompile Gas Verification"
    echo -e "${C_BLUE}Verifying live 1,000-block telemetry capture...${C_RESET}"
    "$PYTHON_BIN" scripts/verify_datasets.py
}

stage_3() {
    print_header "STAGE 3: Three-State Invariant Foundry Test Suite Execution"
    echo -e "${C_BLUE}Executing 16 Foundry tests across ZKInvariantAudit and ZKMainnetFork...${C_RESET}"
    "$FORGE_BIN" test -vv
}

stage_4() {
    print_header "STAGE 4: Upstream Rayls Enygma gnark Circuit Invariant Tests"
    echo -e "${C_BLUE}Executing upstream Enygma DvP circuit tests (pinned commit a9b06c0)...${C_RESET}"
    if [ -d "/home/nightshade/rayls_src/Enygma/enygma_dvp/gnark_circuits" ]; then
        (cd /home/nightshade/rayls_src/Enygma/enygma_dvp/gnark_circuits && \
         "$GO_BIN" test -v ./test/templates -run TestDvpInitiatorCircuit)
    else
        echo -e "${C_YELLOW}Upstream repository path not found in local workspace; skipping local Go run.${C_RESET}"
    fi
}

stage_5() {
    print_header "STAGE 5: Visual Asset Suite & Diagram Verification"
    echo -e "${C_BLUE}Verifying generated technical diagram and cover image assets...${C_RESET}"
    local missing=0
    for asset in \
        "assets/cover_image_groth16_enygma.png" \
        "assets/diagram_1_groth16_rtgs_pipeline.png" \
        "assets/diagram_2_circuit_constraint_anatomy.png" \
        "assets/diagram_3_enygma_vulnerability_matrix.png" \
        "assets/diagram_4_physical_benchmarks_and_gas.png" \
        "assets/diagram_5_poseidon_hash_permutation_matrix.png" \
        "assets/diagram_6_confidential_dvp_atomic_settlement.png" \
        "assets/diagram_7_mainnet_telemetry_cadence_distribution.png"; do
        if [ -f "$asset" ]; then
            echo -e "${C_GREEN}[PASS] Asset present: $asset ($(wc -c < "$asset") bytes)${C_RESET}"
        else
            echo -e "${C_YELLOW}[MISSING] Asset not found: $asset${C_RESET}"
            missing=1
        fi
    done

    if [ "$missing" -eq 1 ]; then
        echo -e "${C_YELLOW}Regenerating missing assets via Python generator...${C_RESET}"
        "$PYTHON_BIN" scripts/generate_diagrams.py --diagram all
        "$PYTHON_BIN" scripts/generate_cover_image.py
    fi
}

stage_6() {
    print_header "STAGE 6: Empirical Dataset Gatekeeper Verification"
    echo -e "${C_BLUE}Running verify_datasets.py gatekeeper across all 4 gates...${C_RESET}"
    "$PYTHON_BIN" scripts/verify_datasets.py
}

STAGE="${1:-all}"

case "$STAGE" in
    1) stage_1 ;;
    2) stage_2 ;;
    3) stage_3 ;;
    4) stage_4 ;;
    5) stage_5 ;;
    6) stage_6 ;;
    all)
        stage_1
        stage_2
        stage_3
        stage_4
        stage_5
        stage_6
        print_header "ALL 6 RESEARCH STAGES EXECUTED SUCCESSFULLY"
        ;;
    *)
        echo "Usage: $0 [1|2|3|4|5|6|all]"
        exit 1
        ;;
esac
