---
name: configure
description: Onboarding for Claude-Transcription — registers the user's transcription and denoise backends (cloud APIs, MCP servers, local binaries, custom endpoints) into a user-data config file. No provider hardcoded; user picks what they have. Use when the user asks to configure claude-transcription, set up the plugin, add a new transcription backend, or pick a default provider.
---

# Configure Claude-Transcription

Interactive setup that registers the user's actual transcription and denoise backends, then writes them to a config file in the canonical user-data dir. Skills in this plugin read that config — no provider names, API endpoints, or keys are hardcoded.

## Config path (canonical user-data convention)

```
${CLAUDE_USER_DATA:-${XDG_DATA_HOME:-$HOME/.local/share}/claude-plugins}/claude-transcription/config.json
```

Resolution order:
1. `$CLAUDE_USER_DATA/claude-transcription/config.json` if `$CLAUDE_USER_DATA` is set
2. Else `$XDG_DATA_HOME/claude-plugins/claude-transcription/config.json` if `$XDG_DATA_HOME` is set
3. Else `$HOME/.local/share/claude-plugins/claude-transcription/config.json`

Create parent directories with `mkdir -p` if missing. **Never** write under `~/.claude/`.

### Migrating from old path

If `~/.config/claude-transcription/config.json` exists (legacy, schema v1) and the new path does not, offer to migrate. The legacy schema is flat; convert it to schema v2 (below) by mapping the single `transcription_provider` / `denoise_provider` strings into the providers list with `default: true`.

## Schema v2

```json
{
  "schema_version": 2,
  "providers": {
    "transcription": [
      {
        "alias": "<short alias the user uses to refer to this backend>",
        "type": "api | mcp | local-binary | custom-endpoint",
        "default": true,
        "...type-specific fields...": "..."
      }
    ],
    "denoise": [
      { "alias": "...", "type": "...", "default": true }
    ]
  }
}
```

### Provider entry — type-specific fields

| `type` | Required fields | Optional fields | Notes |
|---|---|---|---|
| `api` | `api_key_env` (env var name OR `op://...` reference) | `endpoint` (override default), `model` | Cloud API with bearer key |
| `mcp` | `mcp_server` (full MCP server name as it appears in the MCP list) | `tool_name` (specific tool to call) | Backend invoked via an MCP tool |
| `local-binary` | `binary_name` (`whisper`, `whisper.cpp`, `ffmpeg`, etc.) | `model`, `device`, `extra_args` | Local CLI binary |
| `custom-endpoint` | `endpoint` (URL) | `api_key_env`, `auth_header`, `request_format` | User's own server (vLLM, llama.cpp server, etc.) |

**Credentials rule:** never store the actual key in this file. Always reference via env var name or `op://vault/item/field` (resolved at runtime by `op read`). The plugin supports both forms.

## Interactive flow

Ask the user, in order:

### 1. Transcription backends

> Which transcription backends do you want to register? Pick any number; I'll ask for details on each.

Suggestions (not exhaustive — accept any):
- **Gemini multimodal** (cloud, via API or MCP)
- **OpenAI Whisper API** (cloud, API)
- **AssemblyAI** (cloud, API — adds diarization + timestamps)
- **Deepgram** (cloud, API)
- **Local Whisper** (`faster-whisper` or `whisper.cpp`, local binary)
- **Custom endpoint** (your own vLLM / llama.cpp / OpenAI-compatible server)
- **MCP server** (any registered MCP server with a transcription tool)

For each picked backend:
- Alias (short, lowercase — e.g. `gemini`, `aai`, `whisper-local`, `my-vllm`)
- Type (`api`, `mcp`, `local-binary`, or `custom-endpoint`)
- Type-specific fields (per the table above)

### 2. Denoise backends

Same loop. Suggestions:
- **Auphonic** (cloud API, cheap, good default)
- **ElevenLabs** (cloud API)
- **Dolby.io** (cloud API)
- **DeepFilterNet** (local ML)
- **ffmpeg afftdn** (local non-ML)
- **MCP server** with a denoise tool
- **Custom endpoint**

### 3. Pick defaults

> Which transcription backend should I use when you say "transcribe this" without naming a provider?

Same for denoise. Mark the chosen entries with `"default": true`. Only one default per category.

### 4. Verify credentials

For every `api` or `custom-endpoint` provider with an `api_key_env`: check `printenv "$VARNAME"` returns a non-empty value. If empty, list the missing env vars at the end and tell the user to set them in their shell profile (`~/.bashrc`, `~/.zshenv`, etc.). Don't fail setup over missing keys — the user might set them later.

For `op://` references: do not test-resolve during setup (would prompt for biometric unlock). Just record the reference.

For `mcp` providers: confirm the named MCP server appears in the user's installed MCP list (run `claude mcp list` and grep). Warn but don't fail if not.

For `local-binary`: check the binary is on `$PATH` (`command -v <binary>`). Warn if not found.

## Subcommands

Beyond the full interview, support:

- **`show`** — pretty-print the current config (mask any field containing `key`, `token`, `secret`).
- **`add <category>`** — add one new backend (transcription or denoise) without re-asking for the others.
- **`remove <category> <alias>`** — remove a registered backend.
- **`set-default <category> <alias>`** — change which backend is the default.
- **`validate`** — re-run credential and binary checks against the existing config.

## Argument-driven shortcuts

For non-interactive setup (e.g., from a script):

```
configure add transcription --alias gemini --type mcp --mcp-server jungle-shared__gemini-transcription --default
configure add transcription --alias aai --type api --api-key-env ASSEMBLYAI_API_KEY
configure set-default transcription aai
```

## Validation rules

- Aliases must be unique within their category (a transcription `gemini` and a denoise `gemini` are fine; two transcription `gemini` entries are not).
- Exactly one default per category. If the user removes the default, immediately ask which alias should become the new default.
- `type` must be one of the four allowed values. Reject unknowns.
- `mcp_server` names should be validated against `claude mcp list` (warn if missing).

## What NOT to do

- Don't bake provider names, models, or endpoints into other skills. Every skill that picks a backend must read this config.
- Don't store API keys in this file. Env var names or `op://` references only.
- Don't create a `default_output_dir` field — output paths are runtime-resolved per `references/output-path-resolver.md`.
- Don't write under `~/.claude/`. That's Claude's config surface.
