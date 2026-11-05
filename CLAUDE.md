# CLAUDE.md - dotfiles

chezmoi-managed dotfiles for macOS, Debian/Ubuntu, and SteamOS. `.chezmoiroot` points at `home/`; files outside it are not installed. `bootstrap.sh` pulls, then runs `chezmoi init --apply` on this checkout.

- Template data comes from `home/.chezmoi.toml.tmpl`: `.machine` (`personal`/`work`), `.email`, `.osid`, `.steamos`, `.secretsBackend`. Machine differences go in templates; whole-file exclusions go in `home/.chezmoiignore`.
- Keep setup steps cross-platform: guard OS-specific commands, prefer Homebrew.
- Secrets are never committed. Add references to `home/.chezmoidata/secrets.yaml`; they resolve from Bitwarden (personal) or Keeper (work) at apply time.
- Markdown must pass `markdownlint-cli2` (run by the pre-commit hook; `--fix` auto-fixes).
- `home/dot_claude/modify_settings.json.tmpl` merges into the live Claude settings; don't replace it with a plain file.

## SteamOS

- Read-only root that updates revert: touch only `$HOME`. No `pacman`, `chsh` (`.bashrc` execs zsh), or `snap` (VS Code is a user Flatpak).
- No C compiler: a formula without an `x86_64_linux` or `all` bottle (`brew info --json=v2 <name>`) must sit behind `{{ if not .steamos }}` in the Brewfile.

## Public repo

Workplace-identifying text (hostnames, tenant names, Slack/GitHub IDs, work emails, colleague names) goes in Keeper, read with the `keeper-field` template. `dotfiles-guard` enforces this via the `.githooks/` pre-commit hook and a Claude Code edit hook.
