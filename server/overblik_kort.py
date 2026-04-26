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

# Liste over positionerne af pladerne på billedet
parking_lot_pos_x = [170,235, 300, 365, 430, 495, 560, 625, 690, 755, 100, 165, 230, 295, 360, 425, 490, 555]
parking_lot_pos_y = [375,375, 375, 375, 375, 375, 375, 375, 375, 375, 60, 60, 60, 60, 60, 60, 60, 60]

rect_width = 50
rect_height = 100

# Constants
img_width = 1600
img_height = 900
scale_factor = 0.5

# int som holder styr på loopet over pointer der bliver skabt
i=0

# Hvilke farver og beskrivelser pointerne kan have
colors = ["red","green","purple"]
color = colors[0]
statusser = ["Reserveret","Ikke reserveret","Kan ikke reserveres"]
status = statusser[0]

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


    fig.add_trace(go.Scatter(
        x=[parking_lot_pos_x[i]],
        y=[parking_lot_pos_y[i]],
        mode='markers',
        marker=dict(
           color=color,
        ),
        name=status,
        hoverinfo='name',
        showlegend=False
    ))
    fig.add_shape(
        type="rect",
        x0=parking_lot_pos_x[i] - rect_width/2,
        x1=parking_lot_pos_x[i] + rect_width/2,
        y0=parking_lot_pos_y[i] - rect_height/2,
        y1=parking_lot_pos_y[i] + rect_height/2,
        fillcolor=color,
        line=dict(color="white", width=.5),
        )

    i += 1

fig.show()

#fig.write_html("overblik_figur.html",include_plotlyjs='cdn')
