---
name: Bug
about: Not intended for users! 
title: Summary
labels: bug
assignees: iBrotNano
---

## :bug: Bug

### :spiral_notepad: Description

A description of the faulty behavior.

### :question: Open Questions?

- [ ] @Who: What must be discussed?

### :construction: Blockers

- [ ] Something blocks my work.

#### :footprints: How to reproduce

1. Step 1
1. Step 2

### :inbox_tray: Input

What data goes into the system and what is their source?

### :outbox_tray: Output

What data goes out of the system and why?

### :control_knobs: Conditions

- [ ] Environment: OS, runtime, versions (App, Python/.NET, Browser)
- [ ] Configuration / Feature flags: Which toggles are on?
- [ ] Data preconditions: dataset/state/size
- [ ] User context: role/permissions, locale/timezone
- [ ] System state: cache warm/cold, background jobs/services
- [ ] Load & timing: concurrent users, req/s, latency
- [ ] Network: VPN/Proxy, offline/poor connectivity
- [ ] External services: API availability, rate limits
- [ ] Hardware: CPU/RAM constraints
- [ ] Reproducibility: always/sometimes; time window

### :warning: Side effects

Are there any?

### Acceptance Tests

- [ ] Given <context>, when <action>, then <expected outcome>.

### Prepare the development

- [ ] Create a `bugfix`  or `hotfix` branch

### Docs

Links to documentation pages related to the bug.

### :package: Deployment

- [ ] Merge `bugfix` into `main` or `hotfix` into `production` and `main` and remove the `bugfix` branch via PR
- [ ] Check if the compiled artifact is valid
- [ ] Cleanup the Git history locally on the dev system

### :beer: Retro

> [!TIP]  Was gab es zu lernen?
> What did I learn?

> [!WARNING] Where were the problems?
> Where did I have difficulties? What hindered my work?