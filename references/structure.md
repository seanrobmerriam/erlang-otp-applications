# OTP Structure Reference

## Goal

Build applications as supervision trees of small processes with explicit ownership and recovery boundaries.

## Recommended Layout

For a rebar3 OTP application, start with:

```text
my_app/
├── rebar.config
├── src/
│   ├── my_app.app.src
│   ├── my_app_app.erl
│   ├── my_app_sup.erl
│   ├── my_app_worker.erl
│   └── my_app_domain.erl
└── test/
```

Use module roles deliberately:

- `my_app_app`: implement the `application` behaviour; start the root supervisor and little else.
- `my_app_sup`: implement the root supervisor; define the stable root of the tree.
- `*_sup`: create additional supervisors when a subsystem needs its own restart boundary.
- `*_server` or `*_worker`: implement long-lived processes, usually with `gen_server`.
- `*_domain`, `*_logic`, `*_codec`: keep pure logic outside OTP callback modules.

## Typical Tree

```text
my_app_app
└── my_app_sup (one_for_one)
    ├── registry/process group
    ├── cache_sup
    │   ├── cache_loader
    │   └── cache_server
    └── request_sup
        └── request_router
```

Use the tree to express operational relationships, not package names.

## Supervisor Guidelines

Use supervisors to model failure domains.

Choose strategies by dependency:

- `one_for_one`: restart only the failed child. Default choice.
- `rest_for_one`: restart the failed child and all younger siblings. Use when startup order matters.
- `one_for_all`: restart all children if one fails. Use only when children form one inseparable unit.
- `simple_one_for_one`: legacy pattern; prefer modern dynamic supervisor approaches where available in your OTP version.

Keep top-level supervisors stable. If a subsystem has its own lifecycle or restart rules, give it a dedicated child supervisor.

## gen_server Guidelines

Use `gen_server` when all of the following are true:

- state must live in one process
- callers need serialized access to that state
- the process has a meaningful lifecycle

A `gen_server` should usually own one thing:

- one socket or connection pool coordinator
- one cache state machine
- one queue consumer coordinator
- one durable in-memory state holder

A `gen_server` should not become a generic service object. If callback clauses keep multiplying across unrelated domains, split the process.

## Callback Shape

Prefer this boundary:

- OTP callback: decode message, validate call shape, delegate to domain module, translate result into OTP return tuple.
- Domain module: perform real logic.

Example:

```erlang
handle_call({put, Key, Value}, _From, State) ->
    case my_app_store:put(Key, Value, State) of
        {ok, NewState, Reply} ->
            {reply, Reply, NewState};
        {stop, Reason} ->
            {stop, Reason, State}
    end.
```

The point is not abstraction for its own sake. The point is keeping state transition logic testable without driving the whole process.

## Naming and Registration

Register processes only when callers need stable discovery.

Prefer:

- local registered names for singletons inside one node
- `via` tuples for pluggable registries
- supervisor child ids that match the role of the child

Avoid global registration unless distributed uniqueness is a real requirement.

## Dynamic Children

When workers are created at runtime:

- place them under a dedicated supervisor
- define the shutdown and restart policy explicitly
- decide whether the parent should monitor the child or only interact through the supervisor

Do not let arbitrary processes spawn unmanaged workers. If a process matters, supervise it.

## Common Anti-Patterns

- top-level supervisor with dozens of unrelated children
- business workflows encoded directly in `init/1`, `handle_call/3`, or `handle_info/2`
- mixing resource ownership, orchestration, and domain rules in one module
- workers depending on sibling startup order without `rest_for_one` or a better boundary
