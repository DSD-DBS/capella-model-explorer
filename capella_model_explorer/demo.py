import capellambse
import pandas as pd
import streamlit as st
from jinja2.environment import Environment

env = Environment()


@st.cache_resource
def load_model() -> capellambse.MelodyModel:
    return capellambse.MelodyModel(
        path="automated-train",
        entrypoint="/automated-train.aird",
    )


model = load_model()

with st.sidebar:
    st.write("# Sidebar!")
    viewpoint = st.radio(
        "Viewpoint:", ["Capabilities", "Functions", "Interfaces"]
    )


if viewpoint == "Capabilities":
    with st.sidebar:
        sys_caps = model.sa.all_capabilities
        sys_caps_idx = {cap.name: cap for cap in sys_caps}
        selected_name = st.selectbox(
            "Select System Capability", options=sys_caps_idx.keys()
        )
    cap = sys_caps_idx[selected_name]
    st.write(f"# {cap.name}")

    st.write("## Description")
    st.write(cap.description, unsafe_allow_html=True)

    st.write("## Context Diagram")
    st.write(
        """\
        The image below provides an overview over the actors immediately
        involved in the Capability.
        """
    )
    st.image(cap.context_diagram.as_svg)

    st.write("## Required Functions")
    cap_real_entities = {
        entity.owner for entity in cap.involved_functions if entity.owner
    }
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

    st.dataframe(
        table.style.set_properties(**{"white-space": "pre-wrap"}),
        hide_index=True,
    )

elif viewpoint == "Functions":
    table_template = """
    To realize this capability the System and involved actors are required to perform the following functions:</p>
    <table>
    <tr>
        <th>Involved Entity</th><th>Required function</th>
    </tr>
    <tbody>
    {% for owner, fncs in cap.involved_functions | rejectattr("owner","none") | groupby("owner.name") %}
    <tr>
        <td>{{owner}}</td>
        <td>
        {% for fnc in fncs %}
        - {{fnc.name}}
        {% endfor %}
        </td>
    </tr>
    {% endfor %}
    </tbody>
    </table>
    """
    template = env.from_string(table_template)
    st.markdown(template.render(cap=obj), unsafe_allow_html=True)

    fncs = model.sa.all_functions

    st.write("# Functions")
    sys_fncs = {fnc.name: fnc for fnc in fncs}
    selected_fnc_name = st.selectbox(
        "Select Function", options=sys_fncs.keys()
    )
    fnc_obj = sys_fncs[selected_fnc_name]

    card = f"""{fnc_obj.context_diagram.as_svg}"""
    st.markdown(card, unsafe_allow_html=True)
