<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>{{ text_plugin_synopsis }}</p>

  <p>
    <a href="{{ repo_url }}/releases"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/{{ repo_slug }}?label=Release"/></a>
    <a href="{{ repo_url }}/issues"><img alt="GitHub closed issues" src="https://img.shields.io/github/issues/{{ repo_slug }}?color=A24232&label=Issues"/></a>
    <a href="{{ repo_url }}/blob/{{ default_branch }}/LICENSE"><img alt="GitHub License" src="https://img.shields.io/github/license/{{ repo_slug }}?color=534BAE&label=License"/></a>
  </p>
</div>

******

### {{ h3_languages_with_ascii }}

******

{{ p_languages_all_supported_for_readme }}:

{{ placeholder_ul_languages_all_supported }}

******

### {{ h3_introduction }}

******

{{ p_introduction }}

> {{ p_evidence_boundary }}

******

### {{ h3_functions }}

******

{{ placeholder_features }}

******

### {{ h3_formats }}

******

{{ p_formats }}:

```text
input: {{ input_format }}
output: {{ output_format }}
runtime: {{ runtime_dependency }}
Python request: {{ python_line }}
expected packaged Python: {{ python_version_expected }}
```

{{ p_runtime_version_status }}

******

### {{ h3_plugin_interface }}

******

{{ p_plugin_interface }}:

```text
service action: {{ service_action }}
official index plugin id: {{ plugin_id }}
official index engine: {{ plugin_engine }}
official index variant: {{ plugin_variant }}
protocol provider id: {{ provider_id }}
engine: {{ engine_id }}
protocol: {{ protocol_version }}
```

{{ p_plugin_scope }}

******

### {{ h3_host_integration_status }}

******

> {{ p_host_integration_status }}

```text
release target: {{ release_target }}
release state: {{ release_state }}
paired host: {{ host_pairing }}
release branch: {{ default_branch }}
long-term signer: {{ long_term_signer }}
runtime/security/release owner: {{ release_owner }}
```

******

### {{ h3_security }}

******

{{ p_security }}

******

### {{ h3_security_limits }}

******

{{ placeholder_security_limits }}

******

### {{ h3_unsupported }}

******

{{ placeholder_unsupported_capabilities }}

******

### {{ h3_roadmap }}

******

{{ p_roadmap }}

- [{{ text_link_roadmap }}]({{ repo_url }}/blob/{{ default_branch }}/ROADMAP.md)

******

### {{ h3_release_history }}

******

{{ placeholder_latest_release_history }}

##### {{ h5_for_more_release_history }}

* {{ placeholder_read_more_in_changelog_md }}

******

### {{ h3_verification }}

******

{{ p_static_verification }}:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-r6-release-source.ps1
```

{{ p_bootstrap_verification }}:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest tools.tests.test_bootstrap -v
```

{{ p_deferred_verification }}

******

### {{ h3_build }}

******

{{ p_build_deferred }}

{{ p_local_aars }}:

```text
{{ local_aars }}
```

{{ p_build_architecture }}

******

### {{ h3_license }}

******

{{ p_license }}

******

### {{ h3_resource_layout }}

******

```text
.readme/lang_*.json
.changelog/lang_*.json
.python/generate_markdown.py
app/src/main/assets/doc/CHANGELOG-*.md
app/src/main/res/values-*/strings.xml
```

{{ p_resource_layout }}.

******

### {{ h3_links }}

******

- {{ text_link_autojs6_docs }}: {{ docs_autojs6_url }}
- {{ text_link_chaquopy }}: {{ chaquopy_url }}
- {{ text_link_cpython }}: {{ cpython_url }}
