# COSHUMA Operations Control Plane

`data/operations_registry.json` is the machine-readable lifecycle authority for active COSHUMA work.

GitHub issues #763 and #292 remain evidence/audit channels. They do not independently override the registry after a state has been synchronized.

Rules:
- one active record per task/target;
- one DRI and one next owner;
- merge/build success is not completion;
- production work stays open until production verification evidence exists;
- user gates are limited to CAPTCHA, OTP, legal consent, payment, or forced identity verification;
- recurring incidents reuse the same incident key;
- teams consume assigned queue entries instead of creating duplicate work.

Run:

```bash
python scripts/validate_operations_registry.py
python scripts/next_operations_task.py
```

Every PR touching the registry must pass the validator before any source-mutating build preparation.
