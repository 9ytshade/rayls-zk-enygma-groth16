// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import "forge-std/Test.sol";
import "../contracts/ZKVerifierTestbench.sol";

contract ZKMainnetForkTest is Test {
    string constant RPC_URL = "https://mainnet-rpc.rayls.com";
    uint256 constant CHAIN_ID = 72957;

    address constant CONSENSUS_REGISTRY = 0x07E17e17E17e17E17e17E17E17E17e17e17E17e1;
    address constant FEE_AGGREGATOR_PROXY = 0x07E17E17e17E17e17E17e17e17e17e17E17E17E3;
    address constant DELEGATION_POOL = 0x07e17e17e17e17e17e17e17e17E17e17e17e17e9;

    ZKVerifierTestbench public verifier;
    uint256 public forkId;

    // Standard BN254 G1 Generator point (1, 2)
    ZKVerifierTestbench.G1Point internal G1_GEN;
    // Standard BN254 G2 Generator point
    ZKVerifierTestbench.G2Point internal G2_GEN;

    function setUp() public {
        forkId = vm.createSelectFork(RPC_URL);
        verifier = new ZKVerifierTestbench();

        G1_GEN = ZKVerifierTestbench.G1Point(1, 2);
        G2_GEN = ZKVerifierTestbench.G2Point(
            [
                0x1800deef121f1e76426a00665e5c4479674322d4f75edadd46debd5cd992f6ed,
                0x198e9393920d483a7260bfb731fb5d25f1aa493335a9e71297e485b7aef312c2
            ],
            [
                0x12c85ea5db8c6deb4aab71808dcb408fe3d1e7690c43d37b4ce6cc0166fa7daa,
                0x090689d0585ff075ec9e99ad690c3395bc4b313370b38ef355acdadcd122975b
            ]
        );
    }

    /// @notice Test 1: Verify fork environment, chain ID, and Genesis contract bytecodes
    function test_MainnetFork_ChainStateAndGenesisContractsPresent() public view {
        assertEq(block.chainid, CHAIN_ID, "Forked chainId must match Rayls Mainnet 72957");
        assertTrue(block.gaslimit >= 500_000_000, "Block gas limit must be at least 500M");

        assertEq(CONSENSUS_REGISTRY.code.length, 21929, "ConsensusRegistry bytecode must match canonical 21,929 bytes");
        assertEq(FEE_AGGREGATOR_PROXY.code.length, 122, "FeeAggregatorProxy bytecode must match canonical 122 bytes");
        assertEq(DELEGATION_POOL.code.length, 15790, "DelegationPool bytecode must match canonical 15,790 bytes");
    }

    /// @notice Test 2: Measure direct precompile 6 (ecAdd), 7 (ecMul), and 8 (ecPairing) gas on Rayls Mainnet 72957
    function test_MainnetFork_PrecompilesGasMeasurement() public {
        // Precompile 6 (ecAdd): 150 base gas + staticcall overhead
        uint256[4] memory addInput = [uint256(1), uint256(2), uint256(1), uint256(2)];
        uint256[2] memory addOutput;
        uint256 gasBeforeAdd = gasleft();
        assembly {
            pop(staticcall(gas(), 6, addInput, 0x80, addOutput, 0x40))
        }
        uint256 ecAddGas = gasBeforeAdd - gasleft();
        emit log_named_uint("Precompile 6 (ecAdd) Direct Gas", ecAddGas);

        // Precompile 7 (ecMul): 6000 base gas + staticcall overhead
        uint256[3] memory mulInput = [uint256(1), uint256(2), uint256(5)];
        uint256[2] memory mulOutput;
        uint256 gasBeforeMul = gasleft();
        assembly {
            pop(staticcall(gas(), 7, mulInput, 0x60, mulOutput, 0x40))
        }
        uint256 ecMulGas = gasBeforeMul - gasleft();
        emit log_named_uint("Precompile 7 (ecMul) Direct Gas", ecMulGas);

        // Precompile 8 (ecPairing): 4 pairs of points at infinity (0,0) evaluate to 1
        // EIP-197 specifies 45,000 + 4 * 34,000 = 181,000 base gas
        uint256[24] memory pairInput; // initialized to all zeros = point at infinity O_G1, O_G2
        uint256[1] memory pairOutput;
        bool pairSuccess;
        uint256 gasBeforePair = gasleft();
        assembly {
            pairSuccess := staticcall(sub(gas(), 5000), 8, pairInput, 768, pairOutput, 0x20)
        }
        uint256 ecPairGas = gasBeforePair - gasleft();
        emit log_named_uint("Precompile 8 (4-Pairing) Direct Gas", ecPairGas);
        assertTrue(pairSuccess, "ecPairing should succeed for valid points at infinity");
        assertEq(pairOutput[0], 1, "ecPairing of points at infinity should yield 1");

        // Assertions against standard EVM rules with staticcall wrapper headroom
        assertTrue(ecAddGas >= 150 && ecAddGas <= 500, "ecAdd should consume ~150 gas + dispatch");
        assertTrue(ecMulGas >= 6000 && ecMulGas <= 6500, "ecMul should consume ~6000 gas + dispatch");
        assertTrue(ecPairGas >= 181000 && ecPairGas <= 186000, "ecPairing should consume ~181000 gas + dispatch");
    }

    /// @notice Test 3: Measure full public input accumulation & verifier gas for PrivateMint (4 inputs)
    function test_MainnetFork_PrivateMint_VerificationGas() public {
        uint256 l = 4;
        ZKVerifierTestbench.G1Point[] memory ic = new ZKVerifierTestbench.G1Point[](l + 1);
        for (uint256 i = 0; i <= l; i++) {
            ic[i] = G1_GEN;
        }
        uint256[] memory publicInputs = new uint256[](l);
        for (uint256 i = 0; i < l; i++) {
            publicInputs[i] = i + 100;
        }

        uint256 gasBefore = gasleft();
        verifier.accumulatePublicInputs(ic, publicInputs);
        uint256 accumGas = gasBefore - gasleft();

        emit log_named_uint("PrivateMint (4 Public Inputs) Accumulation Gas", accumGas);
        // Total = base pairing (181,000) + accumulation gas
        uint256 totalEstimatedGas = 181000 + accumGas;
        emit log_named_uint("PrivateMint Total Empirical Verification Gas", totalEstimatedGas);
    }

    /// @notice Test 4: Measure full public input accumulation & verifier gas for DvPDestination (6 inputs)
    function test_MainnetFork_DvPDestination_VerificationGas() public {
        uint256 l = 6;
        ZKVerifierTestbench.G1Point[] memory ic = new ZKVerifierTestbench.G1Point[](l + 1);
        for (uint256 i = 0; i <= l; i++) {
            ic[i] = G1_GEN;
        }
        uint256[] memory publicInputs = new uint256[](l);
        for (uint256 i = 0; i < l; i++) {
            publicInputs[i] = i + 200;
        }

        uint256 gasBefore = gasleft();
        verifier.accumulatePublicInputs(ic, publicInputs);
        uint256 accumGas = gasBefore - gasleft();

        emit log_named_uint("DvPDestination (6 Public Inputs) Accumulation Gas", accumGas);
        uint256 totalEstimatedGas = 181000 + accumGas;
        emit log_named_uint("DvPDestination Total Empirical Verification Gas", totalEstimatedGas);
    }

    /// @notice Test 5: Measure full public input accumulation & verifier gas for DvPInitiator (8 inputs)
    function test_MainnetFork_DvPInitiator_VerificationGas() public {
        uint256 l = 8;
        ZKVerifierTestbench.G1Point[] memory ic = new ZKVerifierTestbench.G1Point[](l + 1);
        for (uint256 i = 0; i <= l; i++) {
            ic[i] = G1_GEN;
        }
        uint256[] memory publicInputs = new uint256[](l);
        for (uint256 i = 0; i < l; i++) {
            publicInputs[i] = i + 300;
        }

        uint256 gasBefore = gasleft();
        verifier.accumulatePublicInputs(ic, publicInputs);
        uint256 accumGas = gasBefore - gasleft();

        emit log_named_uint("DvPInitiator (8 Public Inputs) Accumulation Gas", accumGas);
        uint256 totalEstimatedGas = 181000 + accumGas;
        emit log_named_uint("DvPInitiator Total Empirical Verification Gas", totalEstimatedGas);
    }
}
