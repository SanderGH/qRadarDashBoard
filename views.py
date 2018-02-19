from app import app
from flask import render_template
import offense_table_creator

@app.route('/')
@app.route('/index')
def index():
    #offenses = offense_table_creator.create_offense_table()
    sources  = offense_table_creator.create_source_table()

    events = offense_table_creator.get_log_sources_data()

    categories = []
    for event in events:
        if not (event.get('hour')) in categories:
            categories.append(event.get('hour'))

    categories = [str(int(s)+1) + ':00' for s in categories]
    series = offense_table_creator.highchartify_data(events)

    return render_template('index.html', sources=sources, offenses="[]",categories=categories, series=series)
