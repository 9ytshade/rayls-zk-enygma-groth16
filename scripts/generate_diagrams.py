#!/usr/bin/env python3
"""
generate_diagrams.py - High-Resolution Institutional Diagram Suite for Week 9 Research
Adheres strictly to the Noir Ventures Rayls Design Palette, dynamic padding standards,
and mobile-first readability (font size >= 14pt, zero clipping, balanced 1600x900 canvas).

Generates 7 Comprehensive Architectural & Empirical Visual Assets:
- Diagram 1: Groth16 Prover Pipeline & BN254 Pairing Verification Engine
- Diagram 2: Rayls Enygma Circuit Constraint Anatomy & Poseidon Hash Costs
- Diagram 3: Three-State Invariant Security Architecture & Defect Matrix
- Diagram 4: Physical CPU Prover Latency vs. Mainnet 72957 Fork Gas
- Diagram 5: Poseidon Hash Permutation Architecture & Merkle Tree Verification
- Diagram 6: Confidential DvP Settlement Sequence & Atomic Cross-Subnet Protocol
- Diagram 7: Rayls Mainnet 72957 Empirical Telemetry & Cadence Distribution
"""

import sys
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

LOGO_WHITE_PATH = ROOT.parent / "Brand_Guide" / "Rayls_Logo_Pack" / "PNG" / "Rayls_Logo_White.png"
LOGO_BLACK_PATH = ROOT.parent / "Brand_Guide" / "Rayls_Logo_Pack" / "PNG" / "Rayls_Logo_Black.png"

# Canvas dimensions
W, H = 1600, 900

# Noir Ventures Rayls Color Palette
C_BG = (24, 24, 28, 255)            # #18181C Dark canvas
C_CARD = (34, 34, 40, 255)          # #222228 Card surface
C_CARD_HEADER = (42, 42, 50, 255)   # #2A2A32
C_BORDER = (55, 55, 65, 255)        # #373741 Subtle border
C_BORDER_LIGHT = (75, 75, 90, 255)  # #4B4B5A Highlight border

C_YELLOW = (236, 251, 62, 255)      # #ECFB3E Rayls Lime / Yellow accent
C_PURPLE = (180, 154, 255, 255)     # #B49AFF Rayls Lavender / Soft Purple
C_GREEN = (80, 250, 123, 255)       # #50FA7B Verification green
C_RED = (255, 85, 85, 255)          # #FF5555 Rejection / Vulnerability red
C_BLUE = (120, 200, 255, 255)       # #78C8FF Informational blue
C_ORANGE = (255, 184, 108, 255)     # #FFB86C Alert orange

C_WHITE = (255, 255, 255, 255)
C_TEXT_LIGHT = (240, 240, 245, 255) # Off-white primary text
C_TEXT_MUTED = (165, 165, 180, 255) # Secondary muted text
C_BLACK = (17, 17, 20, 255)         # Dark for pill badge fills

# System fonts
FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_REG = r"C:\Windows\Fonts\segoeui.ttf"
FONT_MONO = r"C:\Windows\Fonts\consola.ttf"


def get_fonts():
    """Load institutional typography scale with minimum 14pt body."""
    return {
        "title": ImageFont.truetype(FONT_BOLD, 32),
        "subtitle": ImageFont.truetype(FONT_REG, 16),
        "pill": ImageFont.truetype(FONT_BOLD, 14),
        "card_hdr": ImageFont.truetype(FONT_BOLD, 19),
        "card_sub": ImageFont.truetype(FONT_REG, 15),
        "th": ImageFont.truetype(FONT_BOLD, 14),
        "td": ImageFont.truetype(FONT_REG, 14),
        "td_bold": ImageFont.truetype(FONT_BOLD, 14),
        "mono": ImageFont.truetype(FONT_MONO, 13),
        "mono_bold": ImageFont.truetype(FONT_MONO, 14),
        "stat_num": ImageFont.truetype(FONT_BOLD, 28),
        "stat_label": ImageFont.truetype(FONT_REG, 14),
        "body": ImageFont.truetype(FONT_REG, 14),
        "body_bold": ImageFont.truetype(FONT_BOLD, 14),
    }


def wrap_text_pixels(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list:
    """Break text into lines that strictly do not exceed max_w pixels."""
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = cur + " " + w if cur else w
        if font.getlength(test) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def paste_white_logo(img: Image.Image, right_margin: int = 76, top_y: int = 40):
    """Render high-contrast White Rayls Logo at top-right for dark backgrounds."""
    if LOGO_WHITE_PATH.exists():
        logo = Image.open(LOGO_WHITE_PATH).convert("RGBA")
        logo_h = 36
        logo_w = int(logo_h * logo.width / logo.height)
        logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        img.paste(logo, (W - logo_w - right_margin, top_y), logo)


def draw_header(draw: ImageDraw.Draw, fonts: dict, pill_text: str, title: str, subtitle: str):
    """Draw standardized brand header with dynamically padded pill badge."""
    pill_w = int(fonts["pill"].getlength(pill_text)) + 28
    draw.rounded_rectangle([76, 38, 76 + pill_w, 70], radius=6, fill=C_CARD, outline=C_YELLOW, width=1)
    draw.text((90, 45), pill_text, fill=C_YELLOW, font=fonts["pill"])

    draw.text((76, 84), title, fill=C_TEXT_LIGHT, font=fonts["title"])
    draw.text((76, 128), subtitle, fill=C_TEXT_MUTED, font=fonts["subtitle"])


# ==============================================================================
# DIAGRAM 1: GROTH16 PROVER PIPELINE & BN254 PAIRING VERIFICATION ENGINE
# ==============================================================================
def generate_diagram_1():
    out_path = ASSETS_DIR / "diagram_1_groth16_rtgs_pipeline.png"
    img = Image.new("RGBA", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    fonts = get_fonts()

    paste_white_logo(img)
    draw_header(
        draw,
        fonts,
        "CRYPTOGRAPHIC LIFECYCLE | SUCCINCT BN254 GROTH16 ENGINE",
        "Groth16 Prover Pipeline & BN254 Pairing Verification Engine",
        "End-to-End Cryptographic Flow from Client Witness Generation to On-Chain EVM Precompiles",
    )

    card_w = 460
    card_gap = 32
    start_x = 76
    y0, y1 = 175, 685

    stages = [
        {
            "num": "STAGE 1",
            "title": "Private Client Witness",
            "accent": C_PURPLE,
            "badge": "Off-Chain / Client Gateway",
            "items": [
                ("Input Blinding Factors:", "Poseidon(v, sn, pk_own)"),
                ("Merkle Tree Proof:", "8 Poseidon rounds (depth d=8)"),
                ("Scalar Range Check:", "valuebound.Assert(api, v, 10^36)"),
                ("Constraint System:", "R1CS BN254 Satisfiability"),
                ("R1CS Equation:", "A*s o B*s = C*s in F_q"),
                ("Median Solve Latency:", "13.37 ms (DvP Initiator)"),
                ("Execution Target:", "Lightweight Banking Node / Browser"),
            ],
        },
        {
            "num": "STAGE 2",
            "title": "gnark Prover Engine",
            "accent": C_YELLOW,
            "badge": "Physical CPU Computation",
            "items": [
                ("Circuit Compilation:", "4,077 BN254 R1CS Constraints"),
                ("MSM Multi-Scalar Mult:", "G1 & G2 Curve Operations"),
                ("Quotient Evaluation:", "Coset FFT / iFFT Polynomials"),
                ("SRS Toxic Waste:", "Alpha, Beta, Gamma, Delta Pinned"),
                ("Succinct Output Size:", "3 Group Elements (128 Bytes)"),
                ("Proof Structure:", "[A in G1, B in G2, C in G1]"),
                ("Physical Prove Time:", "415.35 ms median (p95: 717.33 ms)"),
            ],
        },
        {
            "num": "STAGE 3",
            "title": "EVM On-Chain Verification",
            "accent": C_GREEN,
            "badge": "Rayls Mainnet Fork 72957",
            "items": [
                ("Public Statements:", "8 Public Signals (256B) + IC[0]"),
                ("Linear Accumulation:", "vk_x = IC[0] + sum(x_i * IC[i+1])"),
                ("EIP-196 ecAdd (0x06):", "279 gas (point addition)"),
                ("EIP-196 ecMul (0x07):", "6,129 gas (scalar multiplication)"),
                ("EIP-197 ecPairing (0x08):", "181,138 gas (4 BN254 pairings)"),
                ("Total Measured Gas:", "249,739 gas (inc. wrapper)"),
                ("Native Settlement Fee:", "0.01438 RLS @ 57.60 Gwei"),
            ],
        },
    ]

    for i, s in enumerate(stages):
        cx0 = start_x + i * (card_w + card_gap)
        cx1 = cx0 + card_w
        draw.rounded_rectangle([cx0, y0, cx1, y1], radius=12, fill=C_CARD, outline=C_BORDER, width=2)

        draw.rounded_rectangle([cx0, y0, cx1, y0 + 64], radius=12, fill=C_CARD_HEADER)
        draw.text((cx0 + 20, y0 + 12), s["num"], fill=s["accent"], font=fonts["th"])
        draw.text((cx0 + 20, y0 + 34), s["title"], fill=C_WHITE, font=fonts["card_hdr"])

        bw = int(fonts["pill"].getlength(s["badge"])) + 16
        draw.rounded_rectangle([cx1 - bw - 16, y0 + 16, cx1 - 16, y0 + 44], radius=6, fill=C_BG, outline=s["accent"], width=1)
        draw.text((cx1 - bw - 8, y0 + 23), s["badge"], fill=s["accent"], font=fonts["pill"])

        draw.line([cx0, y0 + 64, cx1, y0 + 64], fill=C_BORDER, width=1)

        curr_y = y0 + 82
        for label, val in s["items"]:
            draw.text((cx0 + 20, curr_y), label, fill=C_TEXT_MUTED, font=fonts["body"])
            draw.text((cx0 + 20, curr_y + 20), val, fill=C_WHITE if "ms" not in val and "gas" not in val else s["accent"], font=fonts["mono_bold"])
            curr_y += 58

        if i < 2:
            arr_x = cx1 + 10
            arr_y = (y0 + y1) // 2
            draw.polygon([(arr_x, arr_y - 12), (arr_x + 12, arr_y), (arr_x, arr_y + 12)], fill=C_YELLOW)

    by0, by1 = 710, 850
    draw.rounded_rectangle([76, by0, W - 76, by1], radius=12, fill=C_CARD, outline=C_BORDER, width=2)

    draw.text((100, by0 + 18), "RTGS SUB-SECOND SLA BENCHMARK EVALUATION (CPMI-IOSCO PRINCIPLE 8)", fill=C_YELLOW, font=fonts["th"])
    sla_text = (
        "Client Prover Latency (p95: 717 ms) strictly fulfills the 1,000 ms RTGS proof threshold with a 28.3% safety margin on consumer hardware.\n"
        "Rayls Mainnet L1 block cadence (mean 1.34s) provides rapid probabilistic batch finality, while private subnets isolate enterprise execution."
    )
    draw.text((100, by0 + 46), sla_text, fill=C_TEXT_LIGHT, font=fonts["body"])

    stat_x = W - 380
    draw.line([stat_x - 30, by0 + 15, stat_x - 30, by1 - 15], fill=C_BORDER, width=1)
    draw.text((stat_x, by0 + 22), "TOTAL SETTLEMENT COST", fill=C_TEXT_MUTED, font=fonts["stat_label"])
    draw.text((stat_x, by0 + 44), "0.01438 RLS", fill=C_GREEN, font=fonts["stat_num"])
    draw.text((stat_x, by0 + 84), "249,739 Gas @ 57.60 Gwei", fill=C_PURPLE, font=fonts["pill"])

    img.save(out_path, "PNG")
    print(f"[OK] Generated Diagram 1: {out_path}")
    return out_path


# ==============================================================================
# DIAGRAM 2: RAYLS ENYGMA CIRCUIT CONSTRAINT ANATOMY & POSEIDON HASH COSTS
# ==============================================================================
def generate_diagram_2():
    out_path = ASSETS_DIR / "diagram_2_circuit_constraint_anatomy.png"
    img = Image.new("RGBA", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    fonts = get_fonts()

    paste_white_logo(img)
    draw_header(
        draw,
        fonts,
        "CIRCUIT ANATOMY | BN254 R1CS CONSTRAINT ANALYSIS",
        "Rayls Enygma Circuit Constraint Anatomy & Optimization",
        "Forensic Dissection of 5 Production gnark BN254 Circuits & Poseidon Hash Costs",
    )

    y0, y1 = 175, 850

    lx0, lx1 = 76, 940
    draw.rounded_rectangle([lx0, y0, lx1, y1], radius=12, fill=C_CARD, outline=C_BORDER, width=2)
    draw.rounded_rectangle([lx0, y0, lx1, y0 + 56], radius=12, fill=C_CARD_HEADER)
    draw.text((lx0 + 24, y0 + 16), "Production gnark Circuit Constraint Hierarchy", fill=C_WHITE, font=fonts["card_hdr"])
    draw.line([lx0, y0 + 56, lx1, y0 + 56], fill=C_BORDER, width=1)

    circuits = [
        ("PrivateMintCircuit", 802, "5 Public, 3 Secret (Depth 0)", C_BLUE),
        ("DvPDestinationCircuit (d=8)", 3778, "7 Public, 18 Secret (Depth 8)", C_PURPLE),
        ("DvPInitiatorCircuit (d=8)", 4077, "9 Public, 19 Secret (Depth 8)", C_YELLOW),
        ("PaymentCircuit (1-in, 2-out)", 4491, "8 Public, 19 Secret (Depth 8)", C_GREEN),
        ("PaymentCircuit (2-in, 2-out)", 7440, "11 Public, 31 Secret (Depth 8)", C_TEXT_LIGHT),
    ]

    max_c = 8704
    bar_start_x = lx0 + 24
    bar_max_w = lx1 - lx0 - 48
    curr_y = y0 + 74

    for name, count, desc, color in circuits:
        draw.text((bar_start_x, curr_y), name, fill=C_WHITE, font=fonts["td_bold"])
        draw.text((bar_start_x + 320, curr_y), desc, fill=C_TEXT_MUTED, font=fonts["td"])
        draw.text((lx1 - 140, curr_y), f"{count:,} R1CS", fill=color, font=fonts["mono_bold"])

        bar_y = curr_y + 24
        bar_w = int((count / max_c) * bar_max_w)
        draw.rounded_rectangle([bar_start_x, bar_y, bar_start_x + bar_max_w, bar_y + 16], radius=4, fill=C_BG)
        draw.rounded_rectangle([bar_start_x, bar_y, bar_start_x + bar_w, bar_y + 16], radius=4, fill=color)
        curr_y += 68

    callout_y = curr_y + 10
    draw.rounded_rectangle([bar_start_x, callout_y, lx1 - 24, y1 - 20], radius=10, fill=C_BG, outline=C_YELLOW, width=1)
    draw.text((bar_start_x + 18, callout_y + 16), "FORENSIC DISCOVERY: DOCUMENTATION VS. IMPLEMENTATION MISMATCH", fill=C_YELLOW, font=fonts["th"])
    disc_text = (
        "- Legacy Documentation Claim: 8,704 R1CS constraints for DvP settlement.\n"
        "- Upstream gnark Code Reality: 4,077 R1CS constraints (exact BN254 compilation).\n"
        "- Net Optimization: -4,627 constraints (-53.2% shrinkage) via custom Poseidon gadgets\n"
        "  and unified multi-scalar accumulator, enabling sub-500ms consumer proving."
    )
    draw.text((bar_start_x + 18, callout_y + 44), disc_text, fill=C_TEXT_LIGHT, font=fonts["body"])

    rx0, rx1 = 970, W - 76
    draw.rounded_rectangle([rx0, y0, rx1, y1], radius=12, fill=C_CARD, outline=C_BORDER, width=2)
    draw.rounded_rectangle([rx0, y0, rx1, y0 + 56], radius=12, fill=C_CARD_HEADER)
    draw.text((rx0 + 24, y0 + 16), "Cryptographic Gadgets & Cost Breakdown", fill=C_WHITE, font=fonts["card_hdr"])
    draw.line([rx0, y0 + 56, rx1, y0 + 56], fill=C_BORDER, width=1)

    cards = [
        {
            "title": "Poseidon Hash S-Box Cost (BN254)",
            "accent": C_PURPLE,
            "text": (
                "Parameter set: t=3 (2-in) and t=5 (4-in), alpha=5 S-box.\n"
                "Rounds: R_F=8 full rounds, R_P=56 partial rounds.\n"
                "R1CS Weight: ~240 constraints per 2-to-1 hash.\n"
                "Merkle Path (d=8): 8 hashes = 1,920 R1CS constraints\n"
                "(47.1% of entire DvP Initiator circuit budget)."
            ),
        },
        {
            "title": "ValueBound Range Proof Gadget",
            "accent": C_YELLOW,
            "text": (
                "Implementation: valuebound.Assert(api, v, 10^36).\n"
                "Restricts integer values to 120-bit ceiling (< 10^36).\n"
                "Security Mandate: Prevents BN254 scalar field overflow\n"
                "(r = 21888242871839275222246405745257275088548364...)\n"
                "Defends against malicious note wrapping attacks."
            ),
        },
        {
            "title": "Public Statement Calldata Footprint",
            "accent": C_GREEN,
            "text": (
                "Succinct Groth16 Proof: 128 bytes fixed.\n"
                "Public Inputs: 8 signals (256 bytes on-chain calldata).\n"
                "Total Calldata: 384 bytes per confidential settlement.\n"
                "Layer-1 Overhead: Minimal calldata gas footprint\n"
                "compared to 2,000+ byte STARK or PLONK proofs."
            ),
        },
    ]

    cy = y0 + 74
    for c in cards:
        draw.rounded_rectangle([rx0 + 20, cy, rx1 - 20, cy + 170], radius=10, fill=C_BG, outline=C_BORDER, width=1)
        draw.text((rx0 + 36, cy + 14), c["title"], fill=c["accent"], font=fonts["th"])
        draw.text((rx0 + 36, cy + 40), c["text"], fill=C_TEXT_LIGHT, font=fonts["body"])
        cy += 190

    img.save(out_path, "PNG")
    print(f"[OK] Generated Diagram 2: {out_path}")
    return out_path


# ==============================================================================
# DIAGRAM 3: THREE-STATE INVARIANT SECURITY ARCHITECTURE & DEFECT MATRIX
# ==============================================================================
def generate_diagram_3():
    out_path = ASSETS_DIR / "diagram_3_enygma_vulnerability_matrix.png"
    img = Image.new("RGBA", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    fonts = get_fonts()

    paste_white_logo(img)
    draw_header(
        draw,
        fonts,
        "SECURITY ARCHITECTURE | THREE-STATE INVARIANT MATRIX",
        "Three-State Invariant Security Architecture & Defect Matrix",
        "Counterfactual Vulnerability Analysis & Controlled Invariant Verification (CRIT-ZK1 to ZK7)",
    )

    top_y0, top_y1 = 175, 440
    w_card = 460
    gap = 32
    start_x = 76

    states = [
        {
            "state": "STATE 1: HAPPY PATH",
            "accent": C_GREEN,
            "badge": "Passes Verification",
            "desc": "Valid witness generation, active tree roots, unique unspent nullifiers, dynamic tree progression (0 -> 1), and valid BN254 elliptic curve pairing identities.",
            "tests": ["test_HappyPath_DvPInitiator_ValidSettlement", "test_HappyPath_ValidGroth16PairingIdentity", "test_HappyPath_DynamicTreeNumberProgression"],
        },
        {
            "state": "STATE 2: REJECTED PATH",
            "accent": C_RED,
            "badge": "Controlled Invariant Reversion",
            "desc": "Tampered tree numbers (CRIT-ZK1), value bound scalar overflow (CRIT-ZK2), nullifier double-spend replays (CRIT-ZK3), statement length mismatch (CRIT-ZK4), and field overflow (CRIT-ZK5).",
            "tests": ["CRIT-ZK1: InvalidTreeNumber()", "CRIT-ZK2: ValueBoundExceeded()", "CRIT-ZK3: NullifierAlreadySpent()"],
        },
        {
            "state": "STATE 3: EDGE / FUZZ PATH",
            "accent": C_PURPLE,
            "badge": "Boundary Robustness",
            "desc": "Unconstrained zero CounterVault bypass guard (CRIT-ZK6), cross-swap commitment mismatch (CRIT-ZK7), and 256 property-based fuzz runs with arbitrary malformed scalar inputs.",
            "tests": ["CRIT-ZK6: ZeroCounterVaultRejected()", "CRIT-ZK7: MessageCommitmentMismatch()", "testFuzz_ArbitraryMalformedValues (256 runs)"],
        },
    ]

    for i, s in enumerate(states):
        cx0 = start_x + i * (w_card + gap)
        cx1 = cx0 + w_card
        draw.rounded_rectangle([cx0, top_y0, cx1, top_y1], radius=12, fill=C_CARD, outline=C_BORDER, width=2)

        draw.rounded_rectangle([cx0, top_y0, cx1, top_y0 + 52], radius=12, fill=C_CARD_HEADER)
        draw.text((cx0 + 18, top_y0 + 16), s["state"], fill=s["accent"], font=fonts["th"])

        bw = int(fonts["pill"].getlength(s["badge"])) + 16
        draw.rounded_rectangle([cx1 - bw - 14, top_y0 + 12, cx1 - 14, top_y0 + 38], radius=6, fill=C_BG, outline=s["accent"], width=1)
        draw.text((cx1 - bw - 6, top_y0 + 19), s["badge"], fill=s["accent"], font=fonts["pill"])

        draw.line([cx0, top_y0 + 52, cx1, top_y0 + 52], fill=C_BORDER, width=1)

        inner_w = w_card - 36
        desc_lines = wrap_text_pixels(s["desc"], fonts["body"], inner_w)
        dy = top_y0 + 64
        for dline in desc_lines:
            draw.text((cx0 + 18, dy), dline, fill=C_TEXT_LIGHT, font=fonts["body"])
            dy += 21

        ty = top_y0 + 154
        draw.text((cx0 + 18, ty), "Verified Invariants:", fill=C_TEXT_MUTED, font=fonts["pill"])
        ty += 22
        for t in s["tests"]:
            draw.text((cx0 + 22, ty), f"* {t}", fill=C_WHITE, font=fonts["mono"])
            ty += 22

    bot_y0, bot_y1 = 465, 850
    draw.rounded_rectangle([76, bot_y0, W - 76, bot_y1], radius=12, fill=C_CARD, outline=C_BORDER, width=2)
    draw.rounded_rectangle([76, bot_y0, W - 76, bot_y0 + 46], radius=12, fill=C_CARD_HEADER)
    draw.text((100, bot_y0 + 13), "Enygma Upstream Vulnerability Classifications & Testbench Verifications", fill=C_WHITE, font=fonts["card_hdr"])
    draw.line([76, bot_y0 + 46, W - 76, bot_y0 + 46], fill=C_BORDER, width=1)

    cols = [
        ("Ref ID", 110),
        ("Vulnerability Class & Mechanism", 400),
        ("Upstream Code Remediation", 460),
        ("Foundry Invariant Test", 320),
        ("Result", 120),
    ]

    th_y = bot_y0 + 56
    tx = 100
    for title, width in cols:
        draw.text((tx, th_y), title, fill=C_YELLOW, font=fonts["th"])
        tx += width
    draw.line([90, th_y + 24, W - 90, th_y + 24], fill=C_BORDER, width=1)

    table_rows = [
        ("CRIT-ZK1", "Cross-Tree Nullifier Replay (HIGH-1)", "api.AssertIsEqual(stTreeNumber, activeTree)", "TamperedTreeNumberReverts", "PASS", C_GREEN),
        ("CRIT-ZK2", "Field Overflow Wrapping (H-2)", "valuebound.Assert(api, v, 10^36)", "FieldOverflowValueReverts", "PASS", C_GREEN),
        ("CRIT-ZK3", "Double-Spend Replay Attack", "spentNullifiers[nullifier] = true mapping", "NullifierDoubleSpendReverts", "PASS", C_GREEN),
        ("CRIT-ZK4", "Statement Length Mismatch Attack", "require(publicWitness.length == IC.length - 1)", "StatementLengthMismatchReverts", "PASS", C_GREEN),
        ("CRIT-ZK5", "BN254 Scalar Field Overflow (>= r)", "Sanity check on public inputs against curve r", "ScalarFieldOverflowReverts", "PASS", C_GREEN),
        ("CRIT-ZK6", "Unconstrained CounterVault Bypass", "api.AssertIsDifferent(StCounterVault, 0)", "ZeroCounterVaultGuardReverts", "PASS", C_GREEN),
        ("CRIT-ZK7", "Unbound Cross-Swap Payload (HIGH-5)", "api.AssertIsEqual(StMessage, StCommitA)", "UnconstrainedStMessageReverts", "PASS", C_GREEN),
    ]

    row_y = th_y + 34
    for ref, vuln, fix, test_name, status, stat_color in table_rows:
        draw.text((100, row_y), ref, fill=C_PURPLE, font=fonts["mono_bold"])
        draw.text((210, row_y), vuln, fill=C_WHITE, font=fonts["td_bold"])
        draw.text((610, row_y), fix, fill=C_TEXT_LIGHT, font=fonts["mono"])
        draw.text((1070, row_y), test_name, fill=C_TEXT_MUTED, font=fonts["mono"])
        draw.text((1390, row_y), status, fill=stat_color, font=fonts["td_bold"])
        draw.line([90, row_y + 26, W - 90, row_y + 26], fill=C_BORDER, width=1)
        row_y += 33

    img.save(out_path, "PNG")
    print(f"[OK] Generated Diagram 3: {out_path}")
    return out_path


# ==============================================================================
# DIAGRAM 4: PHYSICAL CPU PROVER BENCHMARKS VS MAINNET 72957 FORK GAS
# ==============================================================================
def generate_diagram_4():
    out_path = ASSETS_DIR / "diagram_4_physical_benchmarks_and_gas.png"
    img = Image.new("RGBA", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    fonts = get_fonts()

    paste_white_logo(img)
    draw_header(
        draw,
        fonts,
        "EMPIRICAL BENCHMARKS | CPU TIMINGS VS MAINNET FORK GAS",
        "Physical Groth16 Prover Latency vs. Mainnet 72957 Fork Gas",
        "Measured on Consumer Hardware (i3-3110M @ 2.40 GHz, N=50) and Live Rayls Fork Execution",
    )

    y0, y1 = 175, 855
    col_w = 690

    # ----------------------------- LEFT CONTAINER -----------------------------
    lx0, lx1 = 76, 76 + col_w
    draw.rounded_rectangle([lx0, y0, lx1, y1], radius=12, fill=C_CARD, outline=C_BORDER, width=2)
    draw.rounded_rectangle([lx0, y0, lx1, y0 + 64], radius=12, fill=C_CARD_HEADER)
    draw.text((lx0 + 24, y0 + 14), "Physical Prover Timings (N = 50 Runs)", fill=C_WHITE, font=fonts["card_hdr"])
    draw.text((lx0 + 24, y0 + 38), "Host: Intel Core i3-3110M @ 2.40 GHz (2C/4T, 7.6GB RAM, No GPU)", fill=C_YELLOW, font=fonts["pill"])
    draw.line([lx0, y0 + 64, lx1, y0 + 64], fill=C_BORDER, width=1)

    l_cols = [
        ("Circuit", 190),
        ("Median", 100),
        ("P95", 100),
        ("Solve", 90),
        ("PK Size", 100),
        ("RAM", 80),
    ]
    th_y = y0 + 78
    tx = lx0 + 20
    for title, width in l_cols:
        draw.text((tx, th_y), title, fill=C_YELLOW, font=fonts["th"])
        tx += width
    draw.line([lx0 + 16, th_y + 24, lx1 - 16, th_y + 24], fill=C_BORDER, width=1)

    prover_data = [
        ("PrivateMint (802 C)", "115.52 ms", "217.31 ms", "3.15 ms", "145 KB", "4.36 MB", C_BLUE),
        ("DvPDestination (3.7k C)", "404.55 ms", "583.16 ms", "13.89 ms", "640 KB", "11.56 MB", C_PURPLE),
        ("DvPInitiator (4.0k C)", "415.35 ms", "717.33 ms", "13.37 ms", "679 KB", "11.45 MB", C_GREEN),
    ]

    row_y = th_y + 34
    for name, med, p95, solve, pk, ram, col in prover_data:
        draw.text((lx0 + 20, row_y), name, fill=C_WHITE, font=fonts["td_bold"])
        draw.text((lx0 + 210, row_y), med, fill=col, font=fonts["mono_bold"])
        draw.text((lx0 + 310, row_y), p95, fill=C_WHITE, font=fonts["mono"])
        draw.text((lx0 + 410, row_y), solve, fill=C_TEXT_MUTED, font=fonts["mono"])
        draw.text((lx0 + 500, row_y), pk, fill=C_TEXT_LIGHT, font=fonts["mono"])
        draw.text((lx0 + 600, row_y), ram, fill=C_TEXT_MUTED, font=fonts["mono"])
        draw.line([lx0 + 16, row_y + 30, lx1 - 16, row_y + 30], fill=C_BORDER, width=1)
        row_y += 44

    b1_y0, b1_y1 = 435, 630
    draw.rounded_rectangle([lx0 + 20, b1_y0, lx1 - 20, b1_y1], radius=10, fill=C_BG, outline=C_GREEN, width=1)
    draw.text((lx0 + 36, b1_y0 + 14), "RTGS SUB-SECOND SLA VERDICT: VERIFIED PASS", fill=C_GREEN, font=fonts["th"])
    sla_desc = (
        "- Institutional SLA Requirement: <= 1,000 ms proving latency.\n"
        "- Worst-Case Observed P95: 717.33 ms on DvP Initiator (4,077 constraints).\n"
        "- Safety Margin: +282.67 ms headroom (28.3% margin) on dual-core CPU.\n"
        "- Deterministic Proving: Zero GC pauses or cryptographic timeouts.\n"
        "- CPMI-IOSCO Principle 8: Enables continuous real-time gross settlement."
    )
    draw.text((lx0 + 36, b1_y0 + 40), sla_desc, fill=C_TEXT_LIGHT, font=fonts["body"])

    b2_y0, b2_y1 = 645, 835
    draw.rounded_rectangle([lx0 + 20, b2_y0, lx1 - 20, b2_y1], radius=10, fill=C_BG, outline=C_BLUE, width=1)
    draw.text((lx0 + 36, b2_y0 + 14), "CLIENT HARDWARE FOOTPRINT & EDGE NODE VIABILITY", fill=C_BLUE, font=fonts["th"])
    heap_desc = (
        "- Ultra-Low Memory Budget: Peak client heap allocation of only 11.56 MB.\n"
        "- Proving Key Footprint: 145 KB (Mint) to 679 KB (DvP) cached in RAM.\n"
        "- Client Gateway Ready: Feasible on mobile banking apps and WebAssembly.\n"
        "- Zero Specialized Hardware: No datacenter GPUs, FPGAs, or ASICs needed.\n"
        "- High Concurrency: 16 GB bank gateway can support 1,000+ prover threads."
    )
    draw.text((lx0 + 36, b2_y0 + 40), heap_desc, fill=C_TEXT_LIGHT, font=fonts["body"])

    # ----------------------------- RIGHT CONTAINER ----------------------------
    rx0, rx1 = W - 76 - col_w, W - 76
    draw.rounded_rectangle([rx0, y0, rx1, y1], radius=12, fill=C_CARD, outline=C_BORDER, width=2)
    draw.rounded_rectangle([rx0, y0, rx1, y0 + 64], radius=12, fill=C_CARD_HEADER)
    draw.text((rx0 + 24, y0 + 14), "On-Chain EVM Fork Measured Gas (Rayls 72957)", fill=C_WHITE, font=fonts["card_hdr"])
    draw.text((rx0 + 24, y0 + 38), "Fork: https://mainnet-rpc.rayls.com (Chain 72957, Gas Price: 57.60 Gwei)", fill=C_PURPLE, font=fonts["pill"])
    draw.line([rx0, y0 + 64, rx1, y0 + 64], fill=C_BORDER, width=1)

    p_box_y = y0 + 74
    draw.rounded_rectangle([rx0 + 20, p_box_y, rx1 - 20, p_box_y + 68], radius=8, fill=C_BG, outline=C_BORDER, width=1)
    draw.text((rx0 + 32, p_box_y + 10), "RAW EIP-196 / EIP-197 PRECOMPILE BASELINE (RAYLS MAINNET)", fill=C_YELLOW, font=fonts["pill"])
    p_text1 = "0x06 ecAdd: 279 gas (G1 Addition)   |   0x07 ecMul: 6,129 gas (G1 Scalar Mul)"
    p_text2 = "0x08 ecPairing: 181,138 gas (4-Pairing BN254 Cryptographic Identity Check)"
    draw.text((rx0 + 32, p_box_y + 28), p_text1, fill=C_WHITE, font=fonts["mono_bold"])
    draw.text((rx0 + 32, p_box_y + 46), p_text2, fill=C_PURPLE, font=fonts["mono_bold"])

    r_cols = [
        ("Circuit", 180),
        ("Precompile", 110),
        ("Wrapper", 100),
        ("Total Gas", 120),
        ("RLS Cost", 140),
    ]
    rth_y = p_box_y + 78
    rtx = rx0 + 20
    for title, width in r_cols:
        draw.text((rtx, rth_y), title, fill=C_YELLOW, font=fonts["th"])
        rtx += width
    draw.line([rx0 + 16, rth_y + 24, rx1 - 16, rth_y + 24], fill=C_BORDER, width=1)

    gas_data = [
        ("PrivateMint (4 in)", "205,450", "+13,749", "219,199 gas", "0.01262 RLS", C_BLUE),
        ("DvPDestination (6 in)", "217,750", "+16,718", "234,468 gas", "0.01350 RLS", C_PURPLE),
        ("DvPInitiator (8 in)", "230,050", "+19,689", "249,739 gas", "0.01438 RLS", C_GREEN),
    ]

    r_row_y = rth_y + 34
    for name, p_base, wrap, total_g, cost, col in gas_data:
        draw.text((rx0 + 20, r_row_y), name, fill=C_WHITE, font=fonts["td_bold"])
        draw.text((rx0 + 200, r_row_y), p_base, fill=C_TEXT_MUTED, font=fonts["mono"])
        draw.text((rx0 + 310, r_row_y), wrap, fill=C_YELLOW, font=fonts["mono"])
        draw.text((rx0 + 410, r_row_y), total_g, fill=col, font=fonts["mono_bold"])
        draw.text((rx0 + 530, r_row_y), cost, fill=C_WHITE, font=fonts["mono_bold"])
        draw.line([rx0 + 16, r_row_y + 30, rx1 - 16, r_row_y + 30], fill=C_BORDER, width=1)
        r_row_y += 44

    rb1_y0, rb1_y1 = 520, 675
    draw.rounded_rectangle([rx0 + 20, rb1_y0, rx1 - 20, rb1_y1], radius=10, fill=C_BG, outline=C_PURPLE, width=1)
    draw.text((rx0 + 36, rb1_y0 + 14), "EMPIRICAL FINDING: EVM WRAPPER OVERHEAD DYNAMICS", fill=C_PURPLE, font=fonts["th"])
    wrap_desc = (
        "- Staticcall Memory Dispatch: +13,749 to +19,689 gas above pure precompiles.\n"
        "- Root Cause: 768-byte pairing array packing and staticcall opcode overhead.\n"
        "- Linear Statement Scaling: ~2,461 - 3,437 gas per public statement element.\n"
        "- Precompile Dominance: Raw pairing checks account for 72.5% - 82.6% of gas."
    )
    draw.text((rx0 + 36, rb1_y0 + 40), wrap_desc, fill=C_TEXT_LIGHT, font=fonts["body"])

    rb2_y0, rb2_y1 = 690, 835
    draw.rounded_rectangle([rx0 + 20, rb2_y0, rx1 - 20, rb2_y1], radius=10, fill=C_BG, outline=C_YELLOW, width=1)
    draw.text((rx0 + 36, rb2_y0 + 14), "MACROECONOMIC COMPARISON: RAYLS VS. ETHEREUM L1", fill=C_YELLOW, font=fonts["th"])
    econ_desc = (
        "- Rayls Mainnet 72957 Cost: 0.01438 RLS (~$0.0001) per confidential DvP.\n"
        "- Ethereum L1 Cost: 250k gas @ 25 Gwei ($2,500 ETH) costs ~$15.60 per proof.\n"
        "- Institutional Cost Reduction: >99.99% lower transaction friction.\n"
        "- High-Volume Scalability: Enables 100,000+ daily bilateral banking settlements."
    )
    draw.text((rx0 + 36, rb2_y0 + 40), econ_desc, fill=C_TEXT_LIGHT, font=fonts["body"])

    img.save(out_path, "PNG")
    print(f"[OK] Generated Diagram 4: {out_path}")
    return out_path


# ==============================================================================
# DIAGRAM 5: POSEIDON HASH PERMUTATION ARCHITECTURE & MERKLE TREE VERIFICATION
# ==============================================================================
def generate_diagram_5():
    out_path = ASSETS_DIR / "diagram_5_poseidon_hash_permutation_matrix.png"
    img = Image.new("RGBA", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    fonts = get_fonts()

    paste_white_logo(img)
    draw_header(
        draw,
        fonts,
        "ALGEBRAIC HASH DESIGN | HADES SPONGE & MERKLE ACCUMULATOR",
        "Poseidon Hash Permutation Architecture & Merkle Tree Verification",
        "Mathematical Breakdown of Hades Sponge (t=3, t=5) in BN254 and 8-Level Tree Accumulation",
    )

    y0, y1 = 175, 850
    col_w = 690

    lx0, lx1 = 76, 76 + col_w
    draw.rounded_rectangle([lx0, y0, lx1, y1], radius=12, fill=C_CARD, outline=C_BORDER, width=2)
    draw.rounded_rectangle([lx0, y0, lx1, y0 + 64], radius=12, fill=C_CARD_HEADER)
    draw.text((lx0 + 24, y0 + 14), "Hades Sponge Permutation Strategy (BN254 Field)", fill=C_WHITE, font=fonts["card_hdr"])
    draw.text((lx0 + 24, y0 + 38), "State: t=3 (2-in, 1-out) and t=5 (4-in, 1-out)  |  S-box: x^5", fill=C_PURPLE, font=fonts["pill"])
    draw.line([lx0, y0 + 64, lx1, y0 + 64], fill=C_BORDER, width=1)

    steps = [
        ("1. Sponge Initialization & State Injection", "State vector S = [capacity=0, input_1, input_2] in F_q (254-bit prime field).", C_BLUE),
        ("2. First Full Rounds (R_F / 2 = 4 rounds)", "All t state elements undergo round constant addition (C_i), full S-box x^5 (3 constraints/elem), and MDS matrix multiplication M.", C_PURPLE),
        ("3. Partial Rounds (R_P = 56 rounds)", "CRITICAL OPTIMIZATION: Only S[0] undergoes S-box x^5. Elements S[1]..S[t-1] pass linearly. Saves 88% of nonlinear R1CS constraints.", C_YELLOW),
        ("4. Last Full Rounds (R_F / 2 = 4 rounds)", "Restores complete cryptographic diffusion across all t elements with full S-boxes and MDS mixing against algebraic attacks.", C_GREEN),
        ("5. Squeeze & Digest Output", "Hash output S[0] truncated to BN254 scalar field order. Collisions cryptographically infeasible.", C_TEXT_LIGHT),
    ]

    sy = y0 + 80
    for title, desc, color in steps:
        draw.text((lx0 + 24, sy), title, fill=color, font=fonts["th"])
        dlines = wrap_text_pixels(desc, fonts["body"], col_w - 48)
        sdy = sy + 22
        for line in dlines:
            draw.text((lx0 + 24, sdy), line, fill=C_TEXT_LIGHT, font=fonts["body"])
            sdy += 20
        sy = sdy + 14

    b_y = y1 - 130
    draw.rounded_rectangle([lx0 + 20, b_y, lx1 - 20, y1 - 20], radius=10, fill=C_BG, outline=C_PURPLE, width=1)
    draw.text((lx0 + 36, b_y + 14), "SECURITY PRINCIPLE: GROTH16 FRIENDLINESS", fill=C_PURPLE, font=fonts["th"])
    p_sec = (
        "Poseidon's low-degree power map (x^5) requires only 3 R1CS multiplication gates\n"
        "per S-box (x^2 = x*x, x^4 = x^2*x^2, x^5 = x^4*x). In contrast, bitwise hashes (SHA-256)\n"
        "require decomposing 32-bit words into binary bits, exploding constraint counts."
    )
    draw.text((lx0 + 36, b_y + 38), p_sec, fill=C_TEXT_LIGHT, font=fonts["body"])

    rx0, rx1 = W - 76 - col_w, W - 76
    draw.rounded_rectangle([rx0, y0, rx1, y1], radius=12, fill=C_CARD, outline=C_BORDER, width=2)
    draw.rounded_rectangle([rx0, y0, rx1, y0 + 64], radius=12, fill=C_CARD_HEADER)
    draw.text((rx0 + 24, y0 + 14), "8-Level Merkle Tree Path Verification & Benchmarks", fill=C_WHITE, font=fonts["card_hdr"])
    draw.text((rx0 + 24, y0 + 38), "Depth: d=8  |  Capacity: 256 Notes per Tree  |  In-Circuit Path Accumulation", fill=C_YELLOW, font=fonts["pill"])
    draw.line([rx0, y0 + 64, rx1, y0 + 64], fill=C_BORDER, width=1)

    th_y = y0 + 78
    r_cols = [("Cryptographic Hash", 200), ("R1CS Cost", 120), ("Relative Cost", 130), ("ZK Viability", 180)]
    rtx = rx0 + 20
    for title, width in r_cols:
        draw.text((rtx, th_y), title, fill=C_YELLOW, font=fonts["th"])
        rtx += width
    draw.line([rx0 + 16, th_y + 24, rx1 - 16, th_y + 24], fill=C_BORDER, width=1)

    hashes = [
        ("Poseidon (BN254, t=3)", "~240 R1CS", "1.0x (Baseline)", "OPTIMAL (Sub-Second)", C_GREEN),
        ("Rescue-Prime (BN254)", "~480 R1CS", "2.0x Slower", "VIABLE (Enterprise)", C_BLUE),
        ("MiMC-7 (BN254)", "~640 R1CS", "2.7x Slower", "LEGACY (High Latency)", C_PURPLE),
        ("SHA-256 (NIST FIPS 180)", "~25,000 R1CS", "104x Slower", "PROHIBITIVE (Minutes)", C_RED),
        ("Keccak-256 (Ethereum)", "~150,000 R1CS", "625x Slower", "UNUSABLE IN GROTH16", C_RED),
    ]

    r_row_y = th_y + 34
    for hname, r1cs, rel, viab, col in hashes:
        draw.text((rx0 + 20, r_row_y), hname, fill=C_WHITE, font=fonts["td_bold"])
        draw.text((rx0 + 220, r_row_y), r1cs, fill=col, font=fonts["mono_bold"])
        draw.text((rx0 + 340, r_row_y), rel, fill=C_TEXT_LIGHT, font=fonts["mono"])
        draw.text((rx0 + 470, r_row_y), viab, fill=col, font=fonts["td_bold"])
        draw.line([rx0 + 16, r_row_y + 28, rx1 - 16, r_row_y + 28], fill=C_BORDER, width=1)
        r_row_y += 40

    m_card_y = r_row_y + 14
    draw.rounded_rectangle([rx0 + 20, m_card_y, rx1 - 20, y1 - 20], radius=10, fill=C_BG, outline=C_GREEN, width=1)
    draw.text((rx0 + 36, m_card_y + 14), "MERKLE TREE VERIFICATION IN DVPINITIATOR CIRCUIT", fill=C_GREEN, font=fonts["th"])
    m_desc = (
        "- Membership Verification: Evaluates 8 consecutive Poseidon(2-in) hashes.\n"
        "- Path Constraint Weight: 8 x 240 = 1,920 R1CS constraints.\n"
        "- Budget Allocation: 47.1% of entire DvP Initiator circuit (4,077 R1CS).\n"
        "- Dynamic Tree Progression (HIGH-1): In-circuit StTreeNumber verification\n"
        "  prevents attackers from proving note membership against historical trees.\n"
        "- State Commitment: Merkle root stored on-chain; nullifier revoked upon spend."
    )
    draw.text((rx0 + 36, m_card_y + 40), m_desc, fill=C_TEXT_LIGHT, font=fonts["body"])

    img.save(out_path, "PNG")
    print(f"[OK] Generated Diagram 5: {out_path}")
    return out_path


# ==============================================================================
# DIAGRAM 6: CONFIDENTIAL DVP SETTLEMENT SEQUENCE & ATOMIC CROSS-SUBNET PROTOCOL
# ==============================================================================
def generate_diagram_6():
    """Redesigned to eliminate empty vertical space with rich substeps and bottom state artifact cards."""
    out_path = ASSETS_DIR / "diagram_6_confidential_dvp_atomic_settlement.png"
    img = Image.new("RGBA", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    fonts = get_fonts()

    paste_white_logo(img)
    draw_header(
        draw,
        fonts,
        "INTEROPERABILITY ARCHITECTURE | ATOMIC DELIVERY-VS-PAYMENT",
        "Confidential DvP Settlement Sequence & Atomic Cross-Subnet Protocol",
        "6-Step Atomic Lifecycle Between Bank A (Asset Subnet) and Bank B (Cash Subnet / Drex) via Public L1",
    )

    y0, y1 = 175, 715
    col_w = 460
    col_gap = 32
    start_x = 76

    columns = [
        {
            "actor": "BANK A (ASSET SUBNET)",
            "sub": "Sovereign Private EVM Subnet",
            "accent": C_PURPLE,
            "steps": [
                ("1. Bilateral Agreement & Key Exchange", "Off-chain ECDH / ML-KEM exchange to establish shared blinding factor."),
                ("2. Asset Note Escrow & State Lock", "Asset note locked into local Enygma vault; generates StCommitA and Nullifier."),
                ("3. Client Groth16 Prover Execution", "Satisfies 4,077 constraints on DvPInitiator circuit (415ms median on CPU)."),
                ("4. Gateway Calldata Packaging", "Extracts 128B proof and 8 public statement signals for public chain relay."),
            ],
            "card_title": "LOCAL ASSET SUBNET ARTIFACTS",
            "card_color": C_PURPLE,
            "card_items": [
                "- Succinct Proof: 128B [A in G1, B in G2, C in G1]",
                "- Public Statement: 8 signals (256B calldata)",
                "- Prover Timings: 415ms prove | 13.37ms solve",
                "- Memory Footprint: 11.45 MB peak heap budget",
                "- Strict Privacy: Note values & keys never leave Bank A",
            ],
        },
        {
            "actor": "RAYLS PUBLIC CHAIN 72957",
            "sub": "Decentralized Settlement Layer",
            "accent": C_YELLOW,
            "steps": [
                ("5. EVM Precompile Verification", "Staticcalls to 0x06 ecAdd, 0x07 ecMul, and 0x08 ecPairing (181,138 gas)."),
                ("6. Invariant & Nullifier Enforcement", "Checks activeTreeNumber (HIGH-1) and revokes nullifier against replays."),
                ("7. Atomic Commitment Registration", "Registers StCommitA and StCommitB in ZKVerifierTestbench storage."),
                ("8. Settlement Receipt Emission", "Emits SettlementExecuted event for cross-subnet decentralized relayers."),
            ],
            "card_title": "PUBLIC L1 VERIFICATION METRICS",
            "card_color": C_YELLOW,
            "card_items": [
                "- Total Verification Gas: 249,739 gas on Chain 72957",
                "- Precompile Baseline: 230,050 gas (ecPairing x4)",
                "- EVM Wrapper Overhead: +19,689 gas (memory/dispatch)",
                "- Settlement Fee: 0.01438 RLS @ 57.60 Gwei baseline",
                "- L1 Cadence: Mean 1.34s interval (500M gas headroom)",
            ],
        },
        {
            "actor": "BANK B (CASH / DREX SUBNET)",
            "sub": "Central Bank Drex CBDC Subnet",
            "accent": C_GREEN,
            "steps": [
                ("9. Relayer Attestation & Receipt Ingestion", "Submits L1 cryptographic receipt and verified commitments to Bank B."),
                ("10. Cross-Commitment Binding Check", "Verifies StMessage == StCommitA (HIGH-5) ensuring payload consistency."),
                ("11. Tokenized Cash Note Release", "Unlocks tokenized Drex cash note from escrow to Bank A recipient."),
                ("12. Simultaneous Gross Finalization", "Both legs settle atomically with zero credit or principal risk."),
            ],
            "card_title": "CENTRAL BANK DREX GUARANTEES",
            "card_color": C_GREEN,
            "card_items": [
                "- Herstatt Elimination: 100% atomic DvP execution",
                "- Regulatory Mandate: CPMI-IOSCO Principle 8 & 12",
                "- Atomic Timeout: Auto-reverts on proof expiry",
                "- Subnet Interoperability: Direct Drex CBDC bridging",
                "- Zero Balance Leakage: Bank B validates proof only",
            ],
        },
    ]

    for i, col in enumerate(columns):
        cx0 = start_x + i * (col_w + col_gap)
        cx1 = cx0 + col_w
        draw.rounded_rectangle([cx0, y0, cx1, y1], radius=12, fill=C_CARD, outline=C_BORDER, width=2)

        # Header
        draw.rounded_rectangle([cx0, y0, cx1, y0 + 64], radius=12, fill=C_CARD_HEADER)
        draw.text((cx0 + 20, y0 + 14), col["actor"], fill=col["accent"], font=fonts["card_hdr"])
        draw.text((cx0 + 20, y0 + 38), col["sub"], fill=C_TEXT_MUTED, font=fonts["pill"])
        draw.line([cx0, y0 + 64, cx1, y0 + 64], fill=C_BORDER, width=1)

        # 4 Steps (y: 245 to 480)
        sy = y0 + 78
        for title, desc in col["steps"]:
            draw.text((cx0 + 18, sy), title, fill=col["accent"], font=fonts["th"])
            dlines = wrap_text_pixels(desc, fonts["body"], col_w - 36)
            sdy = sy + 20
            for line in dlines:
                draw.text((cx0 + 18, sdy), line, fill=C_TEXT_LIGHT, font=fonts["body"])
                sdy += 18
            sy = sdy + 8

        # Bottom Technical Card (y: 495 to 700) FILLS ALL EMPTY SPACE
        card_by0, card_by1 = 495, 700
        draw.rounded_rectangle([cx0 + 16, card_by0, cx1 - 16, card_by1], radius=10, fill=C_BG, outline=col["card_color"], width=1)
        draw.text((cx0 + 28, card_by0 + 12), col["card_title"], fill=col["card_color"], font=fonts["th"])
        ci_y = card_by0 + 34
        for item in col["card_items"]:
            draw.text((cx0 + 28, ci_y), item, fill=C_TEXT_LIGHT, font=fonts["mono"])
            ci_y += 30

        # Connecting Arrow
        if i < 2:
            arr_x = cx1 + 10
            arr_y = (y0 + y1) // 2
            draw.polygon([(arr_x, arr_y - 12), (arr_x + 12, arr_y), (arr_x, arr_y + 12)], fill=C_YELLOW)

    # Bottom Banner: Herstatt Risk Elimination
    by0, by1 = 735, 855
    draw.rounded_rectangle([76, by0, W - 76, by1], radius=12, fill=C_CARD, outline=C_GREEN, width=1)
    draw.text((100, by0 + 16), "HERSTATT SETTLEMENT RISK ELIMINATION (CPMI-IOSCO PRINCIPLE 12)", fill=C_GREEN, font=fonts["th"])
    h_text = (
        "By binding asset and cash commitments cryptographically to the Rayls Public Settlement Layer, the protocol eliminates cross-currency\n"
        "settlement lag (Herstatt Risk). If either party fails to supply a valid proof within the settlement window, commitments expire atomically."
    )
    draw.text((100, by0 + 42), h_text, fill=C_TEXT_LIGHT, font=fonts["body"])

    img.save(out_path, "PNG")
    print(f"[OK] Generated Diagram 6: {out_path}")
    return out_path


# ==============================================================================
# DIAGRAM 7: RAYLS MAINNET 72957 EMPIRICAL TELEMETRY & CADENCE DISTRIBUTION
# ==============================================================================
def generate_diagram_7():
    """Mathematically verified cadence distribution strictly matching data/mainnet_72957_telemetry.json."""
    out_path = ASSETS_DIR / "diagram_7_mainnet_telemetry_cadence_distribution.png"
    img = Image.new("RGBA", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    fonts = get_fonts()

    paste_white_logo(img)
    draw_header(
        draw,
        fonts,
        "MAINNET FORENSICS | 1,000-BLOCK CONTINUOUS TELEMETRY SCAN",
        "Rayls Mainnet 72957 Empirical Telemetry & Cadence Distribution",
        "Continuous 1,000-Block Forensic Scan (#15,047,066 to #15,048,065) with 999/999 Verified Parent Links",
    )

    top_y0, top_y1 = 175, 265
    c_w = 340
    c_gap = 26
    start_x = 76

    top_stats = [
        ("BLOCK SCAN DEPTH", "1,000 Blocks", "999/999 Parent Links (100%)", C_GREEN),
        ("MEAN CADENCE", "1.3423 sec", "Median: 1.0s | P95: 2.0s", C_YELLOW),
        ("BASELINE GAS PRICE", "57.60 Gwei", "Fixed Fee Engine (Predictable)", C_PURPLE),
        ("BLOCK GAS LIMIT", "500,000,000", "Computational Execution Ceiling", C_BLUE),
    ]

    for i, (title, num, sub, col) in enumerate(top_stats):
        cx0 = start_x + i * (c_w + c_gap)
        cx1 = cx0 + c_w
        draw.rounded_rectangle([cx0, top_y0, cx1, top_y1], radius=10, fill=C_CARD, outline=C_BORDER, width=1)
        draw.text((cx0 + 16, top_y0 + 12), title, fill=C_TEXT_MUTED, font=fonts["pill"])
        draw.text((cx0 + 16, top_y0 + 30), num, fill=col, font=fonts["stat_num"])
        draw.text((cx0 + 16, top_y0 + 64), sub, fill=C_TEXT_LIGHT, font=fonts["pill"])

    bot_y0, bot_y1 = 285, 850
    col_w = 690

    # Left Container: Cadence Distribution (Exact Mathematical Reconciliation: Mean 1.3423s, Range [0s..2s])
    lx0, lx1 = 76, 76 + col_w
    draw.rounded_rectangle([lx0, bot_y0, lx1, bot_y1], radius=12, fill=C_CARD, outline=C_BORDER, width=2)
    draw.rounded_rectangle([lx0, bot_y0, lx1, bot_y0 + 56], radius=12, fill=C_CARD_HEADER)
    draw.text((lx0 + 24, bot_y0 + 16), "Block Interval Cadence Histogram (N = 999 Intervals)", fill=C_WHITE, font=fonts["card_hdr"])
    draw.line([lx0, bot_y0 + 56, lx1, bot_y0 + 56], fill=C_BORDER, width=1)

    intervals = [
        ("0-Second Interval (Sub-Sec)", 10, "1.0%", C_BLUE),
        ("1-Second Interval (Normal)", 637, "63.8%", C_GREEN),
        ("2-Second Interval (Max Gap)", 352, "35.2%", C_YELLOW),
    ]

    iy = bot_y0 + 80
    for label, count, pct, col in intervals:
        draw.text((lx0 + 24, iy), label, fill=C_WHITE, font=fonts["td_bold"])
        draw.text((lx0 + 260, iy), f"{count} intervals", fill=C_TEXT_MUTED, font=fonts["td"])
        draw.text((lx1 - 100, iy), pct, fill=col, font=fonts["mono_bold"])

        bar_y = iy + 24
        bar_w = int((count / 999) * (col_w - 48))
        draw.rounded_rectangle([lx0 + 24, bar_y, lx1 - 24, bar_y + 16], radius=4, fill=C_BG)
        draw.rounded_rectangle([lx0 + 24, bar_y, lx0 + 24 + bar_w, bar_y + 16], radius=4, fill=col)
        iy += 72

    c_y = iy + 14
    draw.rounded_rectangle([lx0 + 20, c_y, lx1 - 20, bot_y1 - 20], radius=10, fill=C_BG, outline=C_GREEN, width=1)
    draw.text((lx0 + 36, c_y + 14), "BLOCK PRODUCTION STABILITY & REORGANIZATION INVARIANTS", fill=C_GREEN, font=fonts["th"])
    stab_desc = (
        "- Unbroken Cryptographic Hash Chain: Verified 999 consecutive parent links\n"
        "  (block[i].parentHash == block[i-1].hash) with zero missing blocks or forks.\n"
        "- Sub-2-Second Determinism: 100% of all sampled blocks produced within <= 2s.\n"
        "- Strict Interval Bounding: Min interval = 0s, Median = 1.0s, Max = 2.0s.\n"
        "- Weighted Mean Cadence: (0x10 + 1x637 + 2x352) / 999 = 1.3423 seconds.\n"
        "- Single-Node Endpoint Caveat: Confirms local RPC consensus consistency at sample time."
    )
    draw.text((lx0 + 36, c_y + 40), stab_desc, fill=C_TEXT_LIGHT, font=fonts["body"])

    # Right Container: Genesis System Contracts
    rx0, rx1 = W - 76 - col_w, W - 76
    draw.rounded_rectangle([rx0, bot_y0, rx1, bot_y1], radius=12, fill=C_CARD, outline=C_BORDER, width=2)
    draw.rounded_rectangle([rx0, bot_y0, rx1, bot_y0 + 56], radius=12, fill=C_CARD_HEADER)
    draw.text((rx0 + 24, bot_y0 + 16), "Canonical Genesis System Contracts Bytecode Audit", fill=C_WHITE, font=fonts["card_hdr"])
    draw.line([rx0, bot_y0 + 56, rx1, bot_y0 + 56], fill=C_BORDER, width=1)

    gth_y = bot_y0 + 74
    g_cols = [("Contract Name", 200), ("Address", 190), ("Bytecode Size", 130), ("Verified", 110)]
    gtx = rx0 + 20
    for title, width in g_cols:
        draw.text((gtx, gth_y), title, fill=C_YELLOW, font=fonts["th"])
        gtx += width
    draw.line([rx0 + 16, gth_y + 24, rx1 - 16, gth_y + 24], fill=C_BORDER, width=1)

    contracts = [
        ("ConsensusRegistry", "0x07E1...17e1", "21,929 Bytes", "CANONICAL", C_GREEN),
        ("FeeAggregatorProxy", "0x07E1...17E3", "122 Bytes", "CANONICAL", C_PURPLE),
        ("DelegationPool", "0x07e1...17e9", "15,790 Bytes", "CANONICAL", C_BLUE),
    ]

    gy = gth_y + 34
    for cname, addr, bsize, ver, col in contracts:
        draw.text((rx0 + 20, gy), cname, fill=C_WHITE, font=fonts["td_bold"])
        draw.text((rx0 + 220, gy), addr, fill=C_TEXT_MUTED, font=fonts["mono"])
        draw.text((rx0 + 410, gy), bsize, fill=col, font=fonts["mono_bold"])
        draw.text((rx0 + 540, gy), ver, fill=C_GREEN, font=fonts["td_bold"])
        draw.line([rx0 + 16, gy + 28, rx1 - 16, gy + 28], fill=C_BORDER, width=1)
        gy += 44

    rg_y = gy + 14
    draw.rounded_rectangle([rx0 + 20, rg_y, rx1 - 20, bot_y1 - 20], radius=10, fill=C_BG, outline=C_PURPLE, width=1)
    draw.text((rx0 + 36, rg_y + 14), "NETWORK TOPOLOGY & EPISTEMIC BOUNDARY SEPARATION", fill=C_PURPLE, font=fonts["th"])
    top_desc = (
        "- Public Chain ID 72957: Decentralized public settlement layer operating with\n"
        "  500M gas ceiling, hosting consensus, fee aggregation, and verification registries.\n"
        "- Sovereign Subnet Isolation: Enterprise bank transactions occur off the public chain\n"
        "  in private subnets; only zero-knowledge proofs and commitments settle to L1.\n"
        "- Zero Confidentiality Leaks: No balances, note owners, or values are exposed on L1."
    )
    draw.text((rx0 + 36, rg_y + 40), top_desc, fill=C_TEXT_LIGHT, font=fonts["body"])

    img.save(out_path, "PNG")
    print(f"[OK] Generated Diagram 7: {out_path}")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Generate Week 9 Research Diagrams")
    parser.add_argument("--diagram", choices=["1", "2", "3", "4", "5", "6", "7", "all"], default="all", help="Diagram to generate")
    args = parser.parse_args()

    generators = {
        "1": generate_diagram_1,
        "2": generate_diagram_2,
        "3": generate_diagram_3,
        "4": generate_diagram_4,
        "5": generate_diagram_5,
        "6": generate_diagram_6,
        "7": generate_diagram_7,
    }

    if args.diagram == "all":
        for num, gen in generators.items():
            gen()
    else:
        generators[args.diagram]()


if __name__ == "__main__":
    main()
