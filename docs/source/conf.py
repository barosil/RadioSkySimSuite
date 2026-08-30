# https://learn.scientific-python.org/development/guides/docs/
# https://diataxis.fr/
from __future__ import annotations

import importlib.metadata
import os
import sys

sys.path.insert(0, os.path.abspath("../../src/radioskysims"))

project = "RadioSkySim"
copyright = "2025, Luciano Barosi"
author = "Luciano Barosi"

try:
    version = release = importlib.metadata.version("radioskysim")
except importlib.metadata.PackageNotFoundError:
    version = release = "0.0.0"

extensions = [
    "sphinx.ext.napoleon",
    # myst_nb loads myst_parser internally — listing both causes
    # double-registration conflicts (sub-ref / figure-md, ValueError on
    # SphinxUnreferencedFootnotesDetector).
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx_copybutton",
    "sphinx_autodoc_typehints",
    "myst_nb",
    # "autodoc2",  # IO-002: UNCOMMENT to enable the auto-generated API
    #             # reference for the decoupled packages (autodoc2_packages
    #             # below is already configured). Requirements: install
    #             # `autodoc2` (NOT in the docs extra — see file_formats.md),
    #             # remove "apidocs/**" from exclude_patterns, and delete the
    #             # stale apidocs/ dir. Runbook: file_formats.md ->
    #             # "API reference generation (IO-002)".
]

# Notebooks (DOC-002): render with the outputs stored in each .ipynb file.
# Set nb_execution_mode = "cache" to re-execute and cache outputs
# (requires jupyter-cache + a configured kernel).
nb_execution_mode = "off"
nb_execution_timeout = 300

source_suffix = [".rst", ".md"]
exclude_patterns = [
    "_build",
    "**.ipynb_checkpoints",
    "Thumbs.db",
    ".DS_Store",
    ".env",
    ".venv",
    # Stale autodoc artifacts documenting the pre-decoupling monolith.
    # Kept on disk for history; excluded from the build until regenerated
    # via autodoc2 for the decoupled packages (task IO-002). See history_cleanup.
    # NOTE: when enabling IO-002 (autodoc2), remove "apidocs/**" from here.
    "apidocs/**",
    "modules/**",
    "_static/api/**",
]

# Mermaid code blocks: use a plain-text lexer so Sphinx does not warn about an
# unknown Pygments lexer (Mermaid still renders on GitHub / via mermaid tooling).
from pygments.lexers.special import TextLexer  # noqa: E402
from sphinx.highlighting import lexers  # noqa: E402

lexers["mermaid"] = TextLexer()

# autodoc2_packages = [
#     {
#         "path": "../src",
#     },
# ]

html_theme = "pydata_sphinx_theme"
# html_theme = "furo"
# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True


# html_theme_options: dict[str, Any] = {
#     "footer_icons": [
#         {
#             "name": "GitHub",
#             "url": "https://github.com/org/package",
#             "html": """
#                 <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
#                     <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
#                 </svg>
#             """,
#             "class": "",
#         },
#     ],
#     "source_repository": "https://github.com/org/package",
#     "source_branch": "main",
#     "source_directory": "docs/",
# }

# Permitir diretivas e roles do reStructuredText em Markdown
myst_enable_extensions = [
    "colon_fence",  # para blocos com ::: (como em .. admonition::)
    "deflist",  # listas de definição
    "html_image",  # imagens inline
    "dollarmath",  # suporte a $math$
    "linkify",  # transforma URLs automáticas em links
    "substitution",  # substituições tipo |project|
    "tasklist",  # listas com checkboxes
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# ══════════════════════════════════════════════════════════════════════
# IO-002 — autodoc2 API reference (decoupled packages)
# ══════════════════════════════════════════════════════════════════════
# This config is READY (active) but inert while the "autodoc2" extension is
# commented out. To enable the auto-generated API reference:
#   1. Uncomment "autodoc2" in the `extensions` list above.
#   2. Remove "apidocs/**" from `exclude_patterns` above.
#   3. Delete the stale monolith-era output:  rm -rf docs/source/apidocs
#   4. Rebuild:  make docs
# autodoc2 then regenerates `apidocs/` from the packages below; `api.md`
# includes them via toctree. Full runbook: file_formats.md ->
# "API reference generation (IO-002)".
autodoc2_packages = [
    {
        "path": "../../packages/radioskysims-core/src/radioskysims_core",
        "auto_mode": "all",
        "module_mode": "module",
        "ignore_patterns": ["__main__.py", "_version.py"],
    },
    {
        "path": "../../packages/radioskysims-beam/src/radioskysims_beam",
        "auto_mode": "all",
        "module_mode": "module",
        "ignore_patterns": ["__main__.py", "_version.py"],
    },
    {
        "path": "../../packages/radioskysims-skymap/src/radioskysims_skymap",
        "auto_mode": "all",
        "module_mode": "module",
        "ignore_patterns": ["__main__.py", "_version.py"],
    },
    {
        "path": "../../packages/radioskysims-radiotelescope/src/radioskysims_radiotelescope",
        "auto_mode": "all",
        "module_mode": "module",
        "ignore_patterns": ["__main__.py", "_version.py"],
    },
    {
        "path": "../../packages/radioskysims-sources/src/radioskysims_sources",
        "auto_mode": "all",
        "module_mode": "module",
        "ignore_patterns": ["__main__.py", "_version.py"],
    },
    {
        "path": "../../packages/radioskysims-simulation/src/radioskysims_simulation",
        "auto_mode": "all",
        "module_mode": "module",
        "ignore_patterns": ["__main__.py", "_version.py"],
    },
    {
        "path": "../../packages/radioskysims-waterfall/src/radioskysims_waterfall",
        "auto_mode": "all",
        "module_mode": "module",
        "ignore_patterns": ["__main__.py", "_version.py"],
    },
    {
        "path": "../../packages/radioskysims-viz/src/radioskysims_viz",
        "auto_mode": "all",
        "module_mode": "module",
        "ignore_patterns": ["__main__.py", "_version.py"],
    },
    {
        "path": "../../packages/gnsstools4astro/src/gnsstools4astro",
        "auto_mode": "all",
        "module_mode": "module",
        "ignore_patterns": ["__main__.py", "_version.py"],
    },
]

autodoc2_output_dir = "apidocs"

nitpick_ignore = [
    ("py:class", "_io.StringIO"),
    ("py:class", "_io.BytesIO"),
]

always_document_param_types = True
autosummary_generate = True
