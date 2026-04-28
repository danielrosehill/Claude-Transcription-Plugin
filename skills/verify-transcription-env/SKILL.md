---
name: verify-transcription-env
description: Sanity-check the transcription plugin's environment — confirm required API keys are set and reachable via cheap ping. Use when the user asks "is transcription working?", reports a transcription failure, or after changing API keys / shell config.
---

# Verify transcription environment

Cheap end-to-end check that the API keys this plugin depends on are (a) present in the environment and (b) actually accept a request. Reports per-provider status.

## Providers checked

| Provider | Env var | Used by |
|---|---|---|
| AssemblyAI | `ASSEMBLYAI_API_KEY` | `transcribe-assemblyai` |
| OpenRouter (Gemini) | `OPENROUTER_API_KEY` | `gemini-transcription` MCP, `transcribe-gemini-*` skills |
| Google Gemini (direct) | `GEMINI_API_KEY` | optional alt path for Gemini skills |

## How

For each provider, do the cheapest request that proves the key works:

### AssemblyAI
```bash
curl -sS -o /dev/null -w "%{http_code}" \
  -H "Authorization: $ASSEMBLYAI_API_KEY" \
  https://api.assemblyai.com/v2/transcript?limit=1
```
- `200` → key valid
- `401` → key invalid or missing
- non-2xx → report code

### OpenRouter
```bash
curl -sS -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  https://openrouter.ai/api/v1/auth/key
```
- `200` → key valid
- `401` → invalid

### Google Gemini (direct)
```bash
curl -sS -o /dev/null -w "%{http_code}" \
  "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY"
```
- `200` → key valid

## Output

Render a compact status table:

```
Provider       Env var                 Status
─────────────────────────────────────────────────
AssemblyAI     ASSEMBLYAI_API_KEY      OK (200)
OpenRouter     OPENROUTER_API_KEY      MISSING
Gemini direct  GEMINI_API_KEY          OK (200)
```

For any `MISSING` or non-OK row, suggest the fix:
- Missing → "set in `~/.bashrc` / `~/.zshrc` and reload, or add to `~/.claude/settings.json` `env`"
- 401 → "key is set but rejected; rotate or check for stray whitespace"

## Notes

- Do not print the key values themselves, only their presence and the HTTP status.
- If `curl` is missing, fall back to `wget -S -O /dev/null`.
- This skill is read-only — no API calls that incur cost beyond the auth ping.
