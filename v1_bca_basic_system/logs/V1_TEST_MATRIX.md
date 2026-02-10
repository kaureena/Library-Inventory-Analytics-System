# v1 Test Matrix (Manual + Unit)

| Test ID | Area | Input | Expected | Status |
|---|---|---|---|---|
| V1-T01 | Issue | Issue book when stock=0 | Reject issue | Covered (rule + DQ in v2) |
| V1-T02 | Dates | due_date <= issue_date | Reject | Unit test |
| V1-T03 | Fine | return_date <= due_date | Fine = 0 | Unit test |
| V1-T04 | Export | Generate CSV exports | Files created | Demo step |
