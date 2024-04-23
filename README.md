<!--
 ~ Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Capella Model Explorer

![image](https://github.com/DSD-DBS/capella-model-explorer/actions/workflows/build-test-publish.yml/badge.svg)
![image](https://github.com/DSD-DBS/capella-model-explorer/actions/workflows/lint.yml/badge.svg)

A webapp for exploring Capella models through simple "auto-generated" textual and graphical views.

**Longer story**:

We see a larger non-MBSE crowd struggling with the things hidden in the model. With this app we expose model contents in an easy to review readable form with basic graphical annotations. Under the hood it uses Jinja templates enabling the tooling teams to support their users with model-derived documents of any shape and form.

**Use cases**:

- Provide insights into / "spell-out" the model for non-MBSE stakeholders via document-a-like dynamic views that describe model elements in a human-readable form.
- Provide meaningful default views (that can be further customized) for the key elements to kickstart the model exploration.

There are a few more use cases but we will reveal them a bit later.

# Quick start

Clone, then build and run locally with Docker:

```bash
docker build -t model-explorer:latest .
docker run -e ROUTE_PREFIX="" -v /absolute/path/to/your/model/folder/on/host:/model -v $(pwd)/templates:/views -p 8000:8000 model-explorer
```

Then open your browser at `http://localhost:8000/views` and start exploring your model.

While the thing is running you can edit the templates in the `templates` folder and see the changes immediately in the browser.

# Development (local)

To run the app in dev mode you'll need to first run `npm run build` - this is needed by the backend to have some statics to serve. Then run `npm run dev` in a terminal and `python -m capella_model_explorer.backend path_to_model path_to_templates` in another terminal. The backend and statically built frontend will be served at `http://localhost:8000`. The live frontend will be served by vite at `http://localhost:5173`(or similar, it will be printed in the terminal where you ran `npm run dev`).

# Documentation

Read the [full documentation on Github pages](https://dsd-dbs.github.io/capella-model-explorer).

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

then, to develop components `npm run storybook` and to develop the whole app `npm run dev`

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
