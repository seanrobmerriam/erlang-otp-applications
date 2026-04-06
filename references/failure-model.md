# OTP Failure Model Reference

## Goal

Use OTP to recover from runtime faults by isolating failure, crashing fast on invalid state, and letting supervision policy restore the system.

## Let It Crash, Precisely

"Let it crash" does not mean "ignore errors." It means:

- handle expected operational outcomes explicitly
- crash on violated invariants, corrupted state, impossible inputs, and programmer bugs
- let supervisors, not leaf workers, decide restart policy

Examples of expected outcomes:

- upstream timeout
- resource not found
- temporary network refusal
- validation failure from external input

Examples that should usually crash the process:

- state shape no longer matches module assumptions
- impossible message variants reaching a callback
- partial initialization leaving the process inconsistent
- logic bugs that would keep the process running with bad state

## Error vs Crash

Return tagged errors when the caller can reasonably act on them.
Crash when continuing would preserve bad assumptions.

A useful rule:

- If the process is still healthy and the condition is part of the contract, return `{error, Reason}`.
- If the process is no longer trustworthy, stop it.

## Restart Modes

Pick child restart modes intentionally:

- `permanent`: always restart. Good default for critical long-lived services.
- `transient`: restart only on abnormal exit. Good when normal completion is allowed.
- `temporary`: never restart. Good for fire-and-forget or request-scoped workers.

Do not mark everything `permanent` by habit. Temporary jobs that finish normally should not be resurrected.

## Restart Intensity

Supervisor intensity limits prevent infinite crash loops.

If a child crashes repeatedly:

- fix deterministic bugs instead of relying on restart churn
- consider whether the child belongs in a narrower failure domain
- verify initialization dependencies and startup ordering

Frequent restarts are a signal that the supervision design or process contract is wrong.

## Shutdown Semantics

Every child needs an intentional shutdown mode.

- Use a numeric timeout when the process must flush state or close resources.
- Use `brutal_kill` only when cleanup is either impossible or not worth waiting for.
- Keep termination work short and deterministic.

Do not put long business workflows in `terminate/2`. Treat shutdown hooks as cleanup, not normal processing.

## Calls, Casts, and Backpressure

Choose message styles with failure behavior in mind:

- `gen_server:call/2,3`: use when the caller needs a result or failure signal.
- `gen_server:cast/2`: use only when losing immediate feedback is acceptable.
- raw messages: use sparingly and document the protocol clearly.

Avoid turning everything into `cast/2` just to dodge timeouts. Timeouts often indicate that the boundary or workload is wrong.

## State Recovery

Design workers so a restart is safe:

- rebuild state from an external source when possible
- keep initialization idempotent
- avoid hidden side effects during `init/1`
- prefer explicit ownership of files, sockets, ETS tables, or timers

If a worker cannot restart cleanly, the design is brittle. Move more state outward or make reconstruction explicit.

## Observability

Log enough context to understand repeated crashes, but do not wrap every callback in generic catch-all code just to log exceptions. OTP crash reports already provide useful signals. Add structured context at domain boundaries where it improves diagnosis.

## Common Failure Anti-Patterns

- catching every exception and returning `{reply, {error, Reason}, State}`
- retry loops inside a worker with no supervision visibility
- restarting a process that performs non-idempotent external side effects without safeguards
- using `one_for_all` for convenience rather than true shared fate
- masking startup dependency problems instead of fixing tree structure
