
# app.layout = html.Div([
# html.Div(
#     html.H2(
#         children='Stocks Dashboard',
#         style={
#             'fontSize': 50,
#             'fontWeight': 150,
#             # 'borderRadius': '15px',
#             # 'overflow': 'hidden',
#             'font-family': ['Poppins', 'sans-serif'],
#             # 'backgroundColor': colors['background'],
#             'textAlign': 'center',
#             'color': ' #001731',
#         }
#     ),
#     className="pretty_container"),
# html.Div(children=[
#     dcc.Tabs(id="side_panel",   className='pretty_container',
#              children=[
#                  dcc.Tab(className="pretty_container", label="About",
#                          children=html.Div(className="plot_selection_panel pretty_container",
#                                            children=[
#                                                html.H4(
#                                                      "Author: Sergio Chairez"),
#                                                html.Hr(),
#                                                html.P(
#                                                    "I was inspired to make an OHLC chart...")
#                                            ],
#                                            style={'font-family': ['Poppins', 'sans-serif'],
#                                                   'fontWeight': 60, }),
#                          ),
#                  dcc.Tab(label="View", className="pretty_container",
#                          children=[html.Div(className="pretty_container", children=[
#                                html.H3("""Choose the company symbol""",
#                                        style={
#                                            # 'margin-right': '2em',
#                                            'fontWeight': 150,
#                                            'margin': 0,
#                                            'padding': ['0.5em', '5em'],
#                                            # 'borderRadius': '15px',
#                                            'overflow': 'auto',
#                                            'font-family': ['Poppins', 'sans-serif'],
#                                            'display':'inline-block',
#                                            # 'backgroundColor': colors['background'],
#                                            #    'textAlign': 'center',
#                                            'color': ' #001731', }),
#                                dcc.Dropdown(multi=False,
#                                             clearable=False,
#                                             style=dict(
#                                                 #   width='40%',
#                                                 #  verticalAlign="middle",
#                                                 display='inline-block',
#                                             ),
#                                             id='symbolDropdown',
#                                             className="horizontal_dropdowns",
#                                             options=dropdown_options,
#                                             value='AAPL'

#                                             )],
#                                #  ])

#                          ]),

#                          #  ],),

#                          #  ],

#                          # style=dict(display='flex', flexDirection='row',
#                          #            justifyContent='center'),
#                          style={'float': 'left', 'margin': 'auto',
#                                 'display': 'flex', },

#                          vertical=True,
#                          #  parent_style={'float': 'left'}
#                          ),
#                  html.Div(
#                       [
#                           dcc.Graph(id='main_graph')
#                       ],
#                      className='pretty_container eight columns',
#                      style={'float': 'right', 'margin': 'auto'}
#                  ),

#                  ]
# [

#     html.H3("""Choose the company symbol""",
#             style={
#                 # 'margin-right': '2em',
#                 'fontWeight': 150,
#                 'margin': 0,
#                 'padding': ['0.5em', '5em'],
#                 # 'borderRadius': '15px',
#                 'overflow': 'auto',
#                 'font-family': ['Poppins', 'sans-serif'],
#                 'display':'inline-block',
#                 # 'backgroundColor': colors['background'],
#                 #    'textAlign': 'center',
#                 'color': ' #001731', }),
#     dcc.Dropdown(multi=False,
#                  clearable=False,
#                  style=dict(
#                      #  width='40%',
#                      verticalAlign="middle",
#                      display='inline-block',
#                  ),
#                  id='symbolDropdown',
#                  className="horizontal_dropdowns",
#                  options=dropdown_options,
#                  value='AAPL'

#                  ),
# ],

# className="pretty_container"

),

    # html.Div(
    #     [
    #         dcc.Graph(id='main_graph')
    #     ],
    #     className='pretty_container eight columns',
    # ),


    # html.Div(children='Choose the company symbol below', style={
    #     'textAlign': 'center',
    #     'font-family': ['Poppins', 'sans-serif'],
    #     'fontWeight': 60,
    #     'fontSize': 25,
    #     'color': colors['text']
    # }),

    # html.Div(id='dd-output-container'),

    # ], id="mainContainer",
    # )
