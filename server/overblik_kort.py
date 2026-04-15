from flask import Flask, render_template, request, redirect, session
import plotly.graph_objects as go
from PIL import Image
from jinja2 import Template
from database import init_db, get_db
from flask_app import blocked_spots

# Få database
init_db()
db = get_db()
spots = db.execute("""
                       SELECT *
                       FROM parking
                       ORDER BY id ASC
                       """).fetchall()


image = Image.open("static/Parkeringsplads.png")

# Create figure
fig = go.Figure()

# Constants
img_width = 1600
img_height = 900
scale_factor = 0.5

# Hvilke farver og beskrivelser pointerne kan have
colors = ["red","green","purple"]
color = colors[0]
statusser = ["Reserveret","Ikke reserveret","Kan ikke reserveres"]
status = statusser[0]

# int som holder styr på loopet over pointer der bliver skabt
i=0

# Add invisible scatter trace.
# This trace is added to help the autoresize logic work.
fig.add_trace(
    go.Scatter(
        x=[0, img_width * scale_factor],
        y=[0, img_height * scale_factor],
        mode="markers",
        marker_opacity=0,
        name="",
        hoverinfo='name',
        showlegend=False
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

# Der skabes et point for hver ledig parkeringsplads
for spot in spots:

    # De ikke reserverebare parkeringspladser får en anden farve og status
    for blocked_spot in blocked_spots:
        if i + 1 > len(spots)-len(blocked_spots):
            color = colors[2]
            status = statusser[2]
        else:
            color = colors[1]
            status = statusser[1]

    # Hvis punkterne går for langt ændres y, så de ikke går ud over billedet
    if 150 + (65 * i) > 750:
        fig.add_trace(go.Scatter(
            x=[(150 - 700 + (65 * i))],
            y=[50],
            mode='markers',
            marker=dict(
                color=color,
            ),
            name=status,
            hoverinfo='name',
            showlegend=False
        ))
    else:
        fig.add_trace(go.Scatter(
            x=[170 + (65 * i)],
            y=[375],
            mode='markers',
            marker=dict(
                color=color,
            ),
            name=status,
            hoverinfo='name',
            showlegend=False
        ))

    i += 1

fig.show()

#output_html_path=r"server/templates/overblik.html"
#input_template_path = r"server/templates"

#plotly_jinja_data = {"fig":fig.to_html(full_html=False)}

#with open(output_html_path, "w", encoding="utf-8") as output_file:
#    with open(input_template_path) as template_file:
#        j2_template = Template(template_file.read())
#        output_file.write(j2_template.render(plotly_jinja_data))

