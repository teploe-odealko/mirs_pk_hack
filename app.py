import dash_bootstrap_components as dbc
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.express as px
import json
from my_report import create_pdf

from dash.dependencies import Input, Output, State
from plotly import graph_objs as go
from plotly.graph_objs import *
from datetime import datetime as dt
from urllib.request import urlopen

# Read JSON
with open('deff.geojson') as fields:
    geojson = json.load(fields)
# Create DF
df = pd.DataFrame({'color' : [5], 'id' : [0]})
geojson_copy = geojson.copy()
# Dinar opishet)


mapbox_access_token = "pk.eyJ1IjoiYmVzdHdpc2hlczEyMyIsImEiOiJja2YwemgwdTcweXl3MnFvYzVtaDExNmlkIn0.yowUCKCjiCTFXWhe8nzQCA"


# @with_current
def coord_generator_func(geojson):
    for i in range(len(geojson["features"])):
        geojson_copy["features"] = [geojson["features"][i]]
        geojson_copy["features"][0]["id"] = 0
        yield (geojson_copy, geojson["features"][i]["geometry"]["coordinates"][0][0])

coord_generator = coord_generator_func(geojson)
geojson_new, coords = next(coord_generator)


lat = coords[1]
lon = coords[0]
# figure
# fig = px.choropleth_mapbox(df, geojson=geojson_new, locations='id', color='color',
#                        color_continuous_scale="Viridis",
#                        range_color=(0, 12),
#                        mapbox_style="carto-positron",
#                        zoom=15, center = {"lat": lat, "lon": lon},
#                        opacity=0.5)
# fig.update_layout(margin={"r":0, "t":0, "l":0, "b":0})
# print(geojson_new)

fig = go.Figure(go.Scattermapbox())

fig.update_layout(mapbox = {
        'accesstoken': mapbox_access_token,
        'style': "mapbox://styles/mapbox/satellite-v9",
        'center': { 'lon': lon, 'lat': lat},
        'zoom': 15, 'layers': [{
            'source': geojson_new,
            'type': "line", 'below': "traces", "color": "orange"}]},
    margin={"r":0, "t":0, "l":0, "b":0})


# fig = go.Figure(data=go.Choropleth(
#     locations=df['id'], # Spatial coordinates
#     z = df['color'].astype(float), # Data to be color-coded
#     # locationmode = 'USA-states', # set of locations match entries in `locations`
#     colorscale = 'Reds',
#     # center = {"lat": lat, "lon": lon}
#
#     # colorbar_title = "Millions USD",
# ))
# fig.update_geos(
#     center=dict(lon=lon, lat=lat),
#     # projection_rotation=dict(lon=30, lat=30, roll=30),
#     # lataxis_range=[-50,20], lonaxis_range=[0, 200]
# )

# fig.update_layout(
    # title_text = '2011 US Agriculture Exports by State',
    # geo_scope='usa', # limite map scope to USA
# )


app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)

"""Creating buttons"""
buttons = html.Div(
    className="button-3",
    children=[

        dbc.Button("Подтвердить", color="success", className="mr-3", id="accept"),
        dbc.Button("Отклонить", color="danger", className="mr-3", id="cancel"),
        dbc.Button("Забраковать", color="dark", className="mr-1", id="discard"),
        html.Div(id="hidden-div", style ={"display": "none"})
    ],
    style={"display": "flex", "justify-content": "center", "padding-left": "10px", "float": "center"},
)

"""Tooltips for buttons"""
tooltips = html.Div(
    [
        dbc.Tooltip(
            "Подтвердить нарушение, "
            "так как земля с/х назначения проросла древесными породами.",
            target="accept",
            placement="bottom",
            className="mx-2",
            style={"font-size": "15px"}
        ),
        dbc.Tooltip(
            "Отклонить нарушение, "
            "так как нарушения были недавно устранены.",
            target="cancel",
            placement="bottom",
            style={"font-size": "15px"}
        ),
        dbc.Tooltip(
            "Забраковать гипотезу, "
            "так как в качестве нарушения были распознаны с/х угодия.",
            target="discard",
            placement="bottom",
            style={"font-size": "15px"}
        )
    ]
)

"""Body of modal window"""
modal_row = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.Div("IMAGE", style={"text-align": "center", "margin": "5px", "color": "#1E1E1E",
                                                 "padding": "70px 25px", "background-color": "#d8d8d8"})),
                dbc.Col(html.Div(
                    children=[
                        html.P("Адрес : ###########"),
                        html.P("Владелец : ###########"),
                        html.P("Площадь : ###########"),
                        html.P("Кадастровый Номер  : ##:##:#######"),
                    ],
                )),
            ],
        ),
        dbc.Row(dbc.Col(html.Div(
            children=[

                dbc.Checklist(
                    options=[
                        {"label": "Создать отчет в формате PDF", "value": 1},
                        {"label": "Создать отчет в формате WORD", "value": 2}
                    ],
                    value=[],
                    id="PDF checklist-inline-input",
                    inline=True,
                ),
                html.P("..."),
            ],
            style={"display": "flex", "margin": "10px", "padding": "25px", }
        ))),
    ]
)

"""Model window for report"""
modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(f"Оформление отчета по полю №###", style={"background-color": "#1E1E1E", "color": "#d8d8d8"}),
                dbc.ModalBody(
                    html.Div([modal_row]),
                    style={"background-color": "#1E1E1E", "color": "#d8d8d8"}
                ),
                dbc.ModalFooter(
                    [
                        dbc.Button("Создать отчет", id="save-lg", className="ml-3", color="success"),
                        dbc.Button("Отмена", id="close-lg", className="ml-auto mr-3", color="danger"),
                    ],
                    style={"background-color": "#1E1E1E", "color": "#d8d8d8"}
                ),
            ],
            id="modal-lg",
            size="lg",
        ),
    ],

)


"""Toast"""
toast = dbc.Toast(
            "Отчет сохранен!",
            id="positioned-toast",
            header="Примечание",
            is_open=False,
            dismissable=True,
            icon="success",
            # top: 66 positions the toast below the navbar
            style={"position": "fixed", "top": 23, "right": 15, "width": 350, "font-size": "15px", "color": "#1E1E1E"},
        )

"""App body"""
row = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                # Column for user controls
                html.Div(
                    className="four columns div-user-controls",
                    children=[
                        html.H1("Заголовок"),
                        html.H3(id="counter_field"),
                        html.P("Адрес : ###########"),
                        html.P("Владелец : ###########"),
                        html.P("Площадь : ###########"),
                        html.P("Кадастровый Номер  : ##:##:#######"),
                        buttons,
                        tooltips,
                        html.P(id="total-rides"),
                        html.P(id="total-rides-selection"),
                        html.P(id="date-value"),
                    ],
                ),
                # Column for app graphs and plots
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    children=[
                        dcc.Graph(id="map-graph", figure=fig, config={"displaylogo": False}),
                    ],
                ),
            ],
        )
    ]
)




"""Final Layout"""
app.layout = html.Div(
    [row, modal, toast]
)

"""For modal window"""
def toggle_modal(n1, n2, n3, is_open):
    if n1 or n2 or n3:
        return not is_open
    return is_open

"""For modal window"""
app.callback(
    Output("modal-lg", "is_open"),
    [Input("accept", "n_clicks"), Input("close-lg", "n_clicks"), Input("save-lg", "n_clicks")],
    [State("modal-lg", "is_open")],
)(toggle_modal)


"""For Toast"""
@app.callback(
    Output("positioned-toast", "is_open"),
    [Input("save-lg", "n_clicks")],
)
def open_toast(n):
    if n:
        return True
    return False


counter = len(geojson["features"])
"""For modal window"""
@app.callback(
    Output("counter_field", "children"),
    [Input("cancel", "n_clicks")])
def display_counter(btn1):
    global counter
    hanged_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'cancel' in hanged_id:
        counter = counter - 1
        return "Осталось проверить : " + str(counter)
    return "Осталось проверить : " + str(counter)

@app.callback(Output("hidden-div", "children"),
              [Input('save-lg', 'n_clicks')])
def create_report(btn1):
    hanged_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'save-lg' in hanged_id:
        create_pdf()
    return "created"

# Обработчик кнопок
@app.callback(Output("map-graph", "figure"),
              [Input('accept', 'n_clicks'),
               Input('cancel', 'n_clicks'),
               Input('discard', 'n_clicks')],
               state=[State(component_id='map-graph', component_property='figure')])

def displayClick(btn1, btn2, btn3, fig):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'cancel' in changed_id:
        msg = 'Button 1 was most recently clicked'
        geojson_new, coords = next(coord_generator)
        lat = coords[1]
        lon = coords[0]
        if isinstance(lat, list):
            lon = lat[0]
            lat = lat[1]
        fig = go.Figure(go.Scattermapbox())
        print(lat, lon)
        fig.update_layout(mapbox = {

            'accesstoken': mapbox_access_token,
            'style': "mapbox://styles/mapbox/satellite-v9",
            'center': { 'lon': lon, 'lat': lat},
            'zoom': 15, 'layers': [{
                'source': geojson_new,
                'type': "line", 'below': "traces", "color": "orange"}]},
            margin={"r":0, "t":0, "l":0, "b":0})
    # fig.update_layout(zoom=13)
    # lat = coords[1]
    # lon = coords[0]
    # fig = px.choropleth_mapbox(df, geojson=geojson_new, locations='id', color='color',
    #                color_continuous_scale="Viridis",
    #                range_color=(0, 12),
    #                mapbox_style="carto-positron",
    #                zoom=15, center = {"lat": lat, "lon": lon},
    #                opacity=0.5)

    return(fig)


if __name__ == "__main__":
    app.run_server(debug=True, port=8888)
