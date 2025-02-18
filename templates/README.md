<!--
 ~ Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Templates

This directory contains [Jinja2 templates] which are grouped in subdirectories
and [Jinja2 macro] files.

Each subdirectoy contains an index file named `index.yaml` with metadata for
the templates of the given template category.

The order of templates within a category is determined by the order in which
they are listed in the index file.

The name of a subdirectory defines the name of a template category. The
directory name can have an optional two-digit prefix (e. g. `10-`) that is used
to sort the categories when they are displayed in the web interface.

Template categories cannot be nested.

[Jinja2 templates]: https://jinja.palletsprojects.com/en/stable/
[Jinja2 macro]: https://jinja.palletsprojects.com/en/stable/templates/#macros
