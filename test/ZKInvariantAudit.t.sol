// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import "forge-std/Test.sol";
import "../contracts/ZKVerifierTestbench.sol";

contract ZKInvariantAuditTest is Test {
    ZKVerifierTestbench public verifier;

    // Test actors
    address public alice = address(0xAAAA);
    address public bob = address(0xBBBB);

    // Baseline test values
    uint256 constant VALID_MESSAGE = 0x1111;
    uint256 constant VALID_COMMIT_A = 0x1111; // StMessage == StCommitA (HIGH-5)
    uint256 constant VALID_COMMIT_B = 0x2222;
    uint256 constant VALID_REVERT_A = 0x3333;
    uint256 constant VALID_ROOT = 0x4444;
    uint256 constant VALID_COUNTER_VAULT = 0xA34B0BB5;
    uint256 constant VALID_VALUE_IN = 50e18; // 50 tokens (well below 10^36)
    bytes32 constant VALID_NULLIFIER = keccak256("enygma-dvp-nullifier-alice-note-0");

    uint256 constant FIELD_OVERFLOW_VALUE = 2e36; // Exceeds VALUE_BOUND_CEILING (1e36)
    bytes32 constant REPLAY_NULLIFIER = keccak256("enygma-dvp-nullifier-alice-note-0");

    function setUp() public {
        verifier = new ZKVerifierTestbench();
    }

    // =========================================================================
    // STATE 1: HAPPY PATH (VALID INVARIANTS SATISFIED)
    // =========================================================================

    /// @notice Test 1: Happy path settlement of DvP Initiator leg
    function test_HappyPath_DvPInitiator_ValidSettlement() public {
        bool success = verifier.settleDvPInitiator(
            VALID_MESSAGE,
            0, // stTreeNumber == activeTreeNumber
            VALID_ROOT,
            VALID_NULLIFIER,
            VALID_COMMIT_B,
            VALID_COMMIT_A,
            VALID_REVERT_A,
            VALID_COUNTER_VAULT,
            VALID_VALUE_IN
        );

        assertTrue(success, "Valid DvP Initiator settlement must succeed");
        assertTrue(verifier.spentNullifiers(VALID_NULLIFIER), "Nullifier must be marked spent");
    }

    /// @notice Test 2: Valid 4-pairing identity check with points at infinity
    function test_HappyPath_ValidGroth16PairingIdentity() public view {
        ZKVerifierTestbench.G1Point memory infG1 = ZKVerifierTestbench.G1Point(0, 0);
        ZKVerifierTestbench.G2Point memory infG2 = ZKVerifierTestbench.G2Point([uint256(0), uint256(0)], [uint256(0), uint256(0)]);

        bool result = verifier.pairing(
            infG1, infG2,
            infG1, infG2,
            infG1, infG2,
            infG1, infG2
        );
        assertTrue(result, "Identity pairing over BN254 must evaluate to 1");
    }

    /// @notice Test 3: Sequential tree number progression allows valid settlement
    function test_HappyPath_DynamicTreeNumberProgression() public {
        verifier.setActiveTreeNumber(1);

        bool success = verifier.settleDvPInitiator(
            VALID_MESSAGE,
            1, // matching tree 1
            VALID_ROOT,
            VALID_NULLIFIER,
            VALID_COMMIT_B,
            VALID_COMMIT_A,
            VALID_REVERT_A,
            VALID_COUNTER_VAULT,
            VALID_VALUE_IN
        );
        assertTrue(success, "Settlement under active tree 1 must succeed");
    }

    // =========================================================================
    // STATE 2: REJECTED PATH (NEGATIVE CONTROLS & COUNTERFACTUAL AUDIT)
    // =========================================================================

    /// @notice Test 4: CRIT-ZK1 - Guard OFF allows nullifier replay across sub-trees; Guard ON reverts
    function test_Counterfactual_CRIT_ZK1_TamperedTreeNumberReverts() public {
        // Step A: Guard OFF permits cross-tree replay (Vulnerable state)
        verifier.setGuards(ZKVerifierTestbench.GuardConfig({
            enforceValueBound: true,
            enforceCounterVaultNonZero: true,
            enforceMessageBinding: true,
            enforceNullifierUniqueness: true,
            enforceTreeNumber: false // Guard OFF
        }));

        bool vulnSuccess = verifier.settleDvPInitiator(
            VALID_MESSAGE,
            999, // tampered tree number
            VALID_ROOT,
            VALID_NULLIFIER,
            VALID_COMMIT_B,
            VALID_COMMIT_A,
            VALID_REVERT_A,
            VALID_COUNTER_VAULT,
            VALID_VALUE_IN
        );
        assertTrue(vulnSuccess, "Guard OFF permits foreign tree number");

        // Step B: Guard ON strictly enforces active tree number
        verifier.setGuards(ZKVerifierTestbench.GuardConfig({
            enforceValueBound: true,
            enforceCounterVaultNonZero: true,
            enforceMessageBinding: true,
            enforceNullifierUniqueness: true,
            enforceTreeNumber: true // Guard ON
        }));

        bytes32 freshNullifier = keccak256("fresh-nullifier-tree-test");
        vm.expectRevert(abi.encodeWithSelector(ZKVerifierTestbench.InvalidTreeNumber.selector, 0, 999));
        verifier.settleDvPInitiator(
            VALID_MESSAGE,
            999, // tampered tree
            VALID_ROOT,
            freshNullifier,
            VALID_COMMIT_B,
            VALID_COMMIT_A,
            VALID_REVERT_A,
            VALID_COUNTER_VAULT,
            VALID_VALUE_IN
        );
    }

    /// @notice Test 5: CRIT-ZK2 - Guard OFF allows field-wrapping balance overflow; Guard ON enforces ceiling
    function test_Counterfactual_CRIT_ZK2_FieldOverflowValueReverts() public {
        // Step A: Guard OFF permits value >= 10^36 (Vulnerable state)
        verifier.setGuards(ZKVerifierTestbench.GuardConfig({
            enforceValueBound: false, // Guard OFF
            enforceCounterVaultNonZero: true,
            enforceMessageBinding: true,
            enforceNullifierUniqueness: true,
            enforceTreeNumber: true
        }));

        bool vulnSuccess = verifier.settleDvPInitiator(
            VALID_MESSAGE,
            0,
            VALID_ROOT,
            VALID_NULLIFIER,
            VALID_COMMIT_B,
            VALID_COMMIT_A,
            VALID_REVERT_A,
            VALID_COUNTER_VAULT,
            FIELD_OVERFLOW_VALUE
        );
        assertTrue(vulnSuccess, "Guard OFF permits value >= 10^36");

        // Step B: Guard ON strictly enforces VALUE_BOUND_CEILING (10^36)
        verifier.setGuards(ZKVerifierTestbench.GuardConfig({
            enforceValueBound: true, // Guard ON
            enforceCounterVaultNonZero: true,
            enforceMessageBinding: true,
            enforceNullifierUniqueness: true,
            enforceTreeNumber: true
        }));

        bytes32 freshNullifier = keccak256("fresh-nullifier-overflow-test");
        vm.expectRevert(abi.encodeWithSelector(ZKVerifierTestbench.ValueBoundExceeded.selector, FIELD_OVERFLOW_VALUE, 1e36));
        verifier.settleDvPInitiator(
            VALID_MESSAGE,
            0,
            VALID_ROOT,
            freshNullifier,
            VALID_COMMIT_B,
            VALID_COMMIT_A,
            VALID_REVERT_A,
            VALID_COUNTER_VAULT,
            FIELD_OVERFLOW_VALUE
        );
    }

    /// @notice Test 6: CRIT-ZK3 - Nullifier double-spend attempt reverts deterministically
    function test_Counterfactual_CRIT_ZK3_NullifierDoubleSpendReverts() public {
        // First spend succeeds
        verifier.settleDvPInitiator(
            VALID_MESSAGE,
            0,
            VALID_ROOT,
            VALID_NULLIFIER,
            VALID_COMMIT_B,
            VALID_COMMIT_A,
            VALID_REVERT_A,
            VALID_COUNTER_VAULT,
            VALID_VALUE_IN
        );

        // Second spend with same nullifier reverts
        vm.expectRevert(abi.encodeWithSelector(ZKVerifierTestbench.NullifierAlreadySpent.selector, VALID_NULLIFIER));
        verifier.settleDvPInitiator(
            VALID_MESSAGE,
            0,
            VALID_ROOT,
            VALID_NULLIFIER,
            VALID_COMMIT_B,
            VALID_COMMIT_A,
            VALID_REVERT_A,
            VALID_COUNTER_VAULT,
            VALID_VALUE_IN
        );
    }

    /// @notice Test 7: CRIT-ZK4 - Statement length mismatch in Groth16 verification reverts
    function test_Counterfactual_CRIT_ZK4_StatementLengthMismatchReverts() public {
        ZKVerifierTestbench.VerifyingKey memory vk;
        vk.ic = new ZKVerifierTestbench.G1Point[](5); // Expects 4 inputs (length + 1 == 5)

        ZKVerifierTestbench.SnarkProof memory proof;
        uint256[] memory badInputs = new uint256[](6); // 6 inputs provided != 4 expected

        vm.expectRevert(abi.encodeWithSelector(ZKVerifierTestbench.StatementLengthMismatch.selector, 4, 6));
        verifier.verifyProof(vk, proof, badInputs);
    }

    /// @notice Test 8: CRIT-ZK5 - Scalar field overflow (signal >= r) reverts
    function test_Counterfactual_CRIT_ZK5_ScalarFieldOverflowReverts() public {
        ZKVerifierTestbench.VerifyingKey memory vk;
        vk.ic = new ZKVerifierTestbench.G1Point[](2); // Expects 1 input

        ZKVerifierTestbench.SnarkProof memory proof;
        uint256[] memory inputs = new uint256[](1);
        inputs[0] = verifier.SNARK_SCALAR_FIELD() + 500; // Overflow scalar field

        vm.expectRevert(abi.encodeWithSelector(ZKVerifierTestbench.ScalarFieldOverflow.selector, inputs[0], verifier.SNARK_SCALAR_FIELD()));
        verifier.verifyProof(vk, proof, inputs);
    }

    // =========================================================================
    // STATE 3: EDGE CASES & INTERRUPTED RECOVERY INVARIANTS
    // =========================================================================

    /// @notice Test 9: CRIT-ZK6 - Unconstrained CounterVault defense (api.AssertIsDifferent(StCounterVault, 0))
    function test_EdgeCase_CRIT_ZK6_ZeroCounterVaultGuardReverts() public {
        // Step A: Guard OFF permits zero counterVault (unconstrained assignment)
        verifier.setGuards(ZKVerifierTestbench.GuardConfig({
            enforceValueBound: true,
            enforceCounterVaultNonZero: false, // Guard OFF
            enforceMessageBinding: true,
            enforceNullifierUniqueness: true,
            enforceTreeNumber: true
        }));

        bool vulnSuccess = verifier.settleDvPInitiator(
            VALID_MESSAGE,
            0,
            VALID_ROOT,
            VALID_NULLIFIER,
            VALID_COMMIT_B,
            VALID_COMMIT_A,
            VALID_REVERT_A,
            0, // Zero counterVault
            VALID_VALUE_IN
        );
        assertTrue(vulnSuccess, "Guard OFF allows zero counterVault");

        // Step B: Guard ON strictly rejects zero counterVault
        verifier.setGuards(ZKVerifierTestbench.GuardConfig({
            enforceValueBound: true,
            enforceCounterVaultNonZero: true, // Guard ON
            enforceMessageBinding: true,
            enforceNullifierUniqueness: true,
            enforceTreeNumber: true
        }));

        bytes32 freshNullifier = keccak256("fresh-nullifier-zero-vault");
        vm.expectRevert(ZKVerifierTestbench.ZeroCounterVaultRejected.selector);
        verifier.settleDvPInitiator(
            VALID_MESSAGE,
            0,
            VALID_ROOT,
            freshNullifier,
            VALID_COMMIT_B,
            VALID_COMMIT_A,
            VALID_REVERT_A,
            0, // Zero counterVault
            VALID_VALUE_IN
        );
    }

    /// @notice Test 10: CRIT-ZK7 - Cross-swap message binding defense (HIGH-5: StMessage == StCommitA)
    function test_EdgeCase_CRIT_ZK7_UnconstrainedStMessageReverts() public {
        // Step A: Guard OFF permits unlinked swap message
        verifier.setGuards(ZKVerifierTestbench.GuardConfig({
            enforceValueBound: true,
            enforceCounterVaultNonZero: true,
            enforceMessageBinding: false, // Guard OFF
            enforceNullifierUniqueness: true,
            enforceTreeNumber: true
        }));

        bool vulnSuccess = verifier.settleDvPInitiator(
            0x9999, // Unlinked message != StCommitA
            0,
            VALID_ROOT,
            VALID_NULLIFIER,
            VALID_COMMIT_B,
            VALID_COMMIT_A,
            VALID_REVERT_A,
            VALID_COUNTER_VAULT,
            VALID_VALUE_IN
        );
        assertTrue(vulnSuccess, "Guard OFF permits unlinked swap message");

        // Step B: Guard ON strictly enforces StMessage == StCommitA
        verifier.setGuards(ZKVerifierTestbench.GuardConfig({
            enforceValueBound: true,
            enforceCounterVaultNonZero: true,
            enforceMessageBinding: true, // Guard ON
            enforceNullifierUniqueness: true,
            enforceTreeNumber: true
        }));

        bytes32 freshNullifier = keccak256("fresh-nullifier-binding-test");
        vm.expectRevert(abi.encodeWithSelector(ZKVerifierTestbench.MessageCommitmentMismatch.selector, 0x9999, VALID_COMMIT_A));
        verifier.settleDvPInitiator(
            0x9999, // Unlinked message
            0,
            VALID_ROOT,
            freshNullifier,
            VALID_COMMIT_B,
            VALID_COMMIT_A,
            VALID_REVERT_A,
            VALID_COUNTER_VAULT,
            VALID_VALUE_IN
        );
    }

    /// @notice Test 11: Fuzz test (256 runs) proving all mutated values >= 10^36 revert
    function testFuzz_ArbitraryMalformedValuesRevert(uint256 fuzzValue) public {
        vm.assume(fuzzValue >= 1e36);
        bytes32 fuzzNullifier = keccak256(abi.encodePacked("fuzz-nullifier", fuzzValue));

        vm.expectRevert(abi.encodeWithSelector(ZKVerifierTestbench.ValueBoundExceeded.selector, fuzzValue, 1e36));
        verifier.settleDvPInitiator(
            VALID_MESSAGE,
            0,
            VALID_ROOT,
            fuzzNullifier,
            VALID_COMMIT_B,
            VALID_COMMIT_A,
            VALID_REVERT_A,
            VALID_COUNTER_VAULT,
            fuzzValue
        );
    }
}
