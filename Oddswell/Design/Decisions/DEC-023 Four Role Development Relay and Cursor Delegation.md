---
tags:
  - decision
  - development
  - notion
  - cursor
status: accepted
date: 2026-08-06
---

# DEC-023 Four-Role Development Relay and Cursor Delegation

## Decision

The recurring OddsWell development relay uses four named roles:

1. **Scope Director** selects the smallest truthful beta-roadmap phase and identifies whether any bounded work is appropriate for Cursor.
2. **Execution Agent** implements and verifies only the approved phase with Ponytail.
3. **Messaging Coordinator** verifies the commit, evidence, tests, local documentation, clean worktree, Notion sync, and next gate.
4. **Notion and Cursor Delegation Agent** updates verified project status in Notion and creates Cursor-ready task packets when delegation is genuinely useful.

The roles run sequentially for each phase. No next phase begins until the current phase is verified locally and synced to Notion.

## Cursor task rule

The Notion Agent may create at most one new Cursor task per verified phase, and only when the Scope Director identifies a bounded, independent, low-risk task. It searches for an existing open task before creating another.

Suitable Cursor work includes:

- documentation;
- isolated tests and developer tooling;
- catalog metadata;
- isolated UI polish;
- noncanonical prototypes;
- Blender Python, import, validation, or export automation.

Cursor does not own core networking, game authority, Odds Bucks, wagering or settlement, brain or simulator behavior, persistence migrations, security, release, deployment, or owner decisions.

## Required task packet

Every Cursor task includes project, roadmap, and report links; context; one exact objective; affected area; prerequisites; testable acceptance criteria; required checks; explicit out-of-scope boundaries; and the expected branch/pull-request handoff. New tasks begin as **To Do** and are never marked **Done** without Coordinator-verified code or pull-request evidence.

## Rationale

Notion becomes the team-facing coordination record without replacing the local Git repository and Obsidian vault as implementation truth. Cursor can accelerate small parallel work without fragmenting authority-sensitive systems or creating speculative task clutter.

## Boundaries

- A Cursor task is optional; no task is created merely to keep Cursor busy.
- An OPEN or OWNER GATE decision is never delegated as implementation.
- Notion records only verified facts and explicitly labeled blockers.
- If Notion is unavailable during the nightly relay, the local commit is preserved, the batch stops, and no sync is fabricated.
