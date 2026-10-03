---
name: commit-push-dev
description: Commit the current working-tree changes with an English commit message whose subject carries a README-derived category (`feat: [icon-picker] ...`), then push. Use whenever the user asks to commit and/or push, in any language, including Korean requests such as "커밋해", "커밋하고 푸시해", "커밋 푸시해", "푸시해", or "커밋메시지 영어로 정리해서 커밋 푸시해".
---

# commit-push-dev

Commit the current changes and push them. This skill works in English by default:
the commit message and the final report are both in English.

## Steps

1. Inspect before staging:
   - `git status --short`, `git diff` and `git diff --cached` (read the real changes;
     do not describe them from memory), and `git log -5 --format=%s` for style.
   - If there is nothing to commit, say so and stop.
2. Decide what belongs in the commit.
   - Stage files by name. Use `git add -A` only when every change is clearly part of
     this work.
   - Never stage secrets (`.env`, keys, tokens) or ignored build output
     (`.venv/`, `.build-venv/`, `build/`, `__pycache__/`).
   - If the changes mix unrelated topics, or an untracked file (for example
     `.claude/`) is not clearly part of the work, ask the user instead of guessing.
     Split into several commits when the topics are independent.
3. Pick the category from `README.md`:
   - Read the current headings (`## Features`, `### Icon picker`, `## Terminal
     execution`, `## Versioning and distribution`, ...) and choose the one that best
     names the area the change touches. Do not use a remembered list; the README is
     the source of truth and its headings change.
   - Write it as lowercase kebab-case: `Icon picker` -> `icon-picker`,
     `Application editor` -> `application-editor`, `Main window` -> `main-window`,
     `` `--no-sandbox` diagnosis `` -> `sandbox-diagnosis`,
     `Versioning and distribution` -> `distribution`, `Tests` -> `tests`.
   - A change that spans several areas uses the dominant one; if none dominates,
     use the closest umbrella heading (for example `features`, `requirements`).
4. Write the message.
   - Subject: `<type>: [<category>] <summary>`, for example
     `feat: [icon-picker] convert non-PNG icons to cached PNG previews`.
   - `<type>` is one of `feat`, `fix`, `docs`, `refactor`, `test`, `build`, `chore`.
   - `<summary>` is imperative, lowercase, no trailing period; keep the whole subject
     at about 72 characters or fewer.
   - Add a body (blank line after the subject) when the reason is not obvious:
     explain why, not a line-by-line diff. Wrap at about 72 characters; bullets are
     fine for several distinct changes.
   - Finish with the commit attribution trailer the harness requires, if one is given.
5. Commit with the message passed through a heredoc, then `git push`.
   - Push the current branch to its upstream. If it has no upstream, use
     `git push -u origin HEAD`.
   - Never force-push, never skip hooks, and never amend commits that already exist.
   - If the push is rejected or a hook fails, report the output and stop; do not work
     around it.
6. Report in English: the commit hash and subject, the files included, and the push
   result. Mention anything deliberately left uncommitted.
