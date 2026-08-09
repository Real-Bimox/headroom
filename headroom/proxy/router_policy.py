"""Provider-neutral policy for selecting compression strategies.

Keeping this separate from the ASGI server lets configuration and router
selection be tested without constructing HTTP clients or proxy lifecycle
state.
"""

from __future__ import annotations

import logging

from headroom.transforms import ContentRouterConfig

logger = logging.getLogger(__name__)

BUILTIN_COMPRESSOR_FLAGS: dict[str, str] = {
    "smart_crusher": "enable_smart_crusher",
    "kompress": "enable_kompress",
    "code_aware": "enable_code_aware",
    "search": "enable_search_compressor",
    "log": "enable_log_compressor",
    "tabular": "enable_tabular_compressor",
    "config": "enable_config_compressor",
    "html": "enable_html_extractor",
    "image": "enable_image_optimizer",
}


def apply_compressor_selection(router_config: ContentRouterConfig, compressors: set[str] | None) -> None:
    """Apply the selected built-ins to an existing router configuration."""
    if compressors is None:
        return
    selected = {name.strip() for name in compressors if name.strip()}
    if not selected:
        return
    select_all = "*" in selected
    unmatched = sorted(selected - set(BUILTIN_COMPRESSOR_FLAGS) - {"*"})
    if unmatched:
        if select_all or selected & set(BUILTIN_COMPRESSOR_FLAGS):
            logger.warning(
                "compressor selection: %s match no built-in compressor "
                "(assumed registry names); built-ins: %s",
                ", ".join(unmatched),
                ", ".join(sorted(BUILTIN_COMPRESSOR_FLAGS)),
            )
        else:
            logger.warning(
                "compressor selection %s matches no built-in compressor — every "
                "built-in compressor is now disabled. If this is a typo, valid "
                "names are: %s (or '*' for all).",
                ", ".join(unmatched),
                ", ".join(sorted(BUILTIN_COMPRESSOR_FLAGS)),
            )
    for name, flag in BUILTIN_COMPRESSOR_FLAGS.items():
        setattr(router_config, flag, select_all or name in selected)


def external_compressor_selection(compressors: set[str] | None) -> list[str] | None:
    """Return only selected third-party compressor entry points."""
    if not compressors:
        return None
    selected = {name.strip() for name in compressors if name.strip()}
    if not selected:
        return None
    if "*" in selected:
        return ["*"]
    external = sorted(selected - set(BUILTIN_COMPRESSOR_FLAGS))
    return external or None
