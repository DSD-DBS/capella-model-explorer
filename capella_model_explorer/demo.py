import streamlit as st
import pandas as pd
from jinja2.environment import Environment

import capellambse

env = Environment()

model = capellambse.MelodyModel(
  path="automated-train",
  entrypoint="/automated-train.aird",
)

viewpoint = "capabilities"

with st.sidebar:
    st.write("# Sidebar!")
    viewpoint = st.selectbox("Viewpoint:", ["Capabilities", "Functions", "Interfaces"])


sys_caps = model.sa.all_capabilities

st.write("""
# Caps
""")
sys_caps_idx = {cap.name: cap for cap in sys_caps}
selected_name = st.selectbox("Select System Capability", options=sys_caps_idx.keys())

cap = sys_caps_idx[selected_name]

st.image(cap.context_diagram.as_svg)

cap_real_entities = set([entity.owner for entity in cap.involved_functions if entity.owner])
table = pd.DataFrame([
          {
            "name": obj.name, 
            "functions": "; ".join(["" + fnc.name for fnc in cap.involved_functions if fnc.owner == obj])
          } for obj in cap_real_entities
        ])

st.dataframe(table.style.set_properties(**{"white-space": "pre-wrap"}))

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

st.write("""
# Functions
""")
sys_fncs = {fnc.name: fnc for fnc in fncs}
selected_fnc_name = st.selectbox("Select Function", options=sys_fncs.keys())
fnc_obj = sys_fncs[selected_fnc_name]

card = f"""{fnc_obj.context_diagram.as_svg}"""
st.markdown(card, unsafe_allow_html=True)