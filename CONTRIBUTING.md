# Contributing to This Repository

## Governance Authority

This repository is governed by the **Stella Maris Constitution (CONST-01)** and the policies defined in the [SMG Enterprise HQ](https://github.com/stella-maris-governance/smg-enterprise-hq).

## Two-Person Integrity Protocol

All changes to governance controls require a **Pull Request (PR)**. No PR shall be merged without the independent audit seal of the **Authorized Official (AO)**, satisfying the SMG Two-Person Integrity Rule.

| Role | Responsibility |
|------|---------------|
| **Principal (Robert Myers)** | Prepares controls, commits evidence, opens PR |
| **Auditor (CoS)** | Reviews PR against policy, validates evidence chain |
| **AO (Regina Myers)** | Authorizes merge — the seal that activates the control |

A control without the AO seal is a draft. A merged control without evidence is a finding.

## Commit Standards

- Use [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `evidence:`, `cleanup:`, `uplift:`
- Reference pack and control IDs in commit messages
- No secrets, credentials, or CUI in any commit

## Evidence Standards

- Primary evidence: deterministic engine outputs (script results)
- Secondary evidence: Azure portal screenshots (added when running against live environment)
- All evidence must be reproducible — same input, same script, same output

---

**© 2026 Stella Maris Governance LLC** — The work speaks for itself.
