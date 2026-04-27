# Output Path Resolver

Canonical logic for deciding where a transcript file should be written. **Every transcribe skill in this plugin loads this reference and follows it.** No skill hardcodes an output path; no skill reads a `default_output_dir` from config (there isn't one).

The resolver is deliberately context-aware: where you are when you trigger a transcribe is usually a strong signal of where the transcript belongs.

## Algorithm

```
1. repo_root := `git rev-parse --show-toplevel 2>/dev/null`
2. if repo_root is empty (cwd is not inside a git repo):
     ask user: "Where should I save the transcript?"
       - accept absolute path, relative path, or `here` (= cwd)
       - no default — do NOT silently pick one
     return user's path
3. else (cwd is inside a git repo):
     existing := first folder that exists at repo_root/, in this order:
       - transcriptions/
       - transcripts/
       - recordings/
     if existing is set:
       output_dir := repo_root/<existing>
     else:
       maybe_spec := check if this is a spec context (see below)
       if maybe_spec:
         output_dir := repo_root/<spec_folder>   (specs/ or spec/, whichever exists)
       else:
         output_dir := repo_root/transcriptions/   (create it)
     return output_dir
```

## Spec-context detection

A repo is treated as "potentially spec-relevant" if **all** of:

- It looks like a dev project (has any of: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Gemfile`, `pom.xml`, `build.gradle`, `composer.json`, `mix.exs`)
- It has a `specs/` or `spec/` folder at the root
- The user has not already given a clear non-spec hint (e.g., they said "meeting recording", "interview", "voice memo")

When all three hold, **ask** the user:

> This looks like a spec-capable repo. Is this recording a spec (saves to `specs/`) or general (saves to `transcriptions/`)?

If they pick spec, write into the existing `specs/` (or `spec/`) folder. Don't create a new one.

If only `specs/` exists but the repo isn't dev-shaped, treat it as a regular `transcriptions/` case — don't conflate.

## Filename

Inside the resolved directory, the filename is:

```
<sanitised-source-stem>-<variant>.<ext>
```

- `sanitised-source-stem` — basename of the input audio file with non-alphanumerics collapsed to `-`
- `variant` — one of `raw`, `cleaned`, `structured`, `notes`, `summary`, `blog` (whatever the skill is producing)
- `ext` — `md` for text, `srt` / `vtt` for timed, `json` for raw provider output

If a file at that path already exists, append `-2`, `-3`, etc.

## After writing

Always print the resolved absolute path so the user knows exactly where it landed. Example:

```
✓ Transcript saved: /home/user/repos/my-project/transcriptions/team-sync-cleaned.md
```

## Why this design

- **No global default output dir.** A single setting can't capture "for repo X save to specs, for repo Y save to transcriptions, when at home ask me." Inferring from cwd is more accurate than asking once and getting it wrong forever.
- **Specs are a known case.** Voice-noting a spec into a dev repo is a common workflow; surfacing the choice once per recording is worth it.
- **Outside any repo, no guessing.** Picking `~/Transcripts` or cwd silently is a recipe for lost files. Ask.
- **Single source of truth.** Adding a new context (e.g., a `meetings/` convention) means editing this file only.
