import click
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import capellambse
from pathlib import Path
import yaml
import operator
from jinja2 import Environment


app = FastAPI()
app.model_path = None
app.templates_path = None
app.model = None
app.templates = {}
app.env = Environment()


def index_templates(path: Path):
    templates = {}
    for template_file in path.glob('*.yaml'):
        with open(template_file, 'r') as f:
            template = yaml.safe_load(f)
            templates[template_file.name[:-5]] = template
            # later we could add here count of objects that can be rendered with this template
    return templates


def find_objects(model, obj_type, below=None):
    if below:
        getter = operator.attrgetter(below)
        return model.search(obj_type, below=getter(model))
    return model.search(obj_type)



@click.command()
@click.argument('model', type=click.Path(exists=True))
@click.argument('templates', type=click.Path(exists=True))
def run(model, templates):
    app.model_path = model
    app.templates_path = Path(templates)
    app.templates = index_templates(app.templates_path)
    app.model = capellambse.MelodyModel(app.model_path)
    uvicorn.run(app, host="0.0.0.0", port=8000)


@app.get("/")
def read_root():
    return {"badge": app.model.description_badge}


@app.get("/templates")
def read_templates():
    # list all templates in the templates folder (files that end with .yaml)
    app.templates = index_templates(app.templates_path)
    templates = [dict(idx=key, **app.templates[key]) for key in app.templates]
    return templates


@app.get("/templates/{template_name}")
def read_template(template_name: str):
    base = app.templates[template_name]
    variable = base["variable"]
    objects = find_objects(app.model, variable["type"], variable["below"])
    base["objects"] = [{"idx": obj.uuid, "name": obj.name} for obj in objects]
    return base


@app.get("/templates/{template_name}/{object_id}")
def render_template(template_name: str, object_id: str):
    base = app.templates[template_name]
    template_filename = base["template"]
    # load the template file from the templates folder
    with open(app.templates_path / template_filename, 'r') as f:
        template = app.env.from_string(f.read())
    object = app.model.by_uuid(object_id)
    # render the template with the object
    rendered = template.render(object=object)
    return HTMLResponse(content=rendered, status_code=200)


if __name__ == "__main__":
    run()