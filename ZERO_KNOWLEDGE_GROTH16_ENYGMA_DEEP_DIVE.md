# Zero-Knowledge Proof Anatomy: Benchmarking Groth16 Proving on Rayls Enygma Circuits
## Empirical CPU Prover Latencies, EVM Pairing Gas, and Cross-Subnet Delivery-versus-Payment Invariants

![Cover: Zero-Knowledge Proof Anatomy](assets/cover_image_groth16_enygma.png)

> **Document Classification:** Institutional Technical Research Monograph  
> **Author:** The Rail Community Content & Research Quest (Week 9)  
> **Target Audience:** Enterprise Blockchain Architects, Central Bank Digital Currency (CBDC) Engineers, Cryptographic Auditors  
> **Empirical Datasets:** [circuit_constraints.json](file:///C:/Users/9ytshade/Desktop/Rayls/Week_9_Zero_Knowledge_Groth16_Enygma/data/circuit_constraints.json) | [groth16_physical_benchmark.json](file:///C:/Users/9ytshade/Desktop/Rayls/Week_9_Zero_Knowledge_Groth16_Enygma/data/groth16_physical_benchmark.json) | [mainnet_72957_telemetry.json](file:///C:/Users/9ytshade/Desktop/Rayls/Week_9_Zero_Knowledge_Groth16_Enygma/data/mainnet_72957_telemetry.json) | [onchain_fork_measured_gas.json](file:///C:/Users/9ytshade/Desktop/Rayls/Week_9_Zero_Knowledge_Groth16_Enygma/data/onchain_fork_measured_gas.json)  
> **Repository:** `9ytshade/rayls-zk-enygma-groth16`  
> **Reproduction Showcase:** Executed via `scripts/record_demo_showcase.sh` (6-Stage Terminal Demonstration)  
> **Commit Hash:** Pinned Upstream Rayls Enygma SHA `a9b06c00cc4076b035c2d9afd5e2ca70b7eae194`  

---

## Scope & Epistemic Boundary Notice

> [!NOTE]
> **Mandatory Scope Declaration:**  
> This research monograph evaluates an illustrative reference testbench (`ZKVerifierTestbench.sol`) alongside physical benchmarks of Rayls' upstream open-source `enygma_dvp` circuit codebase. Gas measurements captured via local Foundry fork of Rayls Public Mainnet (Chain ID `72957`, block tip `#15047066` to `#15048439`) reflect standard EVM precompile execution rules and do not establish the internal execution queue dynamics or private gossip performance of proprietary bank nodes. Furthermore, cryptographic state commitments provide technical settlement finality; statutory legal finality remains governed by judicial jurisdiction, central bank operational frameworks, and bilateral master netting agreements under CPMI-IOSCO Principle 8.

---

## 1. Executive Summary & The Institutional RTGS Proving Problem

Central bank digital currency pilots and interbank settlement systems operate under strict real-time gross settlement (RTGS) requirements. Under international standards established by the Committee on Payments and Market Infrastructures and the International Organization of Securities Commissions (CPMI-IOSCO Principle 8), wholesale financial market infrastructures must complete end-to-end settlement deterministically and continuously during operating hours. In pilots such as the Central Bank of Brazil (BCB) Drex project, privacy-preserving zero-knowledge transactions must balance two opposing forces:

1. **Strict Banking Secrecy:** Protecting balance amounts, counterparty account identifiers, and transaction volumes from unauthorized market visibility (complying with Brazilian Complementary Law 105/2001, EU GDPR Article 5, and US GLBA).
2. **Sub-Second Latency Budgets:** Generating and verifying zero-knowledge proofs rapidly enough to maintain real-time liquidity flow without causing queuing gridlock or requiring dedicated datacenter GPU clusters at each member bank gateway.

A central engineering question facing financial institutions deploying Rayls Sovereign Subnets is whether succinct zero-knowledge proof systems (Groth16 on BN254) can physically meet sub-second proving thresholds on standard consumer client hardware, and what exact on-chain EVM verification overhead is incurred when settling confidential Delivery-versus-Payment (DvP) commitments to the decentralized Rayls Public Chain (Chain ID `72957`).

```
+---------------------------------------------------------------------------------------------------------+
|                                    WEEK 9 CORE EMPIRICAL FINDINGS                                       |
+---------------------------------------------------------------------------------------------------------+
|  1. RTGS Proving SLA Compliance : 100% of physical prover runs meet the <= 1,000ms RTGS threshold on     |
|                                   consumer dual-core hardware. DvP Initiator median prove time is        |
|                                   415.35ms (p95: 717.33ms), providing a 28.3% safety margin.             |
|                                                                                                         |
|  2. Circuit Constraint Shrinkage: Forensic compilation of upstream gnark BN254 code revealed 4,077      |
|                                   R1CS constraints for DvP Initiator: a -53.2% reduction (-4,627 R1CS)  |
|                                   below legacy documentation claims of 8,704 constraints.                |
|                                                                                                         |
|  3. EVM Wrapper Overhead Delta  : On Rayls Chain 72957, precompiles 6, 7, and 8 cost 279, 6,129, and    |
|                                   181,138 gas. Solidity memory packing adds +13,749 to +19,689 gas      |
|                                   overhead, scaling at ~2,461-3,437 gas per public statement input.      |
|                                                                                                         |
|  4. Settlement Unit Economics   : At 57.60 Gwei baseline gas price, verifying confidential DvP costs    |
|                                   0.01438 RLS (a fraction of a cent at nominal valuation), delivering   |
|                                   a >99.99% gas cost reduction vs Ethereum L1 ($15-$25).                |
|                                                                                                         |
|  5. Invariant Test Coverage     : 16/16 tests passed across offline Three-State invariant suites and     |
|                                   live fork tests, proving counterfactual resilience (CRIT-ZK1 to ZK7). |
+---------------------------------------------------------------------------------------------------------+
```

---

## 2. Mathematical Architecture of Groth16 Proving & BN254 Pairings

The zero-knowledge privacy engine powering Rayls Enygma relies on the Groth16 zero-knowledge Succinct Non-Interactive Argument of Knowledge (zk-SNARK) instantiated over the Barreto-Naehrig elliptic curve BN254 (alt_bn128). 

![Diagram 1: Groth16 Prover Pipeline](assets/diagram_1_groth16_rtgs_pipeline.png)

### 2.1 Rank-1 Constraint Systems (R1CS)
Groth16 converts an arithmetic computation into a system of quadratic constraints over a prime field $\mathbb{F}_q$, where $q$ is the BN254 base field order:

$$q = 21888242871839275222246405745257275088696311157297823662689037894645226208583$$

The circuit constraints are formalized as:

$$\langle A_i, s \rangle \cdot \langle B_i, s \rangle - \langle C_i, s \rangle = 0 \quad \text{for } i \in \{1, \dots, m\}$$

where $s = [1, x_1, \dots, x_l, w_1, \dots, w_{m-l-1}]^T$ is the full witness vector composed of public statements $x \in \mathbb{F}_q^l$ and secret witness values $w \in \mathbb{F}_q^{m-l-1}$.

### 2.2 Succinct Proof Generation & Curve Groups
The proving algorithm computes three succinct group elements across two cyclic groups $\mathbb{G}_1$ and $\mathbb{G}_2$ of prime order $r$:

$$r = 21888242871839275222246405745257275088548364400416034343698204186575808495617$$

The proof tuple $\pi = (A, B, C)$ consists of:
- $A \in \mathbb{G}_1$: Affine point $(x, y) \in \mathbb{F}_q^2$ (64 bytes uncompressed)
- $B \in \mathbb{G}_2$: Affine point $(x_0 + i x_1, y_0 + i y_1) \in \mathbb{F}_{q^2}^2$ (128 bytes uncompressed)
- $C \in \mathbb{G}_1$: Affine point $(x, y) \in \mathbb{F}_q^2$ (64 bytes uncompressed)

Total proof payload size is strictly fixed at 128 bytes (when using compressed coordinates) or 256 bytes (uncompressed in standard EVM calldata). This succinct representation decouples verification cost from circuit size: whether the circuit contains 802 constraints or 7,440 constraints, the on-chain verifier executes the exact same number of pairing evaluations.

### 2.3 The 4-Pairing Verification Identity
Verification on-chain requires evaluating the optimal Ate pairing $e: \mathbb{G}_1 \times \mathbb{G}_2 \to \mathbb{G}_T$ over the target extension field $\mathbb{F}_{q^{12}}$. Given the Verification Key parameters:

$$\text{VK} = \left( \alpha \in \mathbb{G}_1, \beta \in \mathbb{G}_2, \gamma \in \mathbb{G}_2, \delta \in \mathbb{G}_2, \{IC_j \in \mathbb{G}_1\}_{j=0}^l \right)$$

The verifier first computes the public input linear combination in $\mathbb{G}_1$:

$$vk_x = IC_0 + \sum_{j=1}^l x_j \cdot IC_j$$

The proof $\pi = (A, B, C)$ is valid if and only if the multi-pairing identity evaluates to 1 in $\mathbb{G}_T$:

$$e(A, B) \cdot e(-\alpha, \beta) \cdot e(-vk_x, \gamma) \cdot e(-C, \delta) = 1$$

---

## 3. Upstream Rayls Enygma Circuit Anatomy & Poseidon Hashing Costs

To inspect the concrete circuit architecture, I compiled the official upstream Rayls Enygma repository (commit `a9b06c00cc4076b035c2d9afd5e2ca70b7eae194`) to BN254 R1CS using Consensys `gnark` v0.14.0.

![Diagram 2: Circuit Constraint Anatomy](assets/diagram_2_circuit_constraint_anatomy.png)

### 3.1 Forensic Discovery: Constraint Count Shrinkage
Legacy technical documentation for Rayls Enygma referenced a circuit complexity of 8,704 R1CS constraints for DvP settlement operations. Forensic compilation of the active upstream codebase revealed that the production circuit has been optimized down to **4,077 R1CS constraints**:

$$\Delta_{\text{constraints}} = 4,077 - 8,704 = -4,627 \text{ constraints } (-53.16\%)$$

This substantial optimization was achieved through three architectural refinements in gnark:
1. **Poseidon Custom S-Box Integration:** Replacing generic arithmetic field multiplications with native $x^5$ power map gadgets.
2. **Merged Multi-Scalar Input Accumulator:** Consolidating public statement checks into a unified vector.
3. **Truncated Merkle Depth:** Standardizing the private note commitment accumulator at tree depth $d=8$ (supporting 256 note commitments per epoch), avoiding oversized 32-level trees.

```
+---------------------------------------------------------------------------------------------------------+
|                                ENYGMA UPSTREAM CIRCUIT CONSTRAINT AUDIT                                 |
+---------------------------------------------------------------------------------------------------------+
|  Circuit Name                 | Total R1CS | Public Inputs (gnark) | Secret Witnesses | Merkle Depth   |
+-------------------------------+------------+-----------------------+------------------+----------------+
|  PrivateMintCircuit           |        802 |                     5 |                3 |       0 (None) |
|  DvPDestinationCircuit        |      3,778 |                     7 |               18 |              8 |
|  DvPInitiatorCircuit          |      4,077 |                     9 |               19 |              8 |
|  PaymentCircuit (1-in, 2-out) |      4,491 |                     8 |               19 |              8 |
|  PaymentCircuit (2-in, 2-out) |      7,440 |                    11 |               31 |              8 |
+---------------------------------------------------------------------------------------------------------+
```

*Note on Public Variable Representation:* In gnark R1CS compilation, `GetNbPublicVariables()` returns $l + 1$ public wires because gnark includes the implicit constant one wire ($s_0 = 1$) in its R1CS public index count (reporting 5, 7, and 9 public variables). When exported to Solidity verifier contracts, the application passes $l$ explicit public statement values (4, 6, and 8 inputs) via `uint256[] memory input`, while the constant wire is absorbed directly into the generator verification point $IC_0$.

### 3.2 Poseidon Hash Permutation Architecture
In zero-knowledge circuits, standard bitwise hash functions such as SHA-256 or Keccak-256 impose immense proving penalties because decomposing 32-bit words into binary bits requires thousands of boolean constraints. Enygma resolves this by utilizing the Poseidon algebraic hash function over $\mathbb{F}_q$.

![Diagram 5: Poseidon Hash Permutation Architecture](assets/diagram_5_poseidon_hash_permutation_matrix.png)

The Poseidon permutation employs the Hades design strategy:
- **State Width:** $t = 3$ for 2-to-1 hashing; $t = 5$ for 4-to-1 hashing.
- **Round Constants:** $R_F = 8$ full rounds (4 at beginning, 4 at end) where all $t$ elements pass through the non-linear S-box $S(x) = x^5$.
- **Partial Rounds:** $R_P = 56$ partial rounds where only the first state element $S_0$ passes through the S-box, while remaining elements pass linearly.
- **R1CS Gate Cost:** Each 2-to-1 Poseidon hash consumes approximately **240 R1CS constraints**.

In the `DvPInitiatorCircuit` (4,077 constraints), verifying the 8-level Merkle path requires 8 sequential Poseidon hashes:

$$8 \times 240 \text{ R1CS} = 1,920 \text{ constraints } (47.09\% \text{ of entire circuit})$$

The Merkle tree path evaluation represents nearly half of the entire circuit budget. Without Poseidon, using SHA-256 (which costs ~25,000 R1CS per hash) would have expanded the circuit to over 200,000 constraints, making sub-second client proving physically impossible.

---

## 4. Physical Consumer CPU Prover Benchmarks (N = 50 Runs)

To eliminate synthetic simulations, I executed $N = 50$ physical Groth16 witness solving and proving runs on host consumer hardware: an Intel Core i3-3110M CPU @ 2.40 GHz (dual-core, 4 threads, 7.6 GB RAM, no GPU acceleration, running Ubuntu 24.04 on WSL2).

![Diagram 4: Physical CPU Prover Latency vs. Mainnet 72957 Fork Gas](assets/diagram_4_physical_benchmarks_and_gas.png)

### 4.1 Proving Latency Distributions
Prover benchmarking measured both witness satisfaction time (`Solve`) and polynomial quotient multi-scalar multiplication time (`Prove`):

```
+---------------------------------------------------------------------------------------------------------+
|                                PHYSICAL CPU GROTH16 BENCHMARKS (N = 50 RUNS)                            |
+---------------------------------------------------------------------------------------------------------+
|  Circuit Target        | Median Solve | Median Prove | Mean Prove  | P95 Prove   | Std Dev  | Proof Size |
+------------------------+--------------+--------------+-------------+-------------+----------+------------+
|  PrivateMint (802 C)   |      3.15 ms |    115.52 ms |   132.39 ms |   217.31 ms |  41.3 ms |    128 B   |
|  DvPDestination (3.7k) |     13.89 ms |    404.55 ms |   436.96 ms |   583.16 ms |  81.9 ms |    128 B   |
|  DvPInitiator (4.0k)   |     13.37 ms |    415.35 ms |   457.15 ms |   717.33 ms |  93.3 ms |    128 B   |
+---------------------------------------------------------------------------------------------------------+
```

### 4.2 RTGS Sub-Second SLA Compliance Assessment
Wholesale banking RTGS mandates require transaction finalization within predictable operational windows. The benchmark results prove:
1. **Sub-Second Margin:** Across 50 consecutive runs of the heaviest circuit (`DvPInitiator`), the median proving time was **415.35ms**. Even at the 95th percentile, worst-case proving was **717.33ms**.
2. **Safety Margin:** Compared against the 1,000ms RTGS threshold, consumer hardware achieves a **+282.67ms safety headroom (28.27% buffer)**.
3. **Client Gateway Memory Footprint:** Proving key sizes on disk are compact (145 KB for Mint, 640 KB for DvPDest, 679 KB for DvPInit). Peak client heap allocation during witness generation and multi-scalar multiplication is **11.45 MB to 11.56 MB**. This lightweight memory budget confirms that commercial banks do not need specialized server infrastructure to run local privacy gateways; proof generation can run inside containerized bank microservices or browser environments.

---

## 5. Live Rayls Mainnet 72957 Fork Gas & EVM Precompile Profiling

To measure real on-chain execution costs, I forked Rayls Public Mainnet (Chain ID `72957`) at block tip `#15047066` using Foundry and deployed the illustrative invariant testbench (`ZKVerifierTestbench.sol`).

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

/// @notice Architectural Prototype & Illustrative Invariant Testbench
/// @dev Profiling EVM precompile gas and mathematical invariants on Rayls Chain 72957
contract ZKVerifierTestbench {
    // EIP-196 / EIP-197 Precompile addresses
    address constant EC_ADD = address(0x06);
    address constant EC_MUL = address(0x07);
    address constant EC_PAIRING = address(0x08);

    function verifyProof(
        uint256[2] memory a,
        uint256[2][2] memory b,
        uint256[2] memory c,
        uint256[] memory input
    ) public view returns (bool) {
        // Multi-scalar accumulation loop + 4-pairing staticcall
        // ...
    }
}
```

### 5.1 Precompile Gas Baseline on Rayls L1
Executing isolated staticcalls directly to the EVM precompiles on Rayls Mainnet 72957 yielded exact empirical gas consumption:
- **Precompile 6 (`ecAdd` 0x06):** **279 gas** (Theoretical EIP-196 base: 150 gas + staticcall dispatch: 129 gas).
- **Precompile 7 (`ecMul` 0x07):** **6,129 gas** (Theoretical EIP-196 base: 6,000 gas + staticcall dispatch: 129 gas).
- **Precompile 8 (`ecPairing` 0x08):** **181,138 gas** for 4 pairings ($k=4$). Theoretical EIP-197 formula:
  
  $$\text{Gas}_{\text{pairing}} = 45,000 + 34,000 \times 4 = 181,000 \text{ gas} \quad (+ 138 \text{ dispatch gas})$$

### 5.2 Solidity Staticcall Wrapper Overhead Analysis
When invoking a complete Groth16 verifier contract, the EVM incurs wrapper overhead: dynamic memory allocation, memory copies, packing 768 bytes for the 4-pairing precompile array, and iterating through public inputs to accumulate $vk_x$.

```
+---------------------------------------------------------------------------------------------------------+
|                                FORK MEASURED EVM VERIFICATION GAS (CHAIN 72957)                         |
+---------------------------------------------------------------------------------------------------------+
|  Circuit Target        | Public Inputs | Precompile Base | Wrapper Overhead | Total Measured Gas | Native RLS Cost |
+------------------------+---------------+-----------------+------------------+--------------------+-----------------+
|  PrivateMint           |             4 |     205,450 gas |      +13,749 gas |        219,199 gas |     0.01262 RLS |
|  DvPDestination        |             6 |     217,750 gas |      +16,718 gas |        234,468 gas |     0.01350 RLS |
|  DvPInitiator          |             8 |     230,050 gas |      +19,689 gas |        249,739 gas |     0.01438 RLS |
+---------------------------------------------------------------------------------------------------------+
```

Empirical data reveals that Solidity wrapper overhead scales linearly with public statement length:

$$\text{Overhead}_{\text{EVM}} \approx 7,800 \text{ gas (fixed staticcall/memory setup)} + 1,480 \text{ gas per public input}$$

Across all evaluated circuits, raw elliptic curve pairings account for **72.5% to 82.6%** of total transaction gas. At the canonical Rayls Mainnet gas price of $57.60\text{ Gwei}$, verifying an atomic confidential DvP settlement costs:

$$\text{Fee} = 249,739 \text{ gas} \times 57.60 \times 10^{-9} \text{ RLS} = 0.01438497 \text{ RLS}$$

Because RLS does not trade on volatile public speculative exchanges with constant fiat feeds, fiat-denominated transaction costs depend on institutional consortium gas settlement agreements. Assuming an illustrative valuation range between $0.01 and $0.10 per RLS, settlement fees remain a negligible fraction of a cent ($0.00014 to $0.0014 per proof). Compared to Ethereum Layer-1 (where 250,000 gas at 25 Gwei and $2,500/ETH costs ~$15.60), Rayls eliminates prohibitive L1 gas friction, allowing financial institutions to settle high-volume intraday obligations without fee volatility.

---

## 6. Three-State Invariant Security Architecture & Defect Matrix

To evaluate contract robustness against adversarial manipulation, I implemented and executed a Three-State Invariant Foundry test suite in `test/ZKInvariantAudit.t.sol` covering 16 distinct operational scenarios.

![Diagram 3: Three-State Invariant Security Architecture](assets/diagram_3_enygma_vulnerability_matrix.png)

```
+---------------------------------------------------------------------------------------------------------+
|                                  THREE-STATE INVARIANT TEST ARCHITECTURE                                |
+---------------------------------------------------------------------------------------------------------+
|  STATE 1: HAPPY PATH                                                                                    |
|  * Valid witness satisfaction, active tree roots, dynamic tree progression (0 -> 1).                    |
|  * Verified BN254 elliptic curve pairing identity: e(A, B) * e(-alpha, beta) * ... == 1.               |
|  * Gas Consumption: 61,060 - 249,739 gas.                                                              |
|                                                                                                         |
|  STATE 2: REJECTED PATH (NEGATIVE CONTROLS & VULNERABILITY MITIGATIONS)                                 |
|  * CRIT-ZK1: Tampered Merkle Tree Number -> Reverts with InvalidTreeNumber(active, tampered).           |
|  * CRIT-ZK2: Field Overflow Wrapping (v >= 10^36) -> Reverts with ValueBoundExceeded(val, 1e36).       |
|  * CRIT-ZK3: Double-Spend Replay -> Reverts with NullifierAlreadySpent(nullifier).                      |
|  * CRIT-ZK4: Statement Length Mismatch -> Reverts with PublicStatementLengthMismatch(8, 7).             |
|  * CRIT-ZK5: Scalar Field Boundary Overflow (>= r) -> Reverts with ScalarFieldOverflow(scalar, r).      |
|                                                                                                         |
|  STATE 3: EDGE / FUZZ PATH (BOUNDARY DEFENSE & ROBUSTNESS)                                              |
|  * CRIT-ZK6: Unconstrained CounterVault Guard -> Reverts with ZeroCounterVaultRejected().              |
|  * CRIT-ZK7: Unbound Cross-Swap Commitment -> Reverts with MessageCommitmentMismatch(msg, commitA).     |
|  * Property-Based Fuzz Testing: 256 fuzz runs with arbitrary malformed scalars; 100% cleanly reverted. |
+---------------------------------------------------------------------------------------------------------+
```

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import "forge-std/Test.sol";
import "../contracts/ZKVerifierTestbench.sol";

contract ZKInvariantAuditTest is Test {
    ZKVerifierTestbench public verifier;

    function setUp() public {
        verifier = new ZKVerifierTestbench();
    }

    /// @notice State 2 Negative Control: CRIT-ZK1 Tampered Tree Number
    function test_Counterfactual_CRIT_ZK1_TamperedTreeNumberReverts() public {
        vm.expectRevert(abi.encodeWithSelector(
            ZKVerifierTestbench.InvalidTreeNumber.selector, 0, 999
        ));
        verifier.settleDvPInitiator(
            0x1111, 999, 0x4444, keccak256("sn"), 0x2222, 0x1111, 0x3333, 0xA34B, 50e18
        );
    }

    /// @notice State 3 Edge Robustness: 256 Property-Based Fuzz Runs
    function testFuzz_ArbitraryMalformedValuesRevert(uint256 malformedValue) public {
        vm.assume(malformedValue >= 1e36);
        vm.expectRevert();
        verifier.settleDvPInitiator(
            0x1111, 0, 0x4444, keccak256("sn"), 0x2222, 0x1111, 0x3333, 0xA34B, malformedValue
        );
    }
}
```

### 6.1 Vulnerability Classifications & Mitigations
- **CRIT-ZK1 (Tree Number Double Spend, HIGH-1):** In early Merkle accumulator designs, nullifiers were only checked for uniqueness within the current tree. If the tree rolled over, an attacker could replay nullifiers across historical epochs. Mitigated in gnark by asserting `api.AssertIsEqual(stTreeNumber, activeTreeNumber)` and validating tree continuity on-chain.
- **CRIT-ZK2 (Scalar Field Overflow, H-2):** BN254 scalar field elements are 254-bit numbers ($r \approx 2^{254}$). A transaction value of $2^{254} - 1$ could wrap modulo $r$ during balance subtractions. Mitigated via `valuebound.Assert(api, v, 10^36)`, restricting values to 120 bits ($< 10^{36}$).
- **CRIT-ZK6 (Unconstrained CounterVault Bypass):** If `StCounterVault` is left unconstrained in the circuit, a malicious actor can set the counterparty vault to address zero, burning assets without unlocking cash. Mitigated in upstream code by enforcing `api.AssertIsDifferent(StCounterVault, 0)`.
- **CRIT-ZK7 (Unbound Cross-Swap Commitment, HIGH-5):** In cross-subnet DvP, if the cross-chain settlement payload (`StMessage`) is decoupled from the asset commitment (`StCommitA`), a compromised relayer could substitute settlement recipients. Mitigated by binding `api.AssertIsEqual(StMessage, StCommitA)`.

---

## 7. Cross-Subnet Confidential Delivery-versus-Payment (DvP) Workflow

The practical culmination of Enygma Groth16 proving is the execution of cross-subnet Delivery-versus-Payment between sovereign bank environments and the central bank cash ledger.

![Diagram 6: Confidential DvP Settlement Sequence](assets/diagram_6_confidential_dvp_atomic_settlement.png)

### 7.1 The 6-Step Atomic Settlement Lifecycle
1. **Bilateral Agreement & Key Exchange:** Bank A and Bank B establish a shared secret via off-chain authenticated key exchange (ECDH or ML-KEM-768), generating blinding factor $r_a$.
2. **Asset Escrow & Commitment Generation:** Bank A locks the tokenized asset into its local Enygma vault on the Asset Subnet and computes commitment $StCommitA = \text{Poseidon}(\text{asset\_id}, v_a, pk_b, sn_a, r_a)$.
3. **Client Groth16 Proving:** Bank A's client gateway compiles witness inputs and executes gnark Groth16 proving on the `DvPInitiatorCircuit` (4,077 R1CS, 415ms median on consumer CPU), producing a 128-byte proof $\pi_A$.
4. **Public L1 Settlement Registration:** Bank A submits $\pi_A$ and 8 public statement elements to Rayls Public Chain 72957.
5. **EVM Invariant Verification:** `ZKVerifierTestbench` verifies pairing identity ($e(A,B)\dots=1$), validates active tree number, and marks $sn_a$ spent in 249,739 gas (0.014 RLS).
6. **Simultaneous Atomic Cash Release:** Upon observing the verified L1 commitment event, Bank B unlocks tokenized central bank Drex deposits on the Cash Subnet. Both legs finalize simultaneously, eliminating Herstatt settlement risk under CPMI-IOSCO Principle 12.

---

## 8. Rayls Mainnet 72957 Empirical Telemetry & Cadence Analysis

To observe public settlement layer operating dynamics, I scanned 1,000 continuous canonical blocks on Rayls Public Mainnet (Chain ID `72957`) from block `#15047066` to `#15048065` via `https://mainnet-rpc.rayls.com`.

![Diagram 7: Rayls Mainnet 72957 Empirical Telemetry](assets/diagram_7_mainnet_telemetry_cadence_distribution.png)

```
+---------------------------------------------------------------------------------------------------------+
|                                RAYLS MAINNET 72957 TELEMETRY (1,000 BLOCKS)                             |
+---------------------------------------------------------------------------------------------------------+
|  Metric Parameter            | Empirical Measured Value  | Forensic Architecture Significance          |
+------------------------------+---------------------------+---------------------------------------------+
|  Scan Block Range            | #15,047,066 - #15,048,065 | 1,000 consecutive blocks (step = 1)         |
|  Parent Hash Verification    | 999 / 999 valid links     | 100% cryptographic continuity (zero forks)  |
|  Mean Block Cadence          | 1.3423 seconds            | Rapid probabilistic finality                |
|  Median Block Cadence        | 1.0000 second             | Deterministic throughput                    |
|  P95 Block Cadence           | 2.0000 seconds            | Strict latency bound                        |
|  Block Production Range      | [0s .. 2s] (Max: 2s)      | Zero observed gaps exceeding 2 seconds      |
|  Gas Limit Execution Ceiling | 500,000,000 gas           | Enormous settlement capacity headroom       |
|  Baseline Gas Price          | 57.60 Gwei (fixed)        | Highly predictable institutional budgeting  |
+---------------------------------------------------------------------------------------------------------+
```

The 500,000,000 block gas execution ceiling provides theoretical capacity for up to ~2,000 Groth16 verifications per block (500M / 250k gas). However, realized network throughput is governed by state trie write latency, validator node disk I/O, and p2p block propagation rather than gas limit alone. This 500M parameter represents computational execution headroom rather than realized sustained transactions-per-second (TPS).

### 8.1 Genesis System Contract Bytecode Verification
Direct RPC code inspection verified deployed system bytecode on Chain `72957`:
- **ConsensusRegistry (`0x07E17e17e17e17e17e17e17e17e17e17e17e1`):** **21,929 bytes** (Manages proof-of-authority validator membership and governance).
- **FeeAggregatorProxy (`0x07E17e17e17e17e17e17e17e17e17e17e17e3`):** **122 bytes** (Canonical EIP-1967 transparent upgradeable proxy managing gas fee distributions).
- **DelegationPool (`0x07e17e17e17e17e17e17e17e17E17e17e17e17e9`):** **15,790 bytes** (Validator staking delegation and rewards accounting).

---

## 9. Four-Domain Evidence Matrix

To maintain strict epistemic rigor, all data points, code proofs, and conclusions are classified into four distinct operational domains:

```
+---------------------------------------------------------------------------------------------------------+
|                                      FOUR-DOMAIN EVIDENCE MATRIX                                        |
+---------------------------------------------------------------------------------------------------------+
|  DOMAIN 1: ON-CHAIN PUBLIC MAINNET L1 TELEMETRY (CHAIN 72957)                                           |
|  * Source: Live RPC queries to https://mainnet-rpc.rayls.com covering blocks #15047066 - #15048065.    |
|  * Verified Metrics: 1.3423s mean cadence, 57.60 Gwei gas price, 500M gas ceiling, genesis bytecode.   |
|  * Epistemic Boundary: Describes public settlement L1 only; does not prove private subnet queues.       |
|                                                                                                         |
|  DOMAIN 2: UPSTREAM OFFICIAL REPOSITORIES (PINNED COMMIT a9b06c0)                                      |
|  * Source: raylsnetwork/Enygma gnark circuit definitions (enygma_dvp/gnark_circuits).                   |
|  * Verified Metrics: 4,077 R1CS constraints, Poseidon S-box costs, TestDvpInitiatorCircuit passes.     |
|  * Epistemic Boundary: Proves mathematical constraint counts in gnark; does not prove node gossip.      |
|                                                                                                         |
|  DOMAIN 3: ARCHITECTURAL PROTOTYPE TESTBENCH (CONTROLLED LOCAL RESULTS)                                 |
|  * Source: ZKVerifierTestbench.sol & ZKInvariantAudit.t.sol (Foundry runtime).                          |
|  * Verified Metrics: 16/16 test passes, 249,739 verification gas, CRIT-ZK1 through ZK7 mitigations.     |
|  * Epistemic Boundary: Controlled local evaluation; demonstrates invariants without claiming exploits.  |
|                                                                                                         |
|  DOMAIN 4: INSTITUTIONAL FRAMEWORKS & REGULATORY STANDARDS                                              |
|  * Source: CPMI-IOSCO Principles 8 & 12, Brazilian Complementary Law 105/2001, BCB Drex Pilot Specs.    |
|  * Verified Metrics: <= 1,000ms RTGS proving budget, Herstatt risk elimination, statutory finality.    |
|  * Epistemic Boundary: Legal and regulatory requirements; blockchain provides technical finality only.  |
+---------------------------------------------------------------------------------------------------------+
```

---

## 10. Hardware Specs, Toolchain Setup & Start-to-Finish Reproduction Guide

All results presented in this monograph are 100% reproducible on consumer hardware using the automated reproduction suite.

### 10.1 Hardware & Environment Specification
- **Host CPU:** Intel Core i3-3110M @ 2.40 GHz (2 Cores, 4 Logical Threads, 3MB Cache)
- **Host Memory:** 7.6 GB Physical DDR3 RAM (3.8 GiB allocated to WSL2)
- **Operating System:** Ubuntu 24.04 LTS on Windows Subsystem for Linux (WSL2)
- **Go Toolchain:** Go v1.22.0+ / v1.26.0 (located at `~/.local/go/bin/go`)
- **Foundry Toolchain:** Forge v0.2.0 (Solc 0.8.24, nightly build)
- **Python Environment:** Python 3.12+ (Pillow 12.3.0, PyYAML)

### 10.2 Step-by-Step Reproduction Instructions

```bash
# 1. Clone repository
git clone https://github.com/9ytshade/rayls-zk-enygma-groth16.git
cd rayls-zk-enygma-groth16

# 2. Verify all datasets via automated gatekeeper (Exit Code 0)
python scripts/verify_datasets.py

# 3. Execute Three-State Invariant Foundry Suite (16/16 tests pass)
forge test -vv

# 4. Execute modular research stage runner
./scripts/run_research_stage.sh 6   # Audits empirical datasets
./scripts/run_research_stage.sh 3   # Runs Foundry invariant test suite
./scripts/run_research_stage.sh all # Runs all 6 research stages end-to-end

# 5. Regenerate all 7 institutional diagrams and cover image
python scripts/generate_diagrams.py --diagram all
python scripts/generate_cover_image.py
```

---

## 11. Strategic Synthesis & Conclusion

In this research monograph, I evaluated the mathematical, cryptographic, and operational mechanics of Groth16 zero-knowledge proving on Rayls Enygma circuits, examining whether client-side privacy can realistically meet the stringent sub-second performance demands of institutional financial market infrastructures.

### 11.1 Summary of Verified Empirical Findings
1. **Mathematical Feasibility on Consumer Compute:** My physical benchmarks ($N = 50$) demonstrated that generating Groth16 proofs for confidential Delivery-versus-Payment operations does not require datacenter-grade GPU clusters. On an entry-level dual-core Intel Core i3 @ 2.40 GHz without GPU acceleration, the median proving time for the complete `DvPInitiatorCircuit` (4,077 R1CS) was **415.35 ms**, with a 95th percentile of **717.33 ms**. This establishes a **+28.3% safety margin** below the 1,000 ms wholesale RTGS processing window.
2. **Circuit Constraint Shrinkage:** Forensic compilation of upstream `raylsnetwork/Enygma` (@ `a9b06c00`) revealed that the active production circuit has been optimized from legacy documentation claims of 8,704 constraints down to **4,077 R1CS constraints** (-53.16% reduction). This optimization is enabled by Poseidon custom S-box gadgets (~240 R1CS per hash) and a bounded Merkle depth of $d=8$, which accounts for 47.09% (1,920 constraints) of the circuit budget.
3. **EVM Verification Economics:** Profiling on a live Rayls Mainnet 72957 fork revealed that pairing precompiles (EIP-196/197 addresses `0x06`, `0x07`, `0x08`) consume 205,450 to 230,050 gas, while Solidity staticcall wrapper and memory array packing add $+13,749$ to $+19,689$ gas. At the baseline network gas price of 57.60 Gwei, settling an atomic confidential DvP transaction burns **0.01438 RLS**, providing a predictable and negligible cost profile compared to public Layer-1 alternatives.
4. **Defense-in-Depth Invariant Security:** The 16-test Three-State Invariant Foundry test suite verified that invalid proofs, historical tree rollbacks (`CRIT-ZK1`), scalar field overflows (`CRIT-ZK2`), double-spend nullifier replays (`CRIT-ZK3`), zero CounterVault bypasses (`CRIT-ZK6`), and unconstrained message bindings (`CRIT-ZK7`) are deterministically rejected by EVM state machines.

### 11.2 Epistemic Boundaries & Non-Exaggerated Limitations
To preserve intellectual integrity, I emphasize the explicit boundaries of these findings:
- **Local Prover vs. Distributed Node Queues:** My physical prover benchmarks measure isolated Go gnark execution on a local CPU. They do not simulate multi-node gossip congestion, core-banking API ingestion overhead, or validator mempool queuing during concurrent transaction spikes. Bank infrastructure architects must provision process thread isolation and concurrent worker pools to absorb intraday peak settlement bursts.
- **Single-Node RPC Telemetry vs. Byzantine Consensus:** The 1,000-block telemetry scan (1.34s mean cadence, 500M gas ceiling) reflects observations through a single public RPC node (`https://mainnet-rpc.rayls.com`). While 999 of 999 consecutive parent links were verified without reorganizations, this describes public L1 settlement dynamics, not the internal private consensus queues of proprietary Sovereign Subnets.
- **Technical Settlement vs. Statutory Legal Finality:** Cryptographic proof verification and on-chain nullifier consumption guarantee mathematical validity and double-spend prevention. However, as mandated by CPMI-IOSCO Principle 8, technical finality does not substitute for statutory legal finality. Wholesale interbank settlement requires binding legal master netting agreements, insolvency carve-outs, and central bank operational frameworks (such as Banco Central do Brasil's Drex pilot guidelines) to achieve full legal enforceability.

### 11.3 Architectural Recommendations for Enterprise Deployments
For financial institutions and system integrators preparing production deployments on Rayls, I recommend:
1. **Containerized Prover Gateways:** Deploy Enygma client provers as lightweight Go microservices with in-memory proving key caches (requiring strictly ~11.5 MB RAM per worker), pinned to dedicated CPU cores.
2. **Dynamic Tree Epoch Synchronization:** Ensure client gateways maintain real-time Merkle tree synchronization with active subnet state to avoid generating proofs against superseded tree roots (`CRIT-ZK1`).
3. **Strict Invariant Validation:** Enforce contract-level range checks ($< r$), explicit CounterVault non-zero assertions, and cryptographic message binding in all custom cross-subnet settlement wrappers.

In conclusion, Rayls Enygma Groth16 proving achieves the mathematical efficiency, client resource footprint, and on-chain fee predictability required for real-time institutional DvP settlement, establishing a practical cryptographic bridge between private banking confidentiality and decentralized public settlement.

---

## 12. Frequently Asked Questions (FAQs)

**Q1: Why does Enygma use Groth16 instead of newer proof systems like PLONK or STARKs?**  
*Answer:* Groth16 offers the smallest proof size (strictly 128 bytes compressed) and lowest EVM on-chain verification gas (~220,000 to 250,000 gas) of any known proof system. PLONK proofs require ~800 to 1,200 bytes and consume over 350,000 gas, while STARKs require tens of kilobytes of calldata. For wholesale interbank settlement, Groth16's minimal on-chain footprint is optimal.

**Q2: Does the circuit constraint reduction from 8,704 to 4,077 weaken cryptographic security?**  
*Answer:* No. The 53.2% constraint reduction was achieved by migrating from generic arithmetic multiplications to custom Poseidon S-box gadgets and optimizing the Merkle tree depth to $d=8$. The cryptographic security margin remains bounded by the 128-bit security level of the BN254 elliptic curve.

**Q3: Can an attacker double-spend by replaying a nullifier on a different Rayls Sovereign Subnet?**  
*Answer:* No. In cross-subnet DvP, nullifiers are registered on the decentralized Rayls Public Chain (Chain ID `72957`). Once a nullifier is marked spent on L1, subsequent settlement attempts using the same nullifier revert with `NullifierAlreadySpent` (`CRIT-ZK3`).

**Q4: Does sub-second proving latency eliminate all counterparty risk?**  
*Answer:* Fast proving ensures that client gateways do not miss settlement windows. However, technical finality does not replace legal finality. Under CPMI-IOSCO Principle 8, financial market infrastructures must combine cryptographic atomic settlement with legally binding bilateral master netting agreements.

---

## 13. References & Official Sources

1. **CPMI-IOSCO:** *Principles for Financial Market Infrastructures (PFMI)*, Principle 8 (Settlement Finality) & Principle 12 (Exchange-of-Value Settlement Systems).
2. **Banco Central do Brasil (BCB):** *Piloto Drex: Diretrizes de Privacidade e Testes de Liquidação Interbancária*, 2023-2024.
3. **Groth, Jens:** *On the Size of Pairing-based Non-interactive Arguments*, Advances in Cryptology - EUROCRYPT 2016.
4. **Grassi et al.:** *Poseidon: A New Hash Function for Zero-Knowledge Proof Systems*, USENIX Security Symposium 2021.
5. **Ethereum Improvement Proposals:**
   - EIP-196: *Precompiled contracts for addition and scalar multiplication on the elliptic curve alt_bn128*.
   - EIP-197: *Precompiled contracts for optimal ate pairing check on the elliptic curve alt_bn128*.
   - EIP-2028: *Transaction data gas cost reduction*.
6. **Consensys gnark:** *Fast Zero-Knowledge Proof Library in Go*, GitHub: `consensys/gnark`.
7. **Rayls Protocol Documentation:** *Rayls Whitepaper & Enygma Privacy Framework*, `https://docs.rayls.com`.
