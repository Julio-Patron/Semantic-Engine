#!/usr/bin/env python3
"""
Automate Stripe Product + Payment Link creation with configurable pricing and
inject live checkout URLs & prices across all repository marketing surfaces:
  - docs/site/index.html
  - README.md
  - README_en.md
  - core_rs/README.md
  - .github/FUNDING.yml

Reads STRIPE_SECRET_KEY (and optional GUMROAD_TIER1_URL / GUMROAD_TIER2_URL)
from environment variables OR directly from the local gitignored `.env` file.
"""

import argparse
import base64
import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
STRIPE_API_BASE = "https://api.stripe.com/v1"


def _load_local_dotenv() -> dict:
    """Read key=value pairs from local .env without printing secrets."""
    env_file = ROOT / ".env"
    values = {}
    if not env_file.is_file():
        return values
    for raw_line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        values[k.strip()] = v.strip().strip('"').strip("'")
    return values


def _stripe_post(endpoint: str, secret_key: str, form_data: dict) -> dict:
    encoded = urlencode(form_data).encode("utf-8")
    token = base64.b64encode(f"{secret_key}:".encode("utf-8")).decode("ascii")
    req = Request(
        f"{STRIPE_API_BASE}/{endpoint.lstrip('/')}",
        data=encoded,
        headers={
            "Authorization": f"Basic {token}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def create_stripe_payment_link(
    secret_key: str,
    name: str,
    description: str,
    amount_cents: int,
    confirmation_message: str,
) -> str:
    product = _stripe_post(
        "/products",
        secret_key,
        {
            "name": name,
            "description": description,
        },
    )
    price = _stripe_post(
        "/prices",
        secret_key,
        {
            "product": product["id"],
            "unit_amount": str(amount_cents),
            "currency": "usd",
        },
    )
    link = _stripe_post(
        "/payment_links",
        secret_key,
        {
            "line_items[0][price]": price["id"],
            "line_items[0][quantity]": "1",
            "after_completion[type]": "hosted_confirmation",
            "after_completion[hosted_confirmation][custom_message]": confirmation_message,
            "invoice_creation[enabled]": "true",
        },
    )
    return link["url"]


def inject_checkout_and_prices(
    price_tier1: int,
    price_tier2: int,
    stripe_tier1: str,
    stripe_tier2: str,
    gumroad_tier1: str,
    gumroad_tier2: str,
) -> None:
    targets = [
        ROOT / "docs" / "site" / "index.html",
        ROOT / "README.md",
        ROOT / "README_en.md",
        ROOT / "core_rs" / "README.md",
    ]
    for path in targets:
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        content = content.replace("$149", f"${price_tier1}")
        content = content.replace("$249", f"${price_tier2}")
        content = content.replace("$299", f"${price_tier2}")
        if stripe_tier1:
            content = content.replace(
                "https://elbuilder77.github.io/Semantic-Engine/?checkout=stripe_tier1#pricing",
                stripe_tier1,
            )
        if stripe_tier2:
            content = content.replace(
                "https://elbuilder77.github.io/Semantic-Engine/?checkout=stripe_tier2#pricing",
                stripe_tier2,
            )
        if gumroad_tier1:
            content = content.replace(
                "https://elbuilder77.github.io/Semantic-Engine/?checkout=gumroad_tier1#pricing",
                gumroad_tier1,
            )
        if gumroad_tier2:
            content = content.replace(
                "https://elbuilder77.github.io/Semantic-Engine/?checkout=gumroad_tier2#pricing",
                gumroad_tier2,
            )
        path.write_text(content, encoding="utf-8")


def main() -> int:
    dotenv_vals = _load_local_dotenv()
    parser = argparse.ArgumentParser(
        description="Provision Stripe Payment Links and inject prices & checkout URLs."
    )
    parser.add_argument(
        "--price-tier1",
        type=int,
        default=149,
        help="USD price for Tier 1 (Commercial License)",
    )
    parser.add_argument(
        "--price-tier2",
        type=int,
        default=299,
        help="USD price for Tier 2 (White-Label Boilerplate)",
    )
    parser.add_argument("--stripe-tier1", default="", help="Existing Stripe Payment Link for Tier 1")
    parser.add_argument("--stripe-tier2", default="", help="Existing Stripe Payment Link for Tier 2")
    parser.add_argument(
        "--gumroad-tier1",
        default=os.getenv("GUMROAD_TIER1_URL", dotenv_vals.get("GUMROAD_TIER1_URL", "")),
        help="Gumroad product URL for Tier 1",
    )
    parser.add_argument(
        "--gumroad-tier2",
        default=os.getenv("GUMROAD_TIER2_URL", dotenv_vals.get("GUMROAD_TIER2_URL", "")),
        help="Gumroad product URL for Tier 2",
    )
    args = parser.parse_args()

    stripe_key = os.getenv("STRIPE_SECRET_KEY", dotenv_vals.get("STRIPE_SECRET_KEY", "")).strip()
    stripe_t1 = args.stripe_tier1
    stripe_t2 = args.stripe_tier2

    if stripe_key and (not stripe_t1 or not stripe_t2):
        print(
            f"Creating products and Payment Links in Stripe (${args.price_tier1} and ${args.price_tier2} USD)..."
        )
        stripe_t1 = stripe_t1 or create_stripe_payment_link(
            secret_key=stripe_key,
            name="SES Core — Commercial Dual-License Exemption (Tier 1)",
            description="Perpetual GPLv3 exemption for 1 organization. Provided As-Is without support.",
            amount_cents=args.price_tier1 * 100,
            confirmation_message=(
                "Thank you! Your Stripe invoice/receipt is your legally binding Commercial License "
                "under COMMERCIAL_LICENSE.md (Tier 1)."
            ),
        )
        stripe_t2 = stripe_t2 or create_stripe_payment_link(
            secret_key=stripe_key,
            name="SES Enterprise — White-Label Boilerplate & Agency License (Tier 2)",
            description="Unlimited client White-Label rights + Enterprise Gateway, Next.js Portal & PDF Audit Kit (As-Is).",
            amount_cents=args.price_tier2 * 100,
            confirmation_message=(
                "Thank you! Your Stripe receipt grants Tier 2 Multi-Client White-Label Rights "
                "under COMMERCIAL_LICENSE.md."
            ),
        )
        print(f"  ✓ Stripe Tier 1 (${args.price_tier1}): {stripe_t1}")
        print(f"  ✓ Stripe Tier 2 (${args.price_tier2}): {stripe_t2}")

    inject_checkout_and_prices(
        args.price_tier1,
        args.price_tier2,
        stripe_t1,
        stripe_t2,
        args.gumroad_tier1,
        args.gumroad_tier2,
    )
    print(
        f"Updated pricing (${args.price_tier1} / ${args.price_tier2} USD) and checkout links across docs/site/index.html and READMEs."
    )

    build_script = ROOT / "scripts" / "build_commercial_assets.py"
    if build_script.exists():
        subprocess.run([sys.executable, str(build_script)], check=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
