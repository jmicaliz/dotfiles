---
name: adr
description: Draft an Architecture Decision Record in the house format (problem statement, goal, a recommended solution and a fairly-argued rejected alternative, ownership, accepted-limitation appendix, and glossary), written as a numbered markdown file in the repository it decides for (default `docs/adrs/`) and reviewed in a PR. Use whenever the user asks for an ADR, design doc, decision doc, tech spec, RFC, or solution comparison, or asks to write up / document a technical decision with the alternatives considered.
---

# ADR

Draft an ADR in the house format. ADRs live in the repository whose code they decide for, next to that code, and are reviewed in a PR like any other change. `TEMPLATE.md` next to this file is the canonical template. **Read `TEMPLATE.md` and fill it in; don't reconstruct the structure from memory**, and don't drop or reorder sections just because a particular ADR has little to say in one of them. Write "N/A: [why]" instead.

The format's whole value is that a reader outside the two teams involved can evaluate the decision without a meeting. That only works if the doc is concrete. A vague ADR in this template is worse than no ADR, because it looks rigorous.

## Steps

1. **Read the code before writing anything.** The sections that carry the argument (Background, Cons, Glossary) depend on details you cannot invent: the actual function and file names, the current gate or hack and why it's there, every entry point that creates the thing in question, and the scale numbers (how many nodes, edges, calls per day, repos affected). Search the repos in scope and gather these first. If a repo isn't available locally, say so and ask rather than writing a plausible-sounding placeholder.

2. **Ask only for what the code can't tell you.** Typically: attendees, which questions need answering in the meeting, who owns what, any in-flight refactor that affects sequencing, and whether a second solution was seriously considered or needs inventing. Batch these into one round of questions; don't drip-feed. If the user has already said something in conversation, use it instead of asking again.

3. **Find the directory and the number.** Use the repo's existing ADR directory if it has one (`docs/adrs/`, `docs/adr/`, `adr/`, or wherever numbered ADR files already live); otherwise create `docs/adrs/`. The number is one past the highest `NNNN-` prefix ever used there, zero-padded to four digits (`0001` for the first). Collect used prefixes from three places: the files in the directory, every file ever added there (`git log --all --diff-filter=A --name-only --format= -- <adr-dir>`, which catches deleted ADRs), and the files open PRs add there (`gh pr list --state open --limit 1000 --json files --jq '.[].files[].path'`, since PR titles lead with the ticket ID, not the ADR number). Never reuse a number, even from a deleted or superseded ADR.

4. **Draft it.** Copy `TEMPLATE.md` to `<adr-dir>/NNNN-kebab-title.md`, keeping the heading as `ADR-NNNN - Title`. Replace every `[bracketed]` placeholder and delete the italic guidance lines under each heading; those are notes to the author, not content. The bracketed prose and diagrams are one illustrative example from a service-integration decision; match their shape and depth, not their vocabulary or diagram topology. Diagrams go in ```` ```mermaid ```` fences, which GitHub renders natively, with a plain `Figure: ...` caption line above. Keep the template's heading levels and caption style; with the guidance lines gone, the file passes markdownlint's default rules.

5. **Check it against the quality bar** below before handing it over.

6. **Leave it for review as a PR.** Set `Status: DRAFT`, tell the user the file path, and stop there; committing and opening the PR follow the repo's normal flow. The PR is the review. Once the meeting questions are answered, record the answers in the file and set `Status: DECIDED` in the last commit before merge. When a later ADR replaces this one, the same PR that adds the new ADR sets this one's status to `SUPERSEDED BY [ADR-NNNN](NNNN-title.md)`; the superseded file stays in place.

## Quality bar

- **Cons must be self-incriminating.** Name the coverage gap, the structural debt, the runtime cost, and the burden placed on another team. If the Cons list reads like it was written by someone selling the solution, it's wrong. These are accepted trade-offs, stated plainly, not risks to be managed away.
- **The rejected solution gets real treatment**: its own diagram and its own genuine Pros before the Cons. A strawman fools no one and destroys trust in the recommendation. Close it with a **Bottom line** that states the single deciding argument in two or three sentences.
- **State the anti-goal.** The Problem Statement should say what you are explicitly *not* building and why the existing system is worth reusing instead. This is what stops the reader proposing a rewrite in the comments.
- **The Goal is one sentence** naming the decision, where it becomes reusable, what it reuses, and the safe default when there's no answer. If it needs two sentences, the scope is unclear.
- **Every system and domain term gets a Glossary entry**, with the numbers that convey scale.
- **Prefer real identifiers to prose.** `` `completeTaskAndCreateNew` `` and `` `file.ts` `` beat "the completion flow."
- **Fill the meeting questions in live.** The answers are the record of the decision; that's what makes the doc an ADR rather than a proposal.

## Fitting the format to the decision

Two solutions is the default shape, not a rule. Three is fine; mark one `[Recommended]` and the rest `[Not chosen]`. If there is genuinely only one viable approach, keep the section and say why the obvious alternative was never in play; don't manufacture a fake option to fill the slot.

The Appendix exists for the one trade-off ugly enough to need its own section: a circular dependency, a framework-version boundary, a migration that has to land first. Give the current invariant, what the proposal breaks, a diagram, and a Plan B with its real caveats. If nothing in the ADR is that ugly, drop the Appendix rather than padding it.

For a small, reversible decision this format is too heavy. Say so and offer a short version (problem, decision, consequences) instead of walking the user through fifteen sections they don't need.
