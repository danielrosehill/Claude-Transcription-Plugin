#!/usr/bin/env bash
# Auth-ping the three transcription providers. Read-only, prints status table.
# Used by the verify-transcription-env skill.

set -u

ROW_FMT="%-15s %-23s %s\n"

print_status() {
  local label="$1" var="$2" code="$3"
  case "$code" in
    "")      printf "$ROW_FMT" "$label" "$var" "MISSING" ;;
    2*)      printf "$ROW_FMT" "$label" "$var" "OK ($code)" ;;
    401|403) printf "$ROW_FMT" "$label" "$var" "REJECTED ($code) — rotate or check whitespace" ;;
    000)     printf "$ROW_FMT" "$label" "$var" "UNREACHABLE — network?" ;;
    *)       printf "$ROW_FMT" "$label" "$var" "HTTP $code" ;;
  esac
}

ping_with_header() {
  local label="$1" var="$2" url="$3" header="$4"
  local val="${!var:-}"
  if [[ -z "$val" ]]; then
    print_status "$label" "$var" ""
    return
  fi
  local code
  code=$(curl -sS -o /dev/null -w "%{http_code}" --max-time 8 \
    -H "$header: $val" "$url" 2>/dev/null || echo "000")
  print_status "$label" "$var" "$code"
}

ping_with_query() {
  local label="$1" var="$2" url_template="$3"
  local val="${!var:-}"
  if [[ -z "$val" ]]; then
    print_status "$label" "$var" ""
    return
  fi
  local code
  code=$(curl -sS -o /dev/null -w "%{http_code}" --max-time 8 \
    "${url_template/KEY/$val}" 2>/dev/null || echo "000")
  print_status "$label" "$var" "$code"
}

printf "$ROW_FMT" "Provider" "Env var" "Status"
printf -- "─────────────────────────────────────────────────\n"

ping_with_header "AssemblyAI"    "ASSEMBLYAI_API_KEY" \
  "https://api.assemblyai.com/v2/transcript?limit=1" "Authorization"

ping_with_header "OpenRouter"    "OPENROUTER_API_KEY" \
  "https://openrouter.ai/api/v1/auth/key" "Authorization: Bearer"

ping_with_query  "Gemini direct" "GEMINI_API_KEY" \
  "https://generativelanguage.googleapis.com/v1beta/models?key=KEY"
