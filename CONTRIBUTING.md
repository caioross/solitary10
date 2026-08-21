# Contributing

The bar here is a mathematical one before it is a software one. A patch that makes the
code faster but weakens what can be certified will be rejected; a patch that makes the
code slower but removes a hidden assumption will not.

## Setup

```bash
python -m venv venv
venv/Scripts/activate          # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
pytest -q
```

The suite must be green before every commit. It runs in well under a minute; if a test
starts taking minutes, that is a bug in the test, not a fact about the problem.

## Non-negotiables

- **No floating point** in anything that supports a mathematical claim. Use `int`,
  `fractions.Fraction` or `sympy.Rational`. Floats are for printing only.
- **Every statement gets a label.** See `docs/METHODOLOGY.md` for the vocabulary. A
  conditional label must list *all* of its inputs, library routines included.
- **Independent verification means independent.** A test that checks a function against
  the same library call the function itself makes proves nothing; both sides fail the
  same way. Where a result depends on a library routine, add a cross-check that
  reimplements it from scratch.
- **A search that cannot certify its own coverage must say so.** Refusing to certify is
  a correct outcome; silently truncating a sweep is not. Any cap, sample or top-N must
  be logged.
- **Abandoned attacks are documented.** If a line of attack fails, add an entry to
  `results/FRACASSOS.md` with the precise reason, before moving on.

## Review

A new result is not labelled as proved until an adversarial pass has been run against
it: reviewers are asked to break the proof, not to approve it. Findings, including the
ones that turned out to be false alarms, are recorded in the phase report.

Two classes of bug are treated as critical, because both can silently certify something
false: a pruning rule that discards a live branch, and a comparison that excludes the
boundary case (`<` where `≤` is meant). Any change to the search engine must be
accompanied by planted-target tests — a fabricated solution injected into the search
space, which the code is required to find.

## Style

Match the surrounding code. Exact arithmetic in helpers, docstrings stating what is
proved and under what hypotheses, and command-line scripts that document themselves via
`--help`.
