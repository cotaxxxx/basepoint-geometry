# Item 7 accepted-template v2 recovery status

Status: **ORIGINAL BYTES NOT RECOVERED; NO RUN AUTHORIZED**

## Accepted external anchor

The accepted item 7 author-statement template v2 is identified externally by:

- SHA-256 prefix: `574eb98d...`
- structural marker: sections or fields `A0` through `A7`

Those accepted bytes are the only bytes entitled to be registered as the
accepted `AUTHOR_STATEMENT_TEMPLATE_v2` candidate.

## Recovery result

The accepted bytes were not found in the accessible conversation uploads,
File Library search, current execution storage, or repository search.  This
record does not infer, reconstruct, or replace the missing original.

## New-authorship separation

Commit `6a8d975f0bcacc2fc431994beebd609fc7a3b35f` introduced a separately authored
SPEC_PENDING, non-executable document.  It is not byte-identical to the
accepted candidate, does not have the accepted A0--A7 structure, and must not
be cited as recovery or registration of the accepted v2.

That document is retained under the distinct path:

`CERTIFICATES/prolate/item7_latitude/AUTHOR_STATEMENT_TEMPLATE_draft-new-authorship.tex`

The former path `AUTHOR_STATEMENT_TEMPLATE_v2.tex` is removed from the branch
head to prevent provenance confusion.  The historical commit remains intact.

## Future recovery rule

If the accepted file is later recovered, it must be checked against the full
SHA-256 beginning `574eb98d...` and its A0--A7 structure before registration.
Until then, item 7 accepted-template v2 registration remains incomplete.

No computation, workflow, tag, certificate, mathematical conclusion, or
author sign-off is authorized by this record.
