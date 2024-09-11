<!--
 ~ Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Capella Model Explorer

![image](https://github.com/DSD-DBS/capella-model-explorer/actions/workflows/build-test-publish.yml/badge.svg)
![image](https://github.com/DSD-DBS/capella-model-explorer/actions/workflows/lint.yml/badge.svg)

A webapp for exploring Capella models through simple "auto-generated" textual
and graphical views.

**Longer story**:

We see a larger non-MBSE crowd struggling with the things hidden in the model.
With this app we expose model contents in an easy to review readable form with
basic graphical annotations. Under the hood it uses Jinja templates enabling
the tooling teams to support their users with model-derived documents of any
shape and form.

**Use cases**:

- Provide insights into / "spell-out" the model for non-MBSE stakeholders via
  document-a-like dynamic views that describe model elements in a
  human-readable form.
- Provide meaningful default views (that can be further customized) for the key
  elements to kickstart the model exploration.

There are a few more use cases but we will reveal them a bit later.

# Quick start

Clone, then build and run locally with Docker:

```bash
docker build -t model-explorer:latest .
docker run -e ROUTE_PREFIX="" -v /absolute/path/to/your/model/folder/on/host:/model -v $(pwd)/templates:/views -p 8000:8000 model-explorer
```

Then open your browser at `http://localhost:8000/views` and start exploring
your model.

While the thing is running you can edit the templates in the `templates` folder
and see the changes immediately in the browser.

# Development (local)

To run the app in dev mode you'll need to first run `npm run build` - this is
needed by the backend to have some statics to serve. Then run `npm run dev` in
a terminal and
`python -m capella_model_explorer.backend path_to_model path_to_templates` in
another terminal. The backend and statically built frontend will be served at
`http://localhost:8000`. The live frontend will be served by vite at
`http://localhost:5173`(or similar, it will be printed in the terminal where
you ran `npm run dev`). If you wish to display the Frontend Software Version,
it will initially show 'Fetch Failed'. To successfully fetch and display the
version, you need to run the command `python frontend/fetch_version.py`.

# Installation

You can install the latest released version directly from PyPI.

```sh
pip install capella-model-explorer
```

To set up a development environment, clone the project and install it into a
virtual environment.

```sh
git clone https://github.com/DSD-DBS/capella-model-explorer
cd capella-model-explorer
python -m venv .venv

source .venv/bin/activate.sh  # for Linux / Mac
.venv\Scripts\activate  # for Windows

pip install -U pip pre-commit
pip install -e '.[docs,test]'
pre-commit install
```

# Front-end development

To develop the frontend:

```bash
cd frontend
npm install
```

then, to develop components `npm run storybook` and to develop the whole app
`npm run dev`

# Integration in the Capella Collaboration Manager

The Capella Model Explorer can be integrated into the
[Capella Collaboration Manager](https://github.com/DSD-DBS/capella-collab-manager).

To do so, you need a running instance of the Capella Collaboration Manager.
Navigate to `Menu` > `Settings` > `Tools` > `Add a new tool` and fill in the
following configuration:

```yaml
name: "Capella model explorer"
integrations:
  t4c: false
  pure_variants: false
  jupyter: false
config:
  resources:
    cpu:
      requests: 0.4
      limits: 2
    memory:
      requests: 1.6Gi
      limits: 6Gi
  environment:
    MODEL_ENTRYPOINT:
      stage: before
      value: "{CAPELLACOLLAB_SESSION_PROVISIONING[0][path]}"
    ROUTE_PREFIX: "{CAPELLACOLLAB_SESSIONS_BASE_PATH}"
  connection:
    methods:
      - id: f51872a8-1a4f-4a4d-b4f4-b39cbd31a75b
        type: http
        name: Direct Browser connection
        sharing:
          enabled: true
        ports:
          metrics: 8000
          http: 8000
        redirect_url: "{CAPELLACOLLAB_SESSIONS_SCHEME}://{CAPELLACOLLAB_SESSIONS_HOST}:{CAPELLACOLLAB_SESSIONS_PORT}{CAPELLACOLLAB_SESSIONS_BASE_PATH}/"
  monitoring:
    prometheus:
      path: /metrics
  provisioning:
    directory: /models
    max_number_of_models: 1
  persistent_workspaces:
    mounting_enabled: false
```

You can tune the resources according to your needs.

After saving the configuration, you have to add a version for the new tool.
Since the Capella Model Explorer can load different Capella versions, we can
use one generic version:

```yaml
name: "Generic"
config:
  is_recommended: true
  is_deprecated: false
  sessions:
    persistent:
      image: ghcr.io/dsd-dbs/capella-model-explorer/model-explorer:latest
  backups:
    image: null
  compatible_versions: [1, 2, 3, 4]
```

Replace the numbers in `compatible_versions` with the version IDs for the
versions you want to support.

When configured properly, users will be able to start read-only sessions for
the Capella Model Explorer. More information about read-only sessions is
available in the
[Capella Collaboration Manager documentation](https://dsd-dbs.github.io/capella-collab-manager/user/sessions/types/read-only/).

# Contributing

We'd love to see your bug reports and improvement suggestions! Please take a
look at our [guidelines for contributors](CONTRIBUTING.md) for details.

# Licenses

This project is compliant with the
[REUSE Specification Version 3.0](https://git.fsfe.org/reuse/docs/src/commit/d173a27231a36e1a2a3af07421f5e557ae0fec46/spec.md).

Copyright DB InfraGO AG, licensed under Apache 2.0 (see full text in
[LICENSES/Apache-2.0.txt](LICENSES/Apache-2.0.txt))

Dot-files are licensed under CC0-1.0 (see full text in
[LICENSES/CC0-1.0.txt](LICENSES/CC0-1.0.txt))
