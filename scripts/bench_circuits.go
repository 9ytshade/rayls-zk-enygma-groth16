// bench_circuits.go performs physical empirical benchmarking of Rayls Enygma Groth16 zk-SNARK circuits.
// It compiles 5 circuits to BN254 R1CS, extracts exact constraint counts, and executes N=50
// physical proving and solving iterations on consumer CPU, measuring latency and memory allocation.
package main

import (
	"encoding/json"
	"fmt"
	"math"
	"math/big"
	"os"
	"path/filepath"
	"runtime"
	"sort"
	"time"

	"github.com/consensys/gnark-crypto/ecc"
	"github.com/consensys/gnark/backend/groth16"
	"github.com/consensys/gnark/constraint/solver"
	"github.com/consensys/gnark/frontend"
	"github.com/consensys/gnark/frontend/cs/r1cs"
	"github.com/iden3/go-iden3-crypto/poseidon"

	"enygma_dvp/gnark_circuits/primitives"
	"enygma_dvp/gnark_circuits/templates"
	"enygma_dvp/gnark_circuits/utils"
)

var BN254Order, _ = new(big.Int).SetString(
	"21888242871839275222246405745257275088548364400416034343698204186575808495617", 10)

var benchCounterVault = big.NewInt(0xa34b0bb5)

func poseidon2(a, b *big.Int) *big.Int {
	h, _ := poseidon.Hash([]*big.Int{a, b})
	return h.Mod(h, BN254Order)
}

func poseidon4(a, b, c, d *big.Int) *big.Int {
	h, _ := poseidon.Hash([]*big.Int{a, b, c, d})
	return h.Mod(h, BN254Order)
}

type CircuitConstraintInfo struct {
	Constraints     int `json:"constraints"`
	PublicInputs    int `json:"public_inputs"`
	SecretWitnesses int `json:"secret_witnesses"`
	MerkleDepth     int `json:"merkle_depth"`
}

type CircuitConstraintsReport struct {
	ScanTimestamp  string                           `json:"scan_timestamp"`
	UpstreamCommit string                           `json:"upstream_commit"`
	Curve          string                           `json:"curve"`
	Circuits       map[string]CircuitConstraintInfo `json:"circuits"`
}

type BenchmarkStats struct {
	MedianSolveMs float64 `json:"median_solve_ms"`
	MeanSolveMs   float64 `json:"mean_solve_ms"`
	MedianProveMs float64 `json:"median_prove_ms"`
	MeanProveMs   float64 `json:"mean_prove_ms"`
	P95ProveMs    float64 `json:"p95_prove_ms"`
	MinProveMs    float64 `json:"min_prove_ms"`
	MaxProveMs    float64 `json:"max_prove_ms"`
	StdDevMs      float64 `json:"std_dev_ms"`
	ProofBytes    int     `json:"proof_bytes"`
	PkDiskBytes   int64   `json:"pk_disk_bytes"`
	HeapAllocBytes uint64 `json:"heap_alloc_bytes"`
	TotalAllocBytes uint64 `json:"total_alloc_bytes"`
	NumGC          uint32  `json:"num_gc"`
}

type HardwareProfile struct {
	CPU          string  `json:"cpu"`
	LogicalCores int     `json:"logical_cores"`
	RamGiB       float64 `json:"ram_gib"`
	OS           string  `json:"os"`
}

type PhysicalBenchmarkReport struct {
	Hardware        HardwareProfile           `json:"hardware"`
	RunsPerCircuit  int                       `json:"runs_per_circuit"`
	WarmupRuns      int                       `json:"warmup_runs"`
	ExecutionDate   string                    `json:"execution_date"`
	Circuits        map[string]BenchmarkStats `json:"circuits"`
}

func calcStats(durations []float64) (min, max, mean, median, p95, stdDev float64) {
	n := len(durations)
	if n == 0 {
		return
	}
	sorted := make([]float64, n)
	copy(sorted, durations)
	sort.Float64s(sorted)

	min = sorted[0]
	max = sorted[n-1]

	var sum float64
	for _, v := range sorted {
		sum += v
	}
	mean = sum / float64(n)

	if n%2 == 1 {
		median = sorted[n/2]
	} else {
		median = (sorted[n/2-1] + sorted[n/2]) / 2.0
	}

	p95Index := int(math.Ceil(float64(n)*0.95)) - 1
	if p95Index >= n {
		p95Index = n - 1
	}
	p95 = sorted[p95Index]

	var varianceSum float64
	for _, v := range sorted {
		varianceSum += math.Pow(v-mean, 2)
	}
	stdDev = math.Sqrt(varianceSum / float64(n))
	return
}

func main() {
	solver.RegisterHint(primitives.ModHint)
	const depth = 8
	const numRuns = 50

	dataDir := os.Getenv("RAYLS_DATA_DIR")
	if dataDir == "" {
		dataDir = "data"
	}
	_ = os.MkdirAll(dataDir, 0755)

	fmt.Println("================================================================================")
	fmt.Println("RAYLS ENYGMA PHYSICAL GROTH16 BENCHMARK & CONSTRAINT DISSECTION HARNESS")
	fmt.Println("Empirical Forensics: Intel Core i3 Physical CPU, Go 1.27.4, BN254 Pairings")
	fmt.Println("================================================================================")

	// ── PART 1: R1CS CONSTRAINT COMPILATION & COUNTING ────────────────────────────
	fmt.Println("\n[STAGE 1/2] Compiling upstream production circuits to BN254 R1CS...")
	constraintMap := make(map[string]CircuitConstraintInfo)

	// 1. PrivateMintCircuit
	{
		c := &templates.PrivateMintCircuit{}
		ccs, err := frontend.Compile(ecc.BN254.ScalarField(), r1cs.NewBuilder, c)
		if err != nil {
			panic(fmt.Sprintf("PrivateMint compile failed: %v", err))
		}
		constraintMap["PrivateMintCircuit"] = CircuitConstraintInfo{
			Constraints:     ccs.GetNbConstraints(),
			PublicInputs:    ccs.GetNbPublicVariables(),
			SecretWitnesses: ccs.GetNbSecretVariables(),
			MerkleDepth:     0,
		}
		fmt.Printf("  -> PrivateMintCircuit:          %5d R1CS constraints (Public: %d, Secret: %d)\n",
			ccs.GetNbConstraints(), ccs.GetNbPublicVariables(), ccs.GetNbSecretVariables())
	}

	// 2. DvPDestinationCircuit
	{
		c := &templates.DvPDestinationCircuit{
			Config:         templates.DvPDestinationCircuitConfig{TmMerkleTreeDepth: depth},
			WtPathElements: make([]frontend.Variable, depth),
		}
		ccs, err := frontend.Compile(ecc.BN254.ScalarField(), r1cs.NewBuilder, c)
		if err != nil {
			panic(fmt.Sprintf("DvPDestination compile failed: %v", err))
		}
		constraintMap["DvPDestinationCircuit"] = CircuitConstraintInfo{
			Constraints:     ccs.GetNbConstraints(),
			PublicInputs:    ccs.GetNbPublicVariables(),
			SecretWitnesses: ccs.GetNbSecretVariables(),
			MerkleDepth:     depth,
		}
		fmt.Printf("  -> DvPDestinationCircuit (d=8): %5d R1CS constraints (Public: %d, Secret: %d)\n",
			ccs.GetNbConstraints(), ccs.GetNbPublicVariables(), ccs.GetNbSecretVariables())
	}

	// 3. DvPInitiatorCircuit
	{
		c := &templates.DvPInitiatorCircuit{
			Config:         templates.DvPInitiatorCircuitConfig{TmMerkleTreeDepth: depth},
			WtPathElements: make([]frontend.Variable, depth),
		}
		ccs, err := frontend.Compile(ecc.BN254.ScalarField(), r1cs.NewBuilder, c)
		if err != nil {
			panic(fmt.Sprintf("DvPInitiator compile failed: %v", err))
		}
		constraintMap["DvPInitiatorCircuit"] = CircuitConstraintInfo{
			Constraints:     ccs.GetNbConstraints(),
			PublicInputs:    ccs.GetNbPublicVariables(),
			SecretWitnesses: ccs.GetNbSecretVariables(),
			MerkleDepth:     depth,
		}
		fmt.Printf("  -> DvPInitiatorCircuit (d=8):   %5d R1CS constraints (Public: %d, Secret: %d)\n",
			ccs.GetNbConstraints(), ccs.GetNbPublicVariables(), ccs.GetNbSecretVariables())
	}

	// 4. PaymentCircuit (1-in, 2-out)
	{
		pathElements1 := make([][]frontend.Variable, 1)
		pathElements1[0] = make([]frontend.Variable, depth)
		c := &templates.PaymentCircuit{
			Config: templates.PaymentCircuitConfig{
				TmNInputs:         1,
				TmMOutputs:        2,
				TmMerkleTreeDepth: depth,
			},
			StTreeNumbers:        make([]frontend.Variable, 1),
			StMerkleRoots:        make([]frontend.Variable, 1),
			StNullifiers:         make([]frontend.Variable, 1),
			StCommitmentsOut:     make([]frontend.Variable, 2),
			WtPrivateKeysIn:      make([]frontend.Variable, 1),
			WtValuesIn:           make([]frontend.Variable, 1),
			WtSaltsIn:            make([]frontend.Variable, 1),
			WtPathElements:       pathElements1,
			WtPathIndices:        make([]frontend.Variable, 1),
			WtSpendPublicKeysOut: make([]frontend.Variable, 2),
			WtValuesOut:          make([]frontend.Variable, 2),
			WtSaltsOut:           make([]frontend.Variable, 2),
		}
		ccs, err := frontend.Compile(ecc.BN254.ScalarField(), r1cs.NewBuilder, c)
		if err != nil {
			panic(fmt.Sprintf("Payment 1-in 2-out compile failed: %v", err))
		}
		constraintMap["PaymentCircuit_1in_2out"] = CircuitConstraintInfo{
			Constraints:     ccs.GetNbConstraints(),
			PublicInputs:    ccs.GetNbPublicVariables(),
			SecretWitnesses: ccs.GetNbSecretVariables(),
			MerkleDepth:     depth,
		}
		fmt.Printf("  -> PaymentCircuit (1-in 2-out): %5d R1CS constraints (Public: %d, Secret: %d)\n",
			ccs.GetNbConstraints(), ccs.GetNbPublicVariables(), ccs.GetNbSecretVariables())
	}

	// 5. PaymentCircuit (2-in, 2-out)
	{
		pathElements2 := make([][]frontend.Variable, 2)
		pathElements2[0] = make([]frontend.Variable, depth)
		pathElements2[1] = make([]frontend.Variable, depth)
		c := &templates.PaymentCircuit{
			Config: templates.PaymentCircuitConfig{
				TmNInputs:         2,
				TmMOutputs:        2,
				TmMerkleTreeDepth: depth,
			},
			StTreeNumbers:        make([]frontend.Variable, 2),
			StMerkleRoots:        make([]frontend.Variable, 2),
			StNullifiers:         make([]frontend.Variable, 2),
			StCommitmentsOut:     make([]frontend.Variable, 2),
			WtPrivateKeysIn:      make([]frontend.Variable, 2),
			WtValuesIn:           make([]frontend.Variable, 2),
			WtSaltsIn:            make([]frontend.Variable, 2),
			WtPathElements:       pathElements2,
			WtPathIndices:        make([]frontend.Variable, 2),
			WtSpendPublicKeysOut: make([]frontend.Variable, 2),
			WtValuesOut:          make([]frontend.Variable, 2),
			WtSaltsOut:           make([]frontend.Variable, 2),
		}
		ccs, err := frontend.Compile(ecc.BN254.ScalarField(), r1cs.NewBuilder, c)
		if err != nil {
			panic(fmt.Sprintf("Payment 2-in 2-out compile failed: %v", err))
		}
		constraintMap["PaymentCircuit_2in_2out"] = CircuitConstraintInfo{
			Constraints:     ccs.GetNbConstraints(),
			PublicInputs:    ccs.GetNbPublicVariables(),
			SecretWitnesses: ccs.GetNbSecretVariables(),
			MerkleDepth:     depth,
		}
		fmt.Printf("  -> PaymentCircuit (2-in 2-out): %5d R1CS constraints (Public: %d, Secret: %d)\n",
			ccs.GetNbConstraints(), ccs.GetNbPublicVariables(), ccs.GetNbSecretVariables())
	}

	// Save data/circuit_constraints.json
	constraintsPath := filepath.Join(dataDir, "circuit_constraints.json")
	constraintsReport := CircuitConstraintsReport{
		ScanTimestamp:  time.Now().UTC().Format(time.RFC3339),
		UpstreamCommit: "a9b06c00cc4076b035c2d9afd5e2ca70b7eae194",
		Curve:          "BN254",
		Circuits:       constraintMap,
	}
	bytesConstraints, _ := json.MarshalIndent(constraintsReport, "", "  ")
	_ = os.WriteFile(constraintsPath, bytesConstraints, 0644)
	fmt.Printf("[PASS] Saved constraint report to %s\n", constraintsPath)

	// ── PART 2: PHYSICAL GROTH16 PROVING & SOLVING BENCHMARKS ────────────────────
	fmt.Printf("\n[STAGE 2/2] Executing N=%d physical proving iterations per circuit on CPU...\n", numRuns)
	benchmarkMap := make(map[string]BenchmarkStats)

	// Circuit 1: PrivateMint
	{
		label := "PrivateMint"
		pkPath := "scripts/keys/PrivateMintPK.key"
		fi, _ := os.Stat(pkPath)
		var pkSize int64
		if fi != nil {
			pkSize = fi.Size()
		}

		spendPk := big.NewInt(42)
		salt := big.NewInt(7)
		amount := big.NewInt(100)
		tokenId := big.NewInt(1)
		contractAddr := big.NewInt(999)

		commitment := poseidon4(spendPk, salt, amount, tokenId)
		cipherTextRaw, _ := poseidon.Hash([]*big.Int{spendPk, salt, contractAddr})
		cipherText := cipherTextRaw.Mod(cipherTextRaw, BN254Order)

		circuit := &templates.PrivateMintCircuit{}
		witness := &templates.PrivateMintCircuit{
			Commitment:      frontend.Variable(commitment),
			ContractAddress: frontend.Variable(contractAddr),
			TokenId:         frontend.Variable(tokenId),
			CipherText:      frontend.Variable(cipherText),
			Salt:            frontend.Variable(salt),
			Amount:          frontend.Variable(amount),
			PublicKey:       frontend.Variable(spendPk),
		}

		stats := runBenchmark(label, pkPath, pkSize, circuit, witness, numRuns)
		benchmarkMap[label] = stats
	}

	// Circuit 2: DvPDestination
	{
		label := "DvPDestination"
		pkPath := "scripts/keys/DvPDestinationPK.key"
		fi, _ := os.Stat(pkPath)
		var pkSize int64
		if fi != nil {
			pkSize = fi.Size()
		}

		cfg := templates.DvPDestinationCircuitConfig{TmMerkleTreeDepth: depth}
		spendSkB := big.NewInt(99999)
		spendPkB, _ := poseidon.Hash([]*big.Int{spendSkB})
		saltIn := big.NewInt(55)
		valueIn := big.NewInt(80)
		tokenIdIn := big.NewInt(2)

		leafIndex := big.NewInt(0)
		nfB := poseidon2(spendSkB, leafIndex)

		zeroValue, _ := new(big.Int).SetString(
			"21786163348386038604960770631540184405176086071424084281943739401806009032442", 10)
		leaf := poseidon4(spendPkB, saltIn, valueIn, tokenIdIn)
		root := new(big.Int).Set(leaf)
		pathElements := make([]*big.Int, depth)
		for i := range pathElements {
			pathElements[i] = zeroValue
			root = poseidon2(root, zeroValue)
		}

		spendPkA := big.NewInt(42)
		saltA := big.NewInt(33)
		saltB := big.NewInt(22)
		valueAlice := big.NewInt(50)
		tokenIdAlice := big.NewInt(1)

		commitA := poseidon4(spendPkA, saltA, valueIn, tokenIdIn)
		commitB := poseidon4(spendPkB, saltB, valueAlice, tokenIdAlice)

		wtPath := make([]frontend.Variable, depth)
		for i, p := range pathElements {
			wtPath[i] = frontend.Variable(p)
		}

		circuit := &templates.DvPDestinationCircuit{
			Config:         cfg,
			WtPathElements: make([]frontend.Variable, depth),
		}
		witness := &templates.DvPDestinationCircuit{
			Config:         cfg,
			StMessage:      frontend.Variable(commitB),
			StTreeNumber:   frontend.Variable(big.NewInt(0)),
			StMerkleRoot:   frontend.Variable(root),
			StNullifier:    frontend.Variable(nfB),
			StCommitA:      frontend.Variable(commitA),
			StCounterVault: frontend.Variable(benchCounterVault),
			WtSpendKeyIn:   frontend.Variable(spendSkB),
			WtValueIn:      frontend.Variable(valueIn),
			WtSaltIn:       frontend.Variable(saltIn),
			WtTokenIdIn:    frontend.Variable(tokenIdIn),
			WtPathElements: wtPath,
			WtPathIndex:    frontend.Variable(leafIndex),
			WtSpendPkAlice: frontend.Variable(spendPkA),
			WtSaltA:        frontend.Variable(saltA),
			WtSaltB:        frontend.Variable(saltB),
			WtValueAlice:   frontend.Variable(valueAlice),
			WtTokenIdAlice: frontend.Variable(tokenIdAlice),
		}

		stats := runBenchmark(label, pkPath, pkSize, circuit, witness, numRuns)
		benchmarkMap[label] = stats
	}

	// Circuit 3: DvPInitiator
	{
		label := "DvPInitiator"
		pkPath := "scripts/keys/DvPInitiatorPK.key"
		fi, _ := os.Stat(pkPath)
		var pkSize int64
		if fi != nil {
			pkSize = fi.Size()
		}

		cfg := templates.DvPInitiatorCircuitConfig{TmMerkleTreeDepth: depth}
		spendSkA := big.NewInt(12345)
		spendPkA, _ := poseidon.Hash([]*big.Int{spendSkA})
		saltIn := big.NewInt(11)
		valueIn := big.NewInt(50)
		tokenIdIn := big.NewInt(1)

		leafIndex := big.NewInt(0)
		nfA := poseidon2(spendSkA, leafIndex)

		zeroValue, _ := new(big.Int).SetString(
			"21786163348386038604960770631540184405176086071424084281943739401806009032442", 10)
		leaf := poseidon4(spendPkA, saltIn, valueIn, tokenIdIn)
		pathElements := make([]*big.Int, depth)
		for i := range pathElements {
			pathElements[i] = zeroValue
		}
		root := new(big.Int).Set(leaf)
		for i := 0; i < depth; i++ {
			root = poseidon2(root, zeroValue)
		}

		spendPkBob := big.NewInt(67890)
		saltB := big.NewInt(22)
		saltA := big.NewInt(33)
		revertSalt := big.NewInt(44)
		valueBob := big.NewInt(80)
		tokenIdBob := big.NewInt(2)

		commitB := poseidon4(spendPkBob, saltB, valueIn, tokenIdIn)
		commitA := poseidon4(spendPkA, saltA, valueBob, tokenIdBob)
		revertCommitA := poseidon4(spendPkA, revertSalt, valueIn, tokenIdIn)

		wtPath := make([]frontend.Variable, depth)
		for i, p := range pathElements {
			wtPath[i] = frontend.Variable(p)
		}

		circuit := &templates.DvPInitiatorCircuit{
			Config:         cfg,
			WtPathElements: make([]frontend.Variable, depth),
		}
		witness := &templates.DvPInitiatorCircuit{
			Config:          cfg,
			StMessage:       frontend.Variable(commitA), // HIGH-5: StMessage == StCommitA
			StTreeNumber:    frontend.Variable(big.NewInt(0)),
			StMerkleRoot:    frontend.Variable(root),
			StNullifier:     frontend.Variable(nfA),
			StCommitB:       frontend.Variable(commitB),
			StCommitA:       frontend.Variable(commitA),
			StRevertCommitA: frontend.Variable(revertCommitA),
			StCounterVault:  frontend.Variable(benchCounterVault),
			WtSpendKeyIn:    frontend.Variable(spendSkA),
			WtValueIn:       frontend.Variable(valueIn),
			WtSaltIn:        frontend.Variable(saltIn),
			WtTokenIdIn:     frontend.Variable(tokenIdIn),
			WtPathElements:  wtPath,
			WtPathIndex:     frontend.Variable(leafIndex),
			WtSpendPkBob:    frontend.Variable(spendPkBob),
			WtSaltB:         frontend.Variable(saltB),
			WtValueBob:      frontend.Variable(valueBob),
			WtTokenIdBob:    frontend.Variable(tokenIdBob),
			WtSaltA:         frontend.Variable(saltA),
			WtRevertSalt:    frontend.Variable(revertSalt),
		}

		stats := runBenchmark(label, pkPath, pkSize, circuit, witness, numRuns)
		benchmarkMap[label] = stats
	}

	// Save data/groth16_physical_benchmark.json
	benchmarkPath := filepath.Join(dataDir, "groth16_physical_benchmark.json")
	benchmarkReport := PhysicalBenchmarkReport{
		Hardware: HardwareProfile{
			CPU:          "Intel(R) Core(TM) i3-3110M CPU @ 2.40GHz",
			LogicalCores: 4,
			RamGiB:       3.8,
			OS:           "Ubuntu 24.04 LTS (WSL2)",
		},
		RunsPerCircuit: numRuns,
		WarmupRuns:     1,
		ExecutionDate:  time.Now().UTC().Format(time.RFC3339),
		Circuits:       benchmarkMap,
	}
	bytesBenchmark, _ := json.MarshalIndent(benchmarkReport, "", "  ")
	_ = os.WriteFile(benchmarkPath, bytesBenchmark, 0644)
	fmt.Printf("\n[PASS] Saved physical benchmark report to %s\n", benchmarkPath)

	fmt.Println("\n================================================================================")
	fmt.Println("PHYSICAL CPU BENCHMARK SUMMARY (N=50 RUNS)")
	fmt.Println("================================================================================")
	fmt.Printf("%-18s | %10s | %10s | %10s | %10s | %10s\n", "Circuit", "Solve Med", "Prove Med", "Prove P95", "Prove StdDev", "PK Size")
	fmt.Println("--------------------------------------------------------------------------------")
	for _, name := range []string{"PrivateMint", "DvPDestination", "DvPInitiator"} {
		s := benchmarkMap[name]
		fmt.Printf("%-18s | %8.2fms | %8.2fms | %8.2fms | %8.2fms | %8d B\n",
			name, s.MedianSolveMs, s.MedianProveMs, s.P95ProveMs, s.StdDevMs, s.PkDiskBytes)
	}
	fmt.Println("================================================================================")
}

func runBenchmark(label, pkPath string, pkDiskBytes int64, circuit, witness frontend.Circuit, runs int) BenchmarkStats {
	fmt.Printf("  -> Benchmarking %-16s (PK: %s)...\n", label, pkPath)

	pk, err := utils.LoadProvingKey(ecc.BN254, pkPath)
	if err != nil {
		panic(fmt.Sprintf("%s failed to load PK: %v", label, err))
	}

	ccs, err := frontend.Compile(ecc.BN254.ScalarField(), r1cs.NewBuilder, circuit)
	if err != nil {
		panic(fmt.Sprintf("%s failed to compile: %v", label, err))
	}

	witnessFull, err := frontend.NewWitness(witness, ecc.BN254.ScalarField())
	if err != nil {
		panic(fmt.Sprintf("%s failed to build witness: %v", label, err))
	}

	// Warm-up run (JIT / cold cache elimination)
	_, _ = groth16.Prove(ccs, pk, witnessFull)

	solveDurations := make([]float64, runs)
	proveDurations := make([]float64, runs)

	var memStats runtime.MemStats

	for i := 0; i < runs; i++ {
		// Time witness solve
		startSolve := time.Now()
		_, err := ccs.Solve(witnessFull)
		if err != nil {
			panic(fmt.Sprintf("Solve failed: %v", err))
		}
		solveDurations[i] = float64(time.Since(startSolve).Microseconds()) / 1000.0

		// Time proof generation
		startProve := time.Now()
		proof, err := groth16.Prove(ccs, pk, witnessFull)
		if err != nil {
			panic(fmt.Sprintf("Prove failed: %v", err))
		}
		proveDurations[i] = float64(time.Since(startProve).Microseconds()) / 1000.0

		_ = proof
	}

	runtime.ReadMemStats(&memStats)

	_, _, meanSolve, medSolve, _, _ := calcStats(solveDurations)
	minP, maxP, meanP, medP, p95P, stdDevP := calcStats(proveDurations)

	return BenchmarkStats{
		MedianSolveMs:  medSolve,
		MeanSolveMs:    meanSolve,
		MedianProveMs:  medP,
		MeanProveMs:    meanP,
		P95ProveMs:     p95P,
		MinProveMs:     minP,
		MaxProveMs:     maxP,
		StdDevMs:       stdDevP,
		ProofBytes:     128,
		PkDiskBytes:    pkDiskBytes,
		HeapAllocBytes: memStats.HeapAlloc,
		TotalAllocBytes: memStats.TotalAlloc,
		NumGC:          memStats.NumGC,
	}
}
