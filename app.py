from streamlit_echarts import st_echarts
from streamlit_echarts import JsCode
import streamlit as st
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta as rd
from deta import Deta
import os

st.set_page_config(layout="wide", page_title="Sarah's Calendar", page_icon="🎂")


def deta_conn():
    try:
        global db
        deta = Deta(os.environ['key'])
        db = deta.Base(os.environ['db'])

        print('deta_conn')

        return True

    except Exception as e:
        print('deta_conn err', e)


def make_charts():
    try:
        # df = table.copy()

        res = db.fetch()
        all_items = res.items

        while res.last:
            res = db.fetch(last=res.last)
            all_items += res.items

        df = pd.DataFrame(all_items)

        del df['entry_date']
        # del df['comment']
        df['day'] = df['due_date'].str[-2:]
        df['value'] = 1
        df = df[['due_date', 'day', 'value', 'reference', 'comment']]
        data = df.values.tolist()

        # cells = 30
        cells = "auto"

        option = {
                "tooltip": {"position": "top",
                            "formatter": JsCode("""function (params) {return params.value[0] + ' ' + params.value[3];}""").js_code},
                "calendar": [
                    {"top": 0, "range": date.today().strftime('%Y'), "cellSize": [cells, 30]},
                    {"top": 250, "range": (date.today() + rd(years=+1)).strftime('%Y'), "cellSize": [cells, 30]},
                ],
                "series": [
                    {
                        "type": "heatmap",
                        "coordinateSystem": "calendar",
                        "calendarIndex": 0,
                        "data": data,
                        "label": {
                            "show": True,
                            "formatter": JsCode("""function (params) {return params.value[1];}""").js_code
                        }
                    },
                    {
                        "type": "heatmap",
                        "coordinateSystem": "calendar",
                        "calendarIndex": 1,
                        "data": data,
                        "label": {
                            "show": True,
                            "formatter": JsCode("""function (params) {return params.value[1];}""").js_code
                        }
                    },
                ],
            }

        print('make_charts')

        return option

        # return st_echarts(option,
        #                   theme='light',
        #                   # width="1000px",
        #                   height="500px",
        #                   key="echarts",
        #                   events={"click": """function(params) {return  'Reference: ' + params.value[3] + '|Due Date: ' + params.value[0] + '|Comment: ' + params.value[4]}"""})

    except Exception as e:
        print('make_charts', e)


def make_table():
    try:
        res = db.fetch()
        all_items = res.items

        while res.last:
            res = db.fetch(last=res.last)
            all_items += res.items

        df = pd.DataFrame(all_items)
        del df['key']

        print('make_table')

        return df[['entry_date', 'reference', 'due_date', 'comment']].sort_values(by='entry_date', ascending=True)

    except Exception as e:
        print('make_table err', e)


def table_on_change():
    try:
        print('table_on_change')
        print(data_editor)
        # check = make_table()
        # print(check)
        # print(table == check)
    except Exception as e:
        print('table_on_change err', e)


def submit():
    try:
        db.put({'entry_date': entry_date, 'due_date': due_date, 'reference': reference, 'comment': comment})
        make_table()
        make_charts()

        print('submit')

    except Exception as e:
        print('submit err', e)


if deta_conn():
    st.title("Sarah's Calendar :blue[_(work-in-progress)_]")

    # table = make_table().copy()
    # table = make_table()

    with st.sidebar:
        reference = st.text_input("Reference", placeholder='Attila Janicsak')
        if reference:
            _date = date.today() + rd(months=+8)
            date_input = st.date_input(label="Due Date", value=_date, format="YYYY-MM-DD")
            comment = st.text_input('Comment')
            entry_date = date.today().strftime('%Y-%m-%d')
            due_date = date_input.strftime('%Y-%m-%d')
            due_day = date_input.strftime('%A')
            with st.expander("Summary", expanded=True):
                st.text(f"Entry Date: {entry_date}")
                st.text(f"Reference: {reference}")
                st.text(f"Due Date: {due_date}")
                st.text(f"Due Day: {due_day}")
                st.text(f"Comment: {comment}")

            if st.button('Submit', type='primary'):
                submit()

    tab1, tab2, tab3 = st.tabs(["Data Entry", "Data Table", "Dunno..."])

    with tab1:
        # charts = make_charts()
        charts = st_echarts(make_charts(),
                            theme='light',
                            height="500px",
                            key="echarts",
                            events={"click": """function(params) {return  'Reference: ' + params.value[3] + '|Due Date: ' + params.value[0] + '|Comment: ' + params.value[4]}"""})

        col1, col2 = st.columns(2)
        with col1:
            try:
                st.subheader(charts.replace('|', '\n\n\n'))
            except:
                st.subheader('...')
        with col2:
            if st.button('Delete Entry', type='primary'):
                ref = charts.split('|')[0].split(': ')[1]
                key = db.fetch({'reference': ref}).items[0].get('key')
                db.delete(key)

    with tab2:
        # data_editor = st.data_editor(table, hide_index=True, on_change=table_on_change)
        data_editor = st.data_editor(make_table(), hide_index=True, on_change=table_on_change)

    with tab3:
        st.header("A cat")
        st.image("https://static.streamlit.io/examples/cat.jpg", width=200)

