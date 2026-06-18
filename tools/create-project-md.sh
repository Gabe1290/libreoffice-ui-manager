#!/usr/bin/env bash
set -euo pipefail

cat > PROJECT.md <<'EOF'
# LibreOffice UI Manager — PROJECT

## Mission

LOUIM is an educational LibreOffice extension designed to progressively simplify the LibreOffice Writer interface.

It helps teachers reduce cognitive overload by showing only the tools needed for the current learning step.

LOUIM is not primarily a lockdown tool. It is a learning tool.

## Current Milestone

Milestone 0.3 — First working extension.

Goal:

- Installable `.oxt`
- Entry in LibreOffice Writer
- Simple "Hello LOUIM" dialog

No menu hiding yet.

## Current Problem

The `.oxt` package builds, but the Python entry point does not yet execute reliably.

Likely causes:

- Python script registration inside the extension
- Incorrect macro path
- Difference between LibreOffice Python macros and Python UNO extensions
- Use of `XSCRIPTCONTEXT` in the wrong execution context

## Current Decision

Before continuing with full extension packaging, first create a working LibreOffice Python macro.

Development order:

1. Make a minimal Python macro work.
2. Show a "Hello LOUIM" dialog.
3. Package the working code into an `.oxt`.
4. Add the Tools menu entry.
5. Continue with Discovery Engine.

## Next Session Tasks

1. Create a minimal Python macro outside the extension.
2. Test it in LibreOffice Writer.
3. Confirm Python/UNO execution works.
4. Create a developer script to install test macros quickly.
5. Return to `.oxt` packaging after the macro works.

## Resume Prompt

Continue LOUIM from PROJECT.md
EOF

echo "Created PROJECT.md"
