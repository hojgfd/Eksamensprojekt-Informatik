import plotly.express as px
from PIL import Image
from jinja2 import Template

image = Image.open("Images/Overblik.jpg")

fig = px.scatter_geo(
    lat=[56.152880],
    lon=[10.190033],
    hover_name=["Denmark"],
    title="Specific Place on Map",
    scope="europe",
)
fig.add_layout_image(source=image)

fig.update_geos(
    scope="europe",
    projection_type="orthographic"
)

fig.show()

#output_html_path=r"server/templates/overblik.html"
#input_template_path = r"server/templates"

#plotly_jinja_data = {"fig":fig.to_html(full_html=False)}

#with open(output_html_path, "w", encoding="utf-8") as output_file:
#    with open(input_template_path) as template_file:
#        j2_template = Template(template_file.read())
#        output_file.write(j2_template.render(plotly_jinja_data))

