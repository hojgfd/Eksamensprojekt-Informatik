import plotly.graph_objects as go
from PIL import Image
from jinja2 import Template

image = Image.open("static/Overblik.jpg")

# Create figure
fig = go.Figure()

# Constants
img_width = 1600
img_height = 900
scale_factor = 0.5

# Add invisible scatter trace.
# This trace is added to help the autoresize logic work.
fig.add_trace(
    go.Scatter(
        x=[0, img_width * scale_factor],
        y=[0, img_height * scale_factor],
        mode="markers",
        marker_opacity=0
    )
)

# Configure axes
fig.update_xaxes(
    visible=False,
    range=[0, img_width * scale_factor]
)

fig.update_yaxes(
    visible=False,
    range=[0, img_height * scale_factor],
    # the scaleanchor attribute ensures that the aspect ratio stays constant
    scaleanchor="x"
)

# Add image
fig.add_layout_image(
    dict(
        x=0,
        sizex=img_width * scale_factor,
        y=img_height * scale_factor,
        sizey=img_height * scale_factor,
        xref="x",
        yref="y",
        opacity=1.0,
        layer="below",
        sizing="stretch",
        source=image)
)

fig.add_trace(go.Scatter(
    x=[100, 150, 200, 250],
    y=[300, 300, 300, 300],
    mode='markers',
    marker=dict(
        color='rgb(255,0,0)',
    ),
    name='Reserveret'
))

fig.add_trace(go.Scatter(
    x=[100, 150, 200, 250],
    y=[50, 50, 50, 50],
    mode='markers',
    marker=dict(
        color='rgb(255,0,255)',
    ),
    name='Kan Ikke Reserveres'
))

fig.show()

#output_html_path=r"server/templates/overblik.html"
#input_template_path = r"server/templates"

#plotly_jinja_data = {"fig":fig.to_html(full_html=False)}

#with open(output_html_path, "w", encoding="utf-8") as output_file:
#    with open(input_template_path) as template_file:
#        j2_template = Template(template_file.read())
#        output_file.write(j2_template.render(plotly_jinja_data))

