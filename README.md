# Erlang OTP Applications

A Codex skill for designing, reviewing, and bootstrapping Erlang/OTP applications.

## What It Covers

- OTP application structure
- Supervision trees and child specs
- `application`, `supervisor`, and `gen_server` roles
- Let-it-crash failure handling
- Restart and shutdown semantics
- A starter rebar3 OTP application template

## Files

- `SKILL.md`: skill trigger and operating instructions
- `references/structure.md`: OTP layout and process boundaries
- `references/failure-model.md`: crash/restart guidance and anti-patterns
- `scripts/scaffold_rebar3_otp_app.py`: copies the starter template with a renamed app
- `assets/rebar3-otp-template/`: starter OTP application scaffold

## When To Use This Skill

Use this skill when working on Erlang services that should follow OTP conventions:

- creating a new OTP application
- reviewing an existing supervision tree
- deciding whether logic belongs in a `gen_server` or a plain module
- defining restart strategies and child restart modes
- debugging systems that should fail fast and recover through supervision

## Scaffold a New App

```bash
python3 scripts/scaffold_rebar3_otp_app.py my_app /tmp/my_app
```

This creates a copy of the bundled rebar3 template and rewrites `myapp` placeholders in file names and contents.

## Starter Template Contents

The template includes:

- `rebar.config`
- `src/<app>.app.src`
- `src/<app>_app.erl`
- `src/<app>_sup.erl`
- `src/<app>_worker.erl`

## Design Principles

- start only the root supervisor from the `application` callback
- keep supervisors responsible for lifecycle, not business logic
- use `gen_server` for long-lived stateful processes with a clear ownership boundary
- keep pure domain logic outside OTP callback modules
- crash on invalid state and let supervisors manage recovery

## Notes

The skill is structured to keep `SKILL.md` concise and move detailed OTP guidance into `references/`.
