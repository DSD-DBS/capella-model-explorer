# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import enum
import logging
import pathlib
import subprocess
import typing as t

import capellambse
import capellambse.model as m
import diff_match_patch
import typing_extensions as te
from capellambse.filehandler import git, local

logger = logging.getLogger(__name__)
NUM_COMMITS = "20"


class RevisionInfo(te.TypedDict, total=False):
    hash: te.Required[str]
    """The revision hash."""
    revision: str
    """The original revision passed to the diff tool."""
    author: str
    """The author of the revision, in "Name <email@domain>" format."""
    date: datetime.datetime
    """The time and date of the revision."""
    description: str
    """The description of the revision, i.e. the commit message."""
    subject: str
    """The subject of the commit."""
    tag: str | None
    """The tag of the commit."""


class Metadata(te.TypedDict):
    model: dict[str, t.Any]
    """The 'modelinfo' used to load the models, sans the revision key."""
    new_revision: RevisionInfo
    old_revision: RevisionInfo


class BaseObject(te.TypedDict):
    uuid: str
    display_name: str
    """Name for displaying in the frontend.

    This is usually the ``name`` attribute of the "current" version of
    the object.
    """


class FullObject(BaseObject, te.TypedDict):
    attributes: dict[str, t.Any]
    """All attributes that the object has (or had)."""


class ChangedAttribute(te.TypedDict):
    previous: t.Any
    """The old value of the attribute."""
    current: t.Any
    """The new value of the attribute."""


class ChangedObject(BaseObject, te.TypedDict):
    attributes: dict[str, ChangedAttribute]
    """The attributes that were changed."""


class ObjectChange(te.TypedDict, total=False):
    created: list[FullObject]
    """Contains objects that were created."""
    deleted: list[FullObject]
    """Contains objects that were deleted."""
    modified: list[ChangedObject]


ObjectLayer: te.TypeAlias = "dict[str, ObjectChange]"


class ObjectChanges(te.TypedDict, total=False):
    oa: ObjectLayer
    """Changes to objects from the OperationalAnalysis layer."""
    sa: ObjectLayer
    """Changes to objects from the SystemAnalysis layer."""
    la: ObjectLayer
    """Changes to objects from the LogicalAnalysis layer."""
    pa: ObjectLayer
    """Changes to objects from the PhysicalAnalysis layer."""
    epbs: ObjectLayer
    """Changes to objects from the EPBS layer."""


class ChangeSummaryDocument(te.TypedDict):
    metadata: Metadata
    objects: ObjectChanges


def init_model(model: capellambse.MelodyModel) -> str | None:
    """Initialize the model and return the path if it's a git repository."""
    file_handler = model.resources["\x00"]
    path = file_handler.path

    if isinstance(file_handler, git.GitFileHandler):
        path = file_handler.cache_dir
    elif (
        isinstance(file_handler, local.LocalFileHandler)
        and file_handler.rootdir.joinpath(".git").is_dir()
    ):
        pass
    else:
        return None
    return str(path)


def populate_commits(model: capellambse.MelodyModel):
    path = init_model(model)
    if not path:
        return path
    return get_commit_hashes(path)


def _serialize_obj(obj: t.Any) -> t.Any:
    if isinstance(obj, m.ModelElement):
        return {"uuid": obj.uuid, "display_name": _get_name(obj)}
    if isinstance(obj, m.ElementList):
        return [{"uuid": i.uuid, "display_name": _get_name(i)} for i in obj]
    if isinstance(obj, enum.Enum | enum.Flag):
        return obj.name
    return obj


def get_diff_data(model: capellambse.MelodyModel, head: str, prev: str):
    path = init_model(model)
    if not path:
        return None
    path = str(pathlib.Path(path).resolve())
    old_model = capellambse.MelodyModel(path=f"git+{path}", revision=prev)

    metadata: Metadata = {
        "model": {"path": path, "entrypoint": None},
        "old_revision": _get_revision_info(path, prev),
        "new_revision": _get_revision_info(path, head),
    }

    objects = compare_models(old_model, model)
    diff_data: ChangeSummaryDocument = {
        "metadata": metadata,
        "objects": objects,
    }
    return _traverse_and_diff(diff_data)


def _get_revision_info(
    repo_path: str,
    revision: str,
) -> RevisionInfo:
    """Return the revision info of the given model."""
    author, date_str, description = (
        subprocess.check_output(
            ["git", "log", "-1", "--format=%aN%x00%aI%x00%B", revision],
            cwd=repo_path,
            encoding="utf-8",
        )
        .strip()
        .split("\x00")
    )
    subject = description.splitlines()[0] if description.splitlines() else ""
    try:
        tag = subprocess.check_output(
            ["git", "tag", "--points-at", revision],
            cwd=repo_path,
            encoding="utf-8",
            stderr=subprocess.DEVNULL,
        ).strip()
    except subprocess.CalledProcessError:
        tag = None

    return {
        "hash": revision,
        "revision": revision,
        "author": author,
        "date": datetime.datetime.fromisoformat(date_str),
        "description": description.rstrip(),
        "subject": subject,
        "tag": tag if tag else None,
    }


def get_commit_hashes(path: str) -> list[RevisionInfo]:
    """Return the commit hashes of the given model."""
    commit_hashes = subprocess.check_output(
        ["git", "log", "-n", NUM_COMMITS, "--format=%H"],
        cwd=path,
        encoding="utf-8",
    ).splitlines()
    return [_get_revision_info(path, c) for c in commit_hashes]


def _get_name(obj: m.ModelObject) -> str:
    """Return the object's name.

    If the object doesn't own a name, its type is returned instead.
    """
    return getattr(obj, "name", None) or f"[{type(obj).__name__}]"


def compare_models(
    old: capellambse.MelodyModel,
    new: capellambse.MelodyModel,
):
    """Compare all elements in the given models."""
    changes = {}
    for layer in (
        "oa",
        "sa",
        "la",
        "pa",
    ):
        layer_old = getattr(old, layer)
        layer_new = getattr(new, layer)
        changes[layer] = compare_objects(layer_old, layer_new, old)
    return changes


def compare_objects(
    old_object: capellambse.ModelObject | None,
    new_object: capellambse.ModelObject,
    old_model: capellambse.MelodyModel,
):
    assert old_object is None or type(old_object) is type(
        new_object
    ), f"{type(old_object).__name__} != {type(new_object).__name__}"

    attributes: dict[str, ChangedAttribute] = {}
    children: dict[str, t.Any] = {}
    for attr in dir(type(new_object)):
        acc = getattr(type(new_object), attr, None)
        if isinstance(acc, m.BasePOD):
            _handle_pod(attr, old_object, new_object, attributes)
        elif isinstance(
            acc, m.AttrProxyAccessor | m.LinkAccessor | m.ParentAccessor
        ):
            _handle_accessors(attr, old_object, new_object, attributes)
        elif (
            # pylint: disable=unidiomatic-typecheck
            type(acc) is m.RoleTagAccessor
            or (type(acc) is m.DirectProxyAccessor and not acc.rootelem)
        ):
            _handle_direct_accessors(
                attr, old_object, new_object, children, old_model
            )

    if attributes or children or old_object is None:
        return {
            "display_name": _get_name(new_object),
            "uuid": getattr(new_object, "uuid", None),
            "change": "created" if old_object is None else "modified",
            "attributes": attributes,
            "children": children,
        }
    return {}


def _handle_pod(attr, old_object, new_object, attributes):
    if attr != "uuid":
        try:
            old_value = getattr(old_object, attr, None)
            new_value = getattr(new_object, attr, None)
            if old_value != new_value:
                attributes[attr] = {
                    "previous": _serialize_obj(old_value),
                    "current": _serialize_obj(new_value),
                }
        except Exception as e:
            print(f"Failed to process attribute '{attr}': {e}")
    else:
        pass


def _handle_accessors(attr, old_object, new_object, attributes):
    old_value = getattr(old_object, attr, None)
    new_value = getattr(new_object, attr, None)
    if isinstance(old_value, m.ModelElement | type(None)) and isinstance(
        new_value, m.ModelElement | type(None)
    ):
        if old_value is new_value is None:
            pass
        elif old_value is None:
            attributes[attr] = {
                "previous": None,
                "current": _serialize_obj(new_value),
            }
        elif new_value is None:
            attributes[attr] = {
                "previous": _serialize_obj(old_value),
                "current": None,
            }
        elif old_value.uuid != new_value.uuid:
            attributes[attr] = {
                "previous": _serialize_obj(old_value),
                "current": _serialize_obj(new_value),
            }
    elif isinstance(old_value, m.ElementList | type(None)) and isinstance(
        new_value, m.ElementList
    ):
        old_value = old_value or []
        if [i.uuid for i in old_value] != [i.uuid for i in new_value]:
            attributes[attr] = {
                "previous": _serialize_obj(old_value),
                "current": _serialize_obj(new_value),
            }
    else:
        raise RuntimeError(
            f"Type mismatched between new value and old value:"
            f" {type(old_value)} != {type(new_value)}"
        )


def _handle_direct_accessors(
    attr, old_object, new_object, children, old_model
):
    old_value = getattr(old_object, attr, None)
    new_value = getattr(new_object, attr, None)
    if isinstance(old_value, m.ModelElement | type(None)) and isinstance(
        new_value, m.ModelElement | type(None)
    ):
        if old_value is new_value is None:
            pass
        elif old_value is None:
            assert new_value is not None
            children[new_value.uuid] = compare_objects(
                None, new_value, old_model
            )
        elif new_value is None:
            children[old_value.uuid] = {
                "display_name": _get_name(old_value),
                "change": "deleted",
            }
        elif old_value.uuid == new_value.uuid:
            result = compare_objects(old_value, new_value, old_model)
            if result:
                children[new_value.uuid] = result
        else:
            children[old_value.uuid] = {
                "display_name": _get_name(old_value),
                "change": "deleted",
            }
            children[new_value.uuid] = compare_objects(
                None, new_value, old_model
            )
    elif isinstance(old_value, m.ElementList | type(None)) and isinstance(
        new_value, m.ElementList
    ):
        old_value = old_value or []
        for item in new_value:
            try:
                old_item = old_model.by_uuid(item.uuid)
            except KeyError:
                old_item = None
            if old_item is None:
                children[item.uuid] = compare_objects(None, item, old_model)
            else:
                result = compare_objects(old_item, item, old_model)
                if result:
                    children[item.uuid] = result

        for item in old_value:
            try:
                new_object._model.by_uuid(item.uuid)
            except KeyError:
                children[item.uuid] = {
                    "display_name": _get_name(item),
                    "change": "deleted",
                }


def _traverse_and_diff(data) -> dict[str, t.Any]:
    """Traverse the data and perform diff on text fields.

    This function recursively traverses the data and performs an HTML
    diff on every "name" and "description" field that has child keys
    "previous" and "current". The result is stored in a new child key
    "diff".
    """
    updates = {}
    for key, value in data.items():
        if (
            isinstance(value, dict)
            and "previous" in value
            and "current" in value
        ):
            curr_type = type(value["current"])
            if curr_type is str:
                diff = _diff_text(
                    (value["previous"] or "").splitlines(),
                    value["current"].splitlines(),
                )
                updates[key] = {"diff": diff}
            elif curr_type is dict:
                diff = _diff_objects(value["previous"], value["current"])
                updates[key] = {"diff": diff}
            elif curr_type is list:
                diff = _diff_lists(value["previous"], value["current"])
                updates[key] = {"diff": diff}
            elif key == "description":
                prev, curr = _diff_description(
                    (value["previous"] or "").splitlines(),
                    value["current"].splitlines(),
                )
                if prev is curr is None:
                    continue
                updates[key] = {"diff": ""}
                value.update({"previous": prev, "current": curr})
        elif isinstance(value, list):
            for item in value:
                _traverse_and_diff(item)
        elif isinstance(value, dict):
            _traverse_and_diff(value)
    for key, value in updates.items():
        data[key].update(value)
    return data


def _diff_text(previous, current) -> str:
    dmp = diff_match_patch.diff_match_patch()
    diff = dmp.diff_main("\n".join(previous), "\n".join(current))
    dmp.diff_cleanupSemantic(diff)
    return dmp.diff_prettyHtml(diff)


def _diff_objects(previous, current) -> str:
    return (
        f"<del>{previous['display_name']}</del> → " if previous else ""
    ) + f"<ins>{current['display_name']}</ins>"


def _diff_lists(previous, current):
    out = {}
    previous = {item["uuid"]: item for item in previous}
    for item in current:
        if item["uuid"] not in previous:
            out[item["uuid"]] = f"<ins>{item['display_name']}</ins>"
        elif item["uuid"] in previous:
            if item["display_name"] != previous[item["uuid"]]["display_name"]:
                out[item["uuid"]] = (
                    f"{_diff_objects(previous[item['uuid']], item)}"
                )
            else:
                out[item["uuid"]] = f"{item['display_name']}"
    current = {item["uuid"]: item for item in current}
    for uuid in previous:
        if uuid not in current:
            out[uuid] = f"<del>{previous[uuid]['display_name']}</del>"
    return out


def _diff_description(
    previous, current
) -> tuple[str, str] | tuple[None, None]:
    if previous is current is None:
        return None, None
    dmp = diff_match_patch.diff_match_patch()
    diff = dmp.diff_main("\n".join(previous), "\n".join(current))
    dmp.diff_cleanupSemantic(diff)
    previous_result = ""
    current_result = ""
    for operation, text in diff:
        if operation == 0:
            previous_result += text
            current_result += text
        elif operation == -1:
            previous_result += f"<del class='text-removed'>{text}</del>"
        elif operation == 1:
            current_result += f"<ins class='text-added'>{text}</ins>"
    return previous_result, current_result
