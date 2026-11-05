# Entry point for a new machine is ./bootstrap.sh; these are day-to-day chezmoi shortcuts.
# FILE narrows a target to one path, e.g. `make diff FILE=~/.zshrc`.

SHELL := /bin/bash
FILE ?=
GUARD := home/dot_local/bin/executable_dotfiles-guard

# keeper-commander warns on Python 3.15+ for every call; see dot_zshrc.tmpl.
export PYTHONWARNINGS := ignore::FutureWarning:keepercommander.utils

.DEFAULT_GOAL := help
.PHONY: help bootstrap apply dry-run diff status verify update upgrade add re-add edit managed unmanaged data doctor reset-once reset-onchange guard lint lint-fix check sync-work

help: ## Show this help
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

bootstrap: ## Pull, install chezmoi if missing, and init + apply (same as ./bootstrap.sh)
	./bootstrap.sh

apply: ## Write the source state to $HOME and run due scripts [FILE=]
	chezmoi apply $(FILE)

dry-run: ## Show what apply would do without changing anything [FILE=]
	chezmoi apply --dry-run --verbose $(FILE)

diff: ## Diff live files against the source; prints rendered secrets [FILE=]
	chezmoi diff $(FILE)

status: ## List files that differ (A/M/D) and scripts that would run (R)
	chezmoi status

verify: ## Exit non-zero if any managed file has drifted from the source
	chezmoi verify

update: ## git pull, then apply
	chezmoi update

upgrade: ## Update Homebrew and upgrade all installed packages (bootstrap does this too)
	brew update
	brew upgrade
	brew cleanup

add: ## Start managing a live file: make add FILE=~/.foo
	@test -n "$(FILE)" || { echo "usage: make add FILE=<path>"; exit 1; }
	chezmoi add $(FILE)

re-add: ## Copy live edits back into the source (skips templates) [FILE=]
	chezmoi re-add $(FILE)

edit: ## Edit a file's source, then apply it: make edit FILE=~/.zshrc
	@test -n "$(FILE)" || { echo "usage: make edit FILE=<path>"; exit 1; }
	chezmoi edit --apply $(FILE)

managed: ## List every path chezmoi manages
	chezmoi managed

unmanaged: ## List files under ~/.config and ~/.claude that chezmoi does not manage
	chezmoi unmanaged ~/.config ~/.claude

data: ## Show template data (machine, email, osid, Keeper UIDs)
	chezmoi data

doctor: ## Check the chezmoi install, config, and password manager CLIs
	chezmoi doctor

reset-once: ## Make run_once_ scripts run again on the next apply
	chezmoi state delete-bucket --bucket=scriptState

reset-onchange: ## Make run_onchange_ scripts run again on the next apply
	chezmoi state delete-bucket --bucket=entryState

guard: ## Scan every tracked file for workplace-identifying text
	git ls-files -z | xargs -0 python3 $(GUARD)

lint: ## Lint Markdown (and Markdown templates)
	markdownlint-cli2 "**/*.md" "**/*.md.tmpl"

lint-fix: ## Auto-fix Markdown lint issues
	markdownlint-cli2 --fix "**/*.md" "**/*.md.tmpl"

sync-work: ## Copy pfe-installed Claude files from this work machine into the source, then guard
	@for f in $$(chezmoi execute-template '{{ range .claudeShared }}{{ . }} {{ end }}'); do \
		mkdir -p "$$(dirname "home/dot_claude/$$f")"; \
		cp -R "$$HOME/.claude/$$f" "$$(dirname "home/dot_claude/$$f")/"; \
		echo "synced $$f"; \
	done
	@git ls-files -mo --exclude-standard -z home/dot_claude | xargs -0 python3 $(GUARD)

check: guard lint ## Run guard and lint, as the pre-commit hook does
