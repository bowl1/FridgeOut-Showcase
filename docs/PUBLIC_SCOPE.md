# What this public repository contains

[Back to the showcase](../README.md)

This is a curated showcase of FridgeOut, not a fork or source distribution of the complete commercial application. It has a fresh history so previous product commits, deleted files and configuration cannot be recovered from this repository's history.

| Published | Kept in the separate product repository |
| --- | --- |
| Selected product screenshots and logo | Full mobile app and native project |
| Architecture and design explanations | Production graph, prompts and complete guardrail taxonomy |
| Interview guide and limitations | Billing, entitlement and accounting implementation |
| Two rewritten educational examples and their tests | Full schema/migrations, RLS implementation and operational SQL |
| Example-only CI without secrets | Deployment hooks, environments and provider credentials |

Documentation describes mechanisms at a useful engineering level without distributing all of their implementation. Examples use invented fixture data and standard-library-only adapters. They have no access to the live product backend, real users, model APIs or payment services.

## Maintaining the boundary

Add specific files after reviewing their contents. Do not copy the entire product directory, `.git` history, `.env` files, native signing files, logs, database exports or user photos. Do not add CI deployment jobs to this repository.

Before publishing an update, inspect both the staged diff and all staged file names. Run examples and link checks. Treat screenshots as content too: check for private accounts, financial data and personal information. Public facts must remain consistent with actual release status.

The current publication uses selected product images already supplied for the product README. Screenshots and example outputs demonstrate behavior; they do not substantiate model-quality or commercial-performance claims.

## Rights

Public visibility allows people to inspect the materials and does not grant a general license to reuse or distribute the paid application. No open-source license is granted by this repository. GitHub's applicable terms govern viewing and platform functionality. See [NOTICE](../NOTICE).
