"""Deprecated fail-closed shim.

The old home-only policy removed required consumer disclosures from monetized pages.
Final public disclosure policy now lives in config/public_content_policy.json and is
applied by guard_built_customer_copy.py after Vite builds the production bundle.
"""

raise SystemExit(
    "Deprecated COSHUMA disclosure cleaner invoked. Refusing to modify dist/: "
    "use config/public_content_policy.json + guard_built_customer_copy.py instead."
)
