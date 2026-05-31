"""Simple end‑to‑end pipeline for Project TIM (Phase 3).

The script demonstrates the *full* flow:
    1. Accept a natural‑language intent (or read from STDIN).
    2. Use the Draftsman translator to produce TIM‑IR.
    3. POST the TIM‑IR to the Governor verification endpoint.
    4. Print the verification result.

It also showcases how to seed the immutable Axiomatic Registry with a few
sample ADUs (numeric facts) before the verification step.
"""

import sys
import json
import argparse
import requests

# Local imports – assume this script runs from the project root and the
# Python path includes the project directory.
from draftsman.translator import IntentParser
from registry.db import add_adu, list_adus

GOVERNOR_URL = "http://localhost:8080/verify"

def seed_registry():
    """Insert a few deterministic ADUs for demo purposes.

    In a real deployment the registry would be populated by a separate
    governance process; here we add a couple of constants so that the
    ``lookup`` operation can be exercised.
    """
    sample_adus = {
        "MAX_TEMP": 100,
        "MIN_TEMP": 0,
        "PI": 3.1415,
    }
    for name, value in sample_adus.items():
        try:
            add_adu(name, value)
        except ValueError:
            # ADU already exists – ignore as we intend idempotent seeding
            pass

def translate_intent(intent: str):
    parser = IntentParser()
    return parser.translate(intent)

def verify_tim_ir(tim_ir: dict):
    response = requests.post(GOVERNOR_URL, json=tim_ir, timeout=5)
    response.raise_for_status()
    return response.json()

def main():
    parser = argparse.ArgumentParser(description="Project TIM end‑to‑end demo")
    parser.add_argument("intent", nargs="?", help="Natural‑language intent to translate")
    parser.add_argument("--seed", action="store_true", help="Seed the registry with demo ADUs before running")
    args = parser.parse_args()

    if args.seed:
        seed_registry()
        print("✅ Registry seeded with demo ADUs")
        print("Current ADUs:")
        for row in list_adus():
            print(f"  - {row[0]} = {row[1]}")
        print()

    if not args.intent:
        # Read intent from stdin if not provided on the command line
        intent = sys.stdin.read().strip()
    else:
        intent = args.intent

    if not intent:
        print("Error: No intent supplied", file=sys.stderr)
        sys.exit(1)

    tim_ir = translate_intent(intent)
    print("🧩 TIM‑IR generated:")
    print(json.dumps(tim_ir, indent=2))

    print("\n🔎 Sending to Governor for verification …")
    result = verify_tim_ir(tim_ir)
    print("✅ Verification result:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
