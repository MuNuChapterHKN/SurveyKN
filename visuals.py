# -*- coding: utf-8 -*-

import sys
import plotly.graph_objects as go

def draw_pie(question, values, config, date, area, textinfo):
    
    """
    Draws a pie chart

    Parameters
    ----------
    question : String
        Text of the question
    values : Pandas.Series
        The column of the working survey whose chart is to be made
    config : Dictionary
        The contents of the config.yml file as a Python dictionary
    date : String
        Just the survey id will do
    area : String
        This doesn't have to be a valid area, it's just here for the
        annotations of the charts. As you may have noticed the global
        pie chart passes "Associtazione" here
    textinfo : String
        The string for the textinfo field of the plotly graphs.
        For further information see plotly.graph_objects.Figure.update_traces
        in the plotly documentation.
        Could be "label+percent" or "value+percent" etc.

    Returns
    -------
    fig : plotly.graph_objects.Figure
        The corresponding pie chart

    """
    
    labels = []
    colors = []
    ordered_values = []
    
    answers = values.index
    
    # Creates the colors
    options = config['Available Choices']
    for answer in answers:
        if answer not in options:
            print(answer + " given to the question " + question + " is not"
                  "a valid answer, check the spelling, exiting...")
            sys.exit(1)
    
    for option in options:
        if option in answers:
            labels.append(options[option]["Label"])
            colors.append(options[option]["Hex"])
            ordered_values.append(values[option])
        
    pie_chart_style = config["Pie Chart Style"]
    annotation_list = [dict(text=area, x=0, y=1.07, font_size=17, showarrow=False), dict(text=date, x=0, y=1, font_size=17, showarrow=False)]
    
    fig = go.Figure( data=[ go.Pie( labels = labels, values = ordered_values ) ] )
    fig.update_traces( textinfo=textinfo, textfont_size=pie_chart_style["On Each Slice"]["Font"],
                          marker=dict( colors=colors, line=dict(color=pie_chart_style["Line Color"], width=pie_chart_style["Line Width"]) ) )
    
    fig.update_layout(
        title_text=question,
        annotations=annotation_list)
    
    return fig

def draw_stacked_bar(question, values, config, dates):
    
    """
    Draws a stacked bar graph for better comparison between different survey results.

    Parameters
    ----------
    question : String
        Text of the question
    values : List
        A list of Pandas.Series, they should be the relevant
        columns from the surveys that you want to compare in the
        bar chart
    config : Dictionary
        The contents of the config.yml file as a Python dictionary
    dates : List
        A list of the ids of the surveys whose results are being
        compared in the bar chart

    Returns
    -------
    fig : plotly.graph_objects.Figure
        The corresponding bar chart

    """
    
    
    options = config['Available Choices']
    
    present_answers = []
    for value_series in values:
        present_answers.extend(value_series.index)

    go_bars = []
    for option in options:
        if option in present_answers:
            counts = []
            for value_series in values:
                if option in value_series.index:
                    counts.append(value_series[option])
                else:
                    counts.append(0)
            
            go_bars.append( go.Bar( name=options[option]["Label"], x=dates, y=counts, marker_color=options[option]["Hex"] ) )
            
    fig = go.Figure(data=go_bars)
    # Change the bar mode
    fig.update_layout(title=question, barmode='stack')
    
    return fig
