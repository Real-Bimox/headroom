# Fork enhancements

This fork tracks `chopratejas/headroom` while maintaining the following local
product and reliability improvements.

## Agent support

- `headroom wrap qwen` supports Qwen Code through the local proxy.
- Qwen Coding and Token plans select their correct upstream endpoint and
  credential environment variable.

## Output efficiency

- Output shaping, cross-turn de-duplication, thinking compaction, and chat
  effort routing are enabled by default for supported OpenAI traffic.

## Reliability and developer experience

- Proxy startup checks for its optional runtime dependencies before importing
  the server, including HTTP/2 support (`h2`).
- The normal development profile is lean; ML/evaluation dependencies are
  explicitly opted into with `dev-ml`.
- Optional model/compressor warmup is opt-in with `HEADROOM_EAGER_PRELOAD=1`.
  The proxy otherwise binds first and loads optional assets lazily.

## Internal seams

- Provider targets are isolated per proxy instance rather than shared mutable
  class state.
- Process runtime settings resolve through a dedicated configuration boundary.
- Compressor-selection policy is separate from ASGI server orchestration.
- Declarative tool metadata underpins Qwen, Kimi, and Vibe wrapper discovery.

## Local operation

Install this checkout globally with proxy dependencies:

```bash
uv tool install --force --editable '.[proxy]' --python python3.13
```

Then run `headroom wrap qwen` or `headroom proxy --port 8787` as usual.
