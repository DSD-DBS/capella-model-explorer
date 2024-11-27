# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
"""Script to generate static sites based on the model-explorer templates."""

import collections.abc as cabc
import functools
import logging
import pathlib

import capellambse
import capellambse.model as m
import click
import jinja2
import lxml.html as lhtml
from lxml import etree
from lxml.builder import E

from . import __version__, templates

LOGGER = logging.getLogger(__name__)

GENERIC_TEMPLATE = "__generic__"


@click.command()
@click.version_option(version=__version__)
@click.option(
    "-m",
    "--model",
    type=capellambse.ModelCLI(),
    required=True,
    help="The Capella model to render",
)
@click.option(
    "-t",
    "--templates",
    "templates_path",
    type=click.Path(exists=True, path_type=pathlib.Path),
    required=True,
)
@click.option(
    "-o",
    "--output",
    type=click.Path(file_okay=False, path_type=pathlib.Path),
    default="./pages",
    show_default=True,
)
def main(
    *,
    model: capellambse.MelodyModel,
    templates_path: pathlib.Path,
    output: pathlib.Path,
) -> None:
    """Statically render a set of templates as standalone HTML pages."""
    logging.basicConfig(level="INFO")

    tl = templates.TemplateLoader(model).index_path(templates_path)
    needed_generic: set[capellambse.helpers.UUIDString] = set()

    def _generate_link(
        obj: m.ModelElement | m.AbstractDiagram, prefix: str = "../"
    ) -> str | None:
        for idx, templ in tl.flat.items():
            if templ.is_in_scope(obj):
                return f"{prefix}{idx}/{obj.uuid}.html"

        assert capellambse.helpers.is_uuid_string(obj.uuid)
        needed_generic.add(obj.uuid)
        if GENERIC_TEMPLATE in tl.flat:
            return f"{prefix}{GENERIC_TEMPLATE}/{obj.uuid}.html"
        return None

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_path))
    env.filters["make_href"] = make_href_filter

    index_body = E.body()
    templates_to_render = [
        (i, t) for i, t in tl.flat.items() if i != GENERIC_TEMPLATE
    ]
    num_templates = len(templates_to_render)
    num_padlen = len(str(num_templates))
    idx_padlen = max(len(i) for i, _ in templates_to_render)
    LOGGER.info("Rendering %d templates", num_templates)
    for template_number, (idx, template) in enumerate(tl.flat.items(), 1):
        if idx == GENERIC_TEMPLATE:
            continue

        template_path = templates_path.joinpath(template.template)
        j2template = env.from_string(template_path.read_text("utf-8"))
        tout = output.joinpath(idx)
        tout.mkdir(parents=True, exist_ok=True)

        index_body.append(E.h1(template.name, E.small(f" ({idx})")))
        pbar_label = f"[{template_number:{num_padlen}d}/{num_templates:{num_padlen}d}]: {idx:{idx_padlen}s}"

        if template.single:
            with click.progressbar(length=100, label=pbar_label) as dummybar:
                rendered = j2template.render(
                    object=None,
                    model=model,
                    diff_data={},
                    object_diff={},
                )
                rendered = capellambse.helpers.replace_hlinks(
                    rendered, model, _generate_link
                )
                tout.joinpath("render.html").write_text(rendered, "utf-8")
                dummybar.update(100)
            index_body.append(
                E.p(
                    E.a(
                        f"View the {template.name!r} template",
                        href=f"{idx}/render.html",
                    )
                )
            )
            continue

        objs: cabc.Sequence[m.ModelElement] = templates.find_objects(
            model,
            obj_type=template.scope.type,
            below=template.scope.below,
            attr=None,
            filters=template.scope.filters,
        )
        if not objs:
            with click.progressbar(length=100, label=pbar_label) as dummybar:
                dummybar.update(100)
            index_body.append(E.p("No objects use this template."))
            continue

        objs = sorted(
            objs,
            key=lambda o: (getattr(o, "name", ""), getattr(o, "uuid", "")),
        )
        index_list = E.ul()
        index_body.append(
            E.details(
                E.summary(f"Show objects in the {template.name!r} template"),
                index_list,
            )
        )

        with click.progressbar(
            objs,
            label=pbar_label,
            item_show_func=lambda o: str(getattr(o, "name", "")),
        ) as pbar:
            for obj in pbar:
                try:
                    rendered = j2template.render(
                        object=obj,
                        model=model,
                        diff_data={},
                        object_diff={},
                    )
                    rendered = capellambse.helpers.replace_hlinks(
                        rendered, model, _generate_link
                    )
                    tout.joinpath(f"{obj.uuid}.html").write_text(
                        rendered, "utf-8"
                    )
                except Exception:
                    LOGGER.exception(
                        "Error render template %s for %s", idx, obj.uuid
                    )
                else:
                    index_list.append(
                        E.li(*lhtml.fragments_fromstring(obj._short_html_()))
                    )

    LOGGER.info("Rendering loose objects using generic template")
    idx = GENERIC_TEMPLATE
    try:
        template = tl.flat[idx]
    except KeyError:
        LOGGER.error("Template %r not found, cannot render loose objects", idx)
    else:
        template_path = templates_path.joinpath(template.template)
        j2template = env.from_string(template_path.read_text("utf-8"))
        tout = output.joinpath(idx)
        tout.mkdir(parents=True, exist_ok=True)
        rendered_generic: set[capellambse.helpers.UUIDString] = set()

        while needed_generic:
            obj_id = needed_generic.pop()
            if obj_id in rendered_generic:
                continue
            rendered_generic.add(obj_id)

            try:
                rendered = j2template.render(
                    object=model.by_uuid(obj_id),
                    model=model,
                    diff_data={},
                    object_diff={},
                )
                rendered = capellambse.helpers.replace_hlinks(
                    rendered, model, _generate_link
                )
                tout.joinpath(f"{obj_id}.html").write_text(rendered, "utf-8")
            except Exception:
                LOGGER.exception("Error in generic template for %s", obj_id)

    rendered = etree.tostring(E.html(index_body), encoding=str)
    rendered = capellambse.helpers.replace_hlinks(
        rendered, model, functools.partial(_generate_link, prefix="")
    )
    output.joinpath("index.html").write_text(rendered, "utf-8")


def make_href_filter(obj: object) -> str:
    if jinja2.is_undefined(obj) or obj is None:
        return "hlink://00000000-0000-0000-0000-000000000000"

    if isinstance(obj, m.ElementList):
        raise TypeError("Cannot make an href to a list of elements")
    if not isinstance(obj, m.ModelElement | m.AbstractDiagram):
        raise TypeError(f"Expected a model object, got {obj!r}")

    return f"hlink://{obj.uuid}"


if __name__ == "__main__":
    main()
