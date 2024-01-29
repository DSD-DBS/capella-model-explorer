# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import sys
import pathlib

import capellambse
import pandas as pd
import streamlit as st
from jinja2.environment import Environment

workspace_path = '~/workspace'

# Parse command-line arguments manually
for arg in sys.argv:
    if arg.startswith('--workspace='):
        workspace_path = arg.split('=')[1]
        break

WORKSPACE = pathlib.Path(workspace_path).expanduser()


env = Environment()


def red_text(text):
    st.write(
            f'<span style="color: red">{text}</span>',
            unsafe_allow_html=True,
        )


if "all_models" not in st.session_state:
    st.session_state["all_models"] = {
        i.name: i for i in WORKSPACE.rglob("*.aird")
    }

with st.sidebar:
    model_name = st.selectbox(
        "Select the Capella model",
        st.session_state["all_models"].keys(),
        index=None,
    )

if not model_name:
    st.stop()

if (
    "model_name" not in st.session_state
    or st.session_state["model_name"] != model_name
):
    all_models = st.session_state["all_models"]
    st.session_state.clear()
    st.session_state["all_models"] = all_models
    st.session_state["model"] = capellambse.MelodyModel(
        st.session_state["all_models"][model_name]
    )
    st.session_state["model_name"] = model_name
model = st.session_state["model"]
with st.sidebar:
    st.write(f"Loaded model {model.name!r}")

sys_caps = model.sa.all_capabilities
sys_caps_idx = {cap.name: cap for cap in sys_caps}

sys_fncs = model.sa.all_functions[1:]
sys_fncs_idx = {fnc.name: fnc for fnc in sys_fncs}

if "current_viewpoint" not in st.session_state:
    st.session_state["current_viewpoint"] = {}
if "current_object" not in st.session_state:
    st.session_state["current_object"] = {}


def jump_to(vp: str, name: str) -> None:
    st.session_state["current_viewpoint"] = {"index": viewpoints.index(vp)}
    if vp == "Capabilities":
        st.session_state["current_object"] = {
            "index": sys_caps.index(sys_caps_idx[name])
        }
    elif vp == "Functions":
        st.session_state["current_object"] = {
            "index": sys_fncs.index(sys_fncs_idx[name])
        }


with st.sidebar:
    st.write("# Sidebar!")
    viewpoints = ["Capabilities", "Functions", "Interfaces"]
    viewpoint = st.radio(
        "Viewpoint:",
        viewpoints,
        **st.session_state["current_viewpoint"],
    )
    st.session_state["current_viewpoint"] = {}


if viewpoint == "Capabilities":
    with st.sidebar:
        if not sys_caps_idx:
            st.write(
                '<span style="color: red">The model has no Capabilities.</span>',
                unsafe_allow_html=True,
            )
            st.stop()
        selected_name = st.selectbox(
            "Select System Capability",
            options=sys_caps_idx.keys(),
            **st.session_state["current_object"],
        )
        st.session_state["current_object"] = {}

    cap = sys_caps_idx[selected_name]
    st.write(f"# {cap.name}")

    st.write("## Description")
    st.write(cap.description, unsafe_allow_html=True)
    st.write("### Pre-condition")
    if cap.precondition:
        st.write(cap.precondition.specification)
    else:
        red_text("No pre-condition defined")

    st.write("### Post-condition")
    if cap.postcondition:
        st.write(cap.postcondition.specification)
    else:
        red_text("No post-condition defined")
    st.write(
        """\
        ## Context Diagram

        The diagram below provides an overview over the entities immediately
        involved in the Capability and related Capabilities.
        """
    )
    st.image(cap.context_diagram.as_svg)

    st.write(
        """\
        ## Data Flow Diagram
        
        The diagram below provides an overview of the System (green) and actor 
        (blue) functions that are required to realize the Capability.
        """)
    st.image(cap.data_flow_view.as_svg)

    st.write(
        """\
        ## Functional Requirements

        This section provides a summary of what functions are required from the
        System and the actors to enable the system Capability.
        """
    )

    cap_real_entities = {
        entity.owner for entity in cap.involved_functions if entity.owner
    }

    for entity in cap_real_entities:
        st.write(
            f"### {entity.name}\n"
            f"To enable the system Capability **{cap.name}**"
            f" the **{entity.name}** shall:"
        )
        for fnc in cap.involved_functions:
            if fnc.owner == entity:
                st.button(
                    fnc.name,
                    on_click=jump_to,
                    args=("Functions", fnc.name),
                )

    table = pd.DataFrame(
        [
            {
                "name": obj.name,
                "functions": "; ".join(
                    fnc.name
                    for fnc in cap.involved_functions
                    if fnc.owner == obj
                ),
            }
            for obj in cap_real_entities
        ]
    )

    # st.dataframe(
    #     table.style.set_properties(**{"white-space": "pre-wrap"}),
    #     hide_index=True,
    # )
    st.divider()
    st.write("# All the other attributes of the object")
    st.write(cap.__html__(), unsafe_allow_html=True)

elif viewpoint == "Functions":
    with st.sidebar:
        selected_name = st.selectbox(
            "Select System Function",
            options=sys_fncs_idx.keys(),
            **st.session_state["current_object"],
        )
        st.session_state["current_object"] = {}

    fnc = sys_fncs_idx[selected_name]
    st.write(f"# {fnc.name}")

    st.write("## Allocated component")
    if fnc.owner is not None:
        st.write(fnc.owner.name)
    else:
        st.write(
            '<span style="color: red">This function is not allocated to a component.</span>',
            unsafe_allow_html=True,
        )

    st.write("## Description")
    if fnc.description:
        st.write(fnc.description, unsafe_allow_html=True)
    else:
        st.write(
            '<span style="color: red">This function has no description.</span>',
            unsafe_allow_html=True,
        )

    st.write("## Context Diagram")
    st.write(
        """\
        The image below provides an overview over the actors immediately
        involved in the Function.
        """
    )
    st.image(fnc.context_diagram.as_svg)

    st.write(
        """\
        ## Involving Capabilities
        The following Capabilities require this function.
        """
    )

    has_caps = False
    for cap in model.search("Capability"):
        if fnc in cap.involved_functions:
            st.button(
                cap.name,
                on_click=jump_to,
                args=("Capabilities", cap.name),
            )
            has_caps = True
    if not has_caps:
        st.write(
            '<span style="color: red">This function is not involved in any Capability.</span>',
            unsafe_allow_html=True,
        )

    st.divider()
    st.write(fnc.__html__(), unsafe_allow_html=True)
