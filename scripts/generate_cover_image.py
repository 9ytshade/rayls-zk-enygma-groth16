#!/usr/bin/env python3
"""Generate Cover Image for Week 9 using the Full-Bleed Rayls Signature Gradient (#B49AFF -> #ECFB3E)."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "cover_image_groth16_enygma.png"
OUT.parent.mkdir(parents=True, exist_ok=True)
LOGO_PATH = ROOT.parent / "Brand_Guide" / "Rayls_Logo_Pack" / "PNG" / "Rayls_Logo_Black.png"

W, H = 1600, 900

C_PURPLE = (180, 154, 255, 255)   # #B49AFF
C_YELLOW = (236, 251, 62, 255)    # #ECFB3E
C_GREEN = (140, 247, 139, 255)    # #8CF78B
C_BLACK = (17, 17, 20, 255)       # #111114
C_CARD = (24, 24, 28, 255)        # #18181C
C_BORDER = (55, 55, 65, 255)
C_WHITE = (255, 255, 255, 255)
C_MUTED = (205, 205, 218, 255)

FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_REG = r"C:\Windows\Fonts\segoeui.ttf"
FONT_MONO = r"C:\Windows\Fonts\consola.ttf"


def make_signature_gradient(width: int, height: int, left_rgba, right_rgba) -> Image.Image:
    base = Image.new("RGBA", (width, height), left_rgba)
    top = Image.new("RGBA", (width, height), right_rgba)
    row = [int(255 * (x / (width - 1))) for x in range(width)]
    mask = Image.new("L", (width, height))
    mask.putdata(row * height)
    base.paste(top, (0, 0), mask)
    return base


def main() -> int:
    img = make_signature_gradient(W, H, C_PURPLE, C_YELLOW)
    draw = ImageDraw.Draw(img)

    if LOGO_PATH.exists():
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo_h = 46
        logo_w = int(logo_h * logo.width / logo.height)
        logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        img.paste(logo, (W - logo_w - 76, 46), logo)

    f_title = ImageFont.truetype(FONT_BOLD, 46)
    f_sub = ImageFont.truetype(FONT_REG, 21)
    f_label = ImageFont.truetype(FONT_BOLD, 15)
    f_stat = ImageFont.truetype(FONT_BOLD, 38)
    f_stat_lbl = ImageFont.truetype(FONT_REG, 15)
    f_body = ImageFont.truetype(FONT_REG, 15)
    f_badge = ImageFont.truetype(FONT_BOLD, 14)

    # Main title
    draw.text((76, 90), "Zero-Knowledge Proof Anatomy:", fill=C_BLACK, font=f_title)
    draw.text((76, 150), "Benchmarking Groth16 Proving on Rayls Enygma Circuits", fill=C_BLACK, font=f_title)
    draw.text((76, 224), "Physical Consumer CPU Proving (N=50), RTGS Sub-Second Latencies & Live Mainnet Fork Gas", fill=C_BLACK, font=f_sub)

    # 3 Metrics Cards
    card_y0, card_y1 = 310, 775
    card_w = 448
    gap = 22

    cards = [
        {
            "tag": "RAYLS MAINNET (CHAIN 72957)",
            "stat": "1.342s Mean",
            "stat_lbl": "Canonical Cadence (N = 1,000 blocks)",
            "lines": [
                "1,000 continuous blocks (#15,047,066 - #15,048,065)",
                "999/999 unbroken parent links, 0-block finalized lag",
                "500M gas ceiling; 57.60 Gwei baseline gasPrice",
                "Genesis bytecodes: ConsensusRegistry (21.9k B)",
                "Precompiles: ecAdd 279, ecMul 6,129, ecPairing 181k"
            ],
            "accent": C_YELLOW,
        },
        {
            "tag": "PHYSICAL GROTH16 PROVER",
            "stat": "415 ms Median",
            "stat_lbl": "RTGS Sub-Second SLA Verified (N=50)",
            "lines": [
                "Prover p95: 717 ms on consumer i3-3110M CPU @ 2.40 GHz",
                "Circuit constraint shrinkage: 4,077 R1CS (53.2% vs doc)",
                "Proving key size: 678,997 B; Client heap: 11.45 MB",
                "Poseidon hash costs: 47.1% of DvP circuit budget",
                "100% compliant with CPMI-IOSCO sub-second SLAs"
            ],
            "accent": C_PURPLE,
        },
        {
            "tag": "THREE-STATE INVARIANT SUITE",
            "stat": "16/16 Passed",
            "stat_lbl": "EVM Precompile Gas & Defect Matrix",
            "lines": [
                "On-chain fork gas: 249,739 gas (0.01438 RLS @ 57.60 Gwei)",
                "Solidity staticcall wrapper overhead: +13.7k to +19.7k gas",
                "Proves CRIT-ZK1 to ZK7 (tree rollback, overflow, replays)",
                "Zero CounterVault guard (CRIT-ZK6) and Message binding",
                "256 property-based fuzz runs with 0 unhandled reverts"
            ],
            "accent": C_GREEN,
        },
    ]

    for i, c in enumerate(cards):
        cx0 = 76 + i * (card_w + gap)
        cx1 = cx0 + card_w
        draw.rounded_rectangle([cx0, card_y0, cx1, card_y1], radius=18, fill=C_CARD, outline=C_BORDER, width=2)

        draw.rounded_rectangle([cx0 + 20, card_y0 + 20, cx0 + 20 + 12, card_y0 + 36], radius=3, fill=c["accent"])
        draw.text((cx0 + 40, card_y0 + 20), c["tag"], fill=C_MUTED, font=f_label)

        draw.text((cx0 + 22, card_y0 + 56), c["stat"], fill=C_WHITE, font=f_stat)
        draw.text((cx0 + 24, card_y0 + 102), c["stat_lbl"], fill=C_YELLOW, font=f_stat_lbl)

        draw.line([cx0 + 22, card_y0 + 130, cx1 - 22, card_y0 + 130], fill=C_BORDER, width=1)

        y_text = card_y0 + 148
        for line in c["lines"]:
            draw.text((cx0 + 24, y_text), f"- {line}", fill=C_MUTED, font=f_body)
            y_text += 46

    # Bottom pill
    draw.rounded_rectangle([76, 804, 370, 848], radius=10, fill=C_BLACK)
    draw.text((92, 815), "Verified Empirical Research Package", fill=C_YELLOW, font=f_badge)

    img.save(OUT, "PNG")
    print(f"Cover image saved to: {OUT}")
    return 0


if __name__ == "__main__":
    main()
