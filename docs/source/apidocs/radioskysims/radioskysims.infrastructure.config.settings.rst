:py:mod:`radioskysims.infrastructure.config.settings`
=====================================================

.. py:module:: radioskysims.infrastructure.config.settings

.. autodoc2-docstring:: radioskysims.infrastructure.config.settings
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`Paths <radioskysims.infrastructure.config.settings.Paths>`
     - .. autodoc2-docstring:: radioskysims.infrastructure.config.settings.Paths
          :summary:
   * - :py:obj:`Settings <radioskysims.infrastructure.config.settings.Settings>`
     - .. autodoc2-docstring:: radioskysims.infrastructure.config.settings.Settings
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`toml_path <radioskysims.infrastructure.config.settings.toml_path>`
     - .. autodoc2-docstring:: radioskysims.infrastructure.config.settings.toml_path
          :summary:
   * - :py:obj:`settings <radioskysims.infrastructure.config.settings.settings>`
     - .. autodoc2-docstring:: radioskysims.infrastructure.config.settings.settings
          :summary:

API
~~~

.. py:data:: toml_path
   :canonical: radioskysims.infrastructure.config.settings.toml_path
   :value: None

   .. autodoc2-docstring:: radioskysims.infrastructure.config.settings.toml_path

.. py:class:: Paths(/, **data: typing.Any)
   :canonical: radioskysims.infrastructure.config.settings.Paths

   Bases: :py:obj:`pydantic.BaseModel`

   .. autodoc2-docstring:: radioskysims.infrastructure.config.settings.Paths

   .. rubric:: Initialization

   .. autodoc2-docstring:: radioskysims.infrastructure.config.settings.Paths.__init__

   .. py:attribute:: sat_signals
      :canonical: radioskysims.infrastructure.config.settings.Paths.sat_signals
      :type: pathlib.Path | None
      :value: None

      .. autodoc2-docstring:: radioskysims.infrastructure.config.settings.Paths.sat_signals

.. py:class:: Settings(_case_sensitive: bool | None = None, _nested_model_default_partial_update: bool | None = None, _env_prefix: str | None = None, _env_file: pydantic_settings.sources.DotenvType | None = ENV_FILE_SENTINEL, _env_file_encoding: str | None = None, _env_ignore_empty: bool | None = None, _env_nested_delimiter: str | None = None, _env_nested_max_split: int | None = None, _env_parse_none_str: str | None = None, _env_parse_enums: bool | None = None, _cli_prog_name: str | None = None, _cli_parse_args: bool | list[str] | tuple[str, ...] | None = None, _cli_settings_source: pydantic_settings.sources.CliSettingsSource[typing.Any] | None = None, _cli_parse_none_str: str | None = None, _cli_hide_none_type: bool | None = None, _cli_avoid_json: bool | None = None, _cli_enforce_required: bool | None = None, _cli_use_class_docs_for_groups: bool | None = None, _cli_exit_on_error: bool | None = None, _cli_prefix: str | None = None, _cli_flag_prefix_char: str | None = None, _cli_implicit_flags: bool | None = None, _cli_ignore_unknown_args: bool | None = None, _cli_kebab_case: bool | typing.Literal[all, no_enums] | None = None, _cli_shortcuts: collections.abc.Mapping[str, str | list[str]] | None = None, _secrets_dir: pydantic_settings.sources.PathType | None = None, **values: typing.Any)
   :canonical: radioskysims.infrastructure.config.settings.Settings

   Bases: :py:obj:`pydantic_settings.BaseSettings`

   .. autodoc2-docstring:: radioskysims.infrastructure.config.settings.Settings

   .. rubric:: Initialization

   .. autodoc2-docstring:: radioskysims.infrastructure.config.settings.Settings.__init__

   .. py:attribute:: model_config
      :canonical: radioskysims.infrastructure.config.settings.Settings.model_config
      :value: 'SettingsConfigDict(...)'

      .. autodoc2-docstring:: radioskysims.infrastructure.config.settings.Settings.model_config

   .. py:attribute:: paths
      :canonical: radioskysims.infrastructure.config.settings.Settings.paths
      :type: radioskysims.infrastructure.config.settings.Paths
      :value: 'Paths(...)'

      .. autodoc2-docstring:: radioskysims.infrastructure.config.settings.Settings.paths

   .. py:method:: load(toml_path: str | pathlib.Path | None = None) -> radioskysims.infrastructure.config.settings.Settings
      :canonical: radioskysims.infrastructure.config.settings.Settings.load
      :classmethod:

      .. autodoc2-docstring:: radioskysims.infrastructure.config.settings.Settings.load

.. py:data:: settings
   :canonical: radioskysims.infrastructure.config.settings.settings
   :value: 'load(...)'

   .. autodoc2-docstring:: radioskysims.infrastructure.config.settings.settings
