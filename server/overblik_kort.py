import plotly.graph_objects as go
import os
from datetime import date, timedelta
from PIL import Image
from jinja2 import Template
from database import init_db, get_db
from config import blocked_spots

def build_fig():
    # Få database
    init_db()
    db = get_db()

    spots = db.execute("""
                       SELECT *
                       FROM parking
                       ORDER BY id ASC
                       """).fetchall()

    #Get occupied_spots
    occupied_spots = []

    today = date.today()
    print(f"tomorrow: {date.today() + timedelta(days=1)}")
    for s in spots:
        print(dict(s))
        if dict(s).get("date") == str(date.today() + timedelta(days=1)):
            occupied_spots.append(dict(s))

    #Get background image
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    image = Image.open(os.path.join(BASE_DIR, "static", "Parkeringsplads.png"))

    # Create figure
    fig = go.Figure()

    # Liste over positionerne af pladerne på billedet
    parking_lot_pos_x = [170, 240, 310, 380, 450, 520, 590, 660, 730, 170, 240, 310, 380, 450, 520, 590, 660, 730]
    parking_lot_pos_y = [375, 375, 375, 375, 375, 375, 375, 375, 375, 65, 65, 65, 65, 65, 65, 65, 65, 65]

    #Size of rect
    rect_width = 50
    rect_height = 100

    # Constants
    img_width = 1600
    img_height = 900
    scale_factor = 0.5

    # int som holder styr på loopet over pointer der bliver skabt
    i = 0

    # Hvilke farver og beskrivelser pointerne kan have
    colors = ["red", "green", "purple"]
    color = colors[0]
    statusser = ["Reserveret", "Ikke reserveret", "Kan ikke reserveres"]
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
    # Before the loop, build a set of occupied spot IDs for fast lookup
    occupied_spot_ids = {s["id"] for s in occupied_spots}

    for spot in spots:
        spot_id = spot["id"]  # use the actual id from the db row

        if spot_id in blocked_spots:
            color = colors[2]
            status = statusser[2]
        elif spot_id in occupied_spot_ids:
            color = colors[0]
            status = statusser[0]
        else:
            color = colors[1]
            status = statusser[1]

        #if i + 1 > len(spots) - len(blocked_spots):
        #    color = colors[2]
        #    status = statusser[2]
        #elif i + 1 > len(spots) - len(blocked_spots) - len(occupied_spots):
        #    color = colors[0]
        #    status = statusser[0]
        #else:
        #    color = colors[1]
        #    status = statusser[1]

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
            x0=parking_lot_pos_x[i] - rect_width / 2,
            x1=parking_lot_pos_x[i] + rect_width / 2,
            y0=parking_lot_pos_y[i] - rect_height / 2,
            y1=parking_lot_pos_y[i] + rect_height / 2,
            fillcolor=color,
            line=dict(color="white", width=2),
        )

        i += 1

    # fig.show()

    return fig