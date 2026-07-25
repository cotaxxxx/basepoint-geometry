# Run the item 6 audits

```bash
python -m pip install sympy==1.14.0 mpmath==1.3.0
cd CERTIFICATES/prolate/item6_axis
python prolate_axis_symbolic_audit.py
python prolate_axis_reference.py --dps 50
```

Expected status:

- symbolic audit: `PASSED`
- reference scout: `NON_CERTIFIED_REFERENCE`
- all sampled `psi` values: positive

The second result is not an Arb certificate.
