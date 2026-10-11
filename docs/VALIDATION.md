# Validation and evidence

[Back to the showcase](../README.md)

Separate implementation evidence from product outcomes. Tests passing does not prove model correctness, production performance, user adoption or App Store approval.

## Product implementation checks

The product repository contains these checks; their full code and infrastructure are intentionally not published here.

| Area | Evidence in the product repository | Practical boundary |
| --- | --- | --- |
| API / schema / rules | Python tests for constraints, authentication propagation and error paths | Mocks and fixtures do not prove provider availability |
| Mobile cache / queues | Type checking and executable tests for image queues, caches, offline deletion and password recovery | Native device permissions and lifecycle need device tests |
| Ownership | Disposable PostgreSQL tests for RLS and cross-user operations | Local simulated auth/storage needs hosted-project acceptance |
| Images | Database lease tests for repeated claims, expiry and retry | Does not guarantee one charge in every remote timeout scenario |
| Accounting | Quota/budget tests and real concurrent PostgreSQL transactions | Estimates need reconciliation with actual provider invoices |
| Billing / deletion | SQL checks for periods, ownership, account deletion and operation isolation | Apple sandbox and provider behavior need end-to-end testing |
| Migrations | First-run and repeat migration checks with data preservation | Production backups and rollout monitoring remain necessary |

Before deployment, the private CI runs backend tests, mobile checks and disposable database checks, applies migrations, and asks Render to deploy the tested commit. A successful deploy-hook response means the deployment was accepted; Render's Live state and HTTP checks still matter.

## Public example checks

The public CI runs only the standalone examples' unit tests. It has no deployment credentials, database or model calls.

```bash
python3 -m unittest discover -s tests -v
```

Checks cover:

- Cumulative recipe usage exceeding available stock, including stock split over multiple rows.
- Unit mismatches and non-positive/invalid numeric quantities.
- Maximum cooking time, approved staple handling and empty ingredient lists.
- Deletion persistence across reopening the queue.
- A lost delete acknowledgement followed by 404.
- Transient failures retaining pending work and permanent rejection restoring visibility.
- Account isolation and account changes during synchronization.

The JSON-file deletion example is intentionally single-process and synchronous. It does not reproduce AsyncStorage write serialization or native lifecycle callbacks. The simplified constraint example does not include diet or semantic hallucination checks.

## Claims intentionally not made

There are no claimed conversion rates, subscriber counts, cost savings, latency percentiles or live-model accuracy percentages in this repository. The screenshots show the product UI. Educational fixtures show expected behavior for selected cases. Neither is a scientific quality benchmark.

## Next acceptance work

1. Complete Apple sandbox purchase, restore, plan-change and account-switch flows on device.
2. Test airplane-mode deletion, restart and reconnect on two real accounts.
3. Verify private image access and RLS on the configured hosted Supabase project.
4. Run versioned live-model evals with human-labeled difficult examples and track acceptance coverage, latency and actual costs.
5. Confirm account deletion behavior and explain independent Apple subscription cancellation in the UI.

These are recommended acceptance checks. Their completion is not implied by a public CI badge.
