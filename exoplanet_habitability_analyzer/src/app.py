import os
import io
import json
from datetime import datetime

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from settings import MONGODB_URI, MONGODB_DB, TZ
from services.db import DB
from services.scoring import score_planet
from ui.theme import inject_css
from utils.io import load_csv

st.set_page_config(page_title='Exoplanet Habitability Analyzer', page_icon='🧪', layout='wide')
inject_css()

st.title('🧪 Exoplanet Habitability Analyzer — HZ • Teq • Score (0–100)')
st.caption('Python + Streamlit + MongoDB • Dark Fantasy Planetary Galaxy UI')

# Sidebar
with st.sidebar:
    st.header('⚙️ Settings')
    uri = st.text_input('MongoDB URI', value=MONGODB_URI)
    dbname = st.text_input('Database', value=MONGODB_DB)
    seed = st.button('🌟 Seed Demo Data')

# Connect DB
try:
    db = DB(uri, dbname)
    st.sidebar.success('✅ Connected to MongoDB')
except Exception as ex:
    db = None
    st.sidebar.error(f'Connection error: {ex}')

# Tabs
analyze_tab, explore_tab, details_tab, library_tab = st.tabs(['🧮 Analyze', '📊 Explore', '🔎 Details', '📚 Library'])

# ------------------ Analyze ------------------
with analyze_tab:
    st.subheader('Upload CSV or use Demo data')
    up = st.file_uploader('CSV file', type=['csv'])

    df = None
    if seed:
        p = os.path.join(os.path.dirname(__file__), '..', 'data', 'exoplanets_demo.csv')
        df = load_csv(p)
        st.success('Seeded demo dataset (4 planets).')
    elif up is not None:
        # save to temp
        bytes_data = up.read()
        tmp = io.BytesIO(bytes_data)
        df = load_csv(tmp)
        st.success(f'Loaded {len(df)} rows from CSV.')

    if df is not None and not df.empty:
        # Compute scores
        scored = []
        for _, row in df.iterrows():
            r = row.to_dict()
            s = score_planet(r)
            doc = {**r, **s}
            scored.append(doc)
        # Persist
        if db:
            db.upsert_planets(scored)
            st.success(f'Upserted {len(scored)} planets into MongoDB.')
        # Preview table
        view = pd.DataFrame(scored)
        cols = ['name','radius_Re','a_AU','S_earth','S_inner','S_outer','Teq_K','score','label']
        show = [c for c in cols if c in view.columns]
        st.dataframe(view[show].round(3), use_container_width=True)

# ------------------ Explore ------------------
with explore_tab:
    st.subheader('Filter & Visualize (from MongoDB)')
    if db:
        label = st.multiselect('Class label', ['Likely','Possible','Unlikely'], default=['Likely','Possible','Unlikely'])
        rmin, rmax = st.slider('Radius (Re)', 0.3, 3.0, (0.3, 3.0))
        smin, smax = st.slider('Score', 0, 100, (0, 100))
        query = {
            'label': {'$in': label},
            'radius_Re': {'$gte': float(rmin), '$lte': float(rmax)},
            'score': {'$gte': int(smin), '$lte': int(smax)}
        }
        docs = db.list_planets(query, limit=1000)
        if not docs:
            st.info('No data found. Use **Analyze** to insert planets.')
        else:
            edf = pd.DataFrame(docs)
            # Charts
            c1, c2 = st.columns(2)
            with c1:
                if {'S_earth','radius_Re'}.issubset(edf.columns):
                    fig = px.scatter(edf, x='S_earth', y='radius_Re', color='label', hover_name='name',
                                     labels={'S_earth':'Insolation (⊕)','radius_Re':'Radius (Re)'})
                    fig.update_layout(template='plotly_dark', height=420)
                    st.plotly_chart(fig, use_container_width=True)
            with c2:
                if {'Teq_K','radius_Re'}.issubset(edf.columns):
                    fig = px.scatter(edf, x='Teq_K', y='radius_Re', color='label', hover_name='name',
                                     labels={'Teq_K':'Teq (K)','radius_Re':'Radius (Re)'})
                    fig.update_layout(template='plotly_dark', height=420)
                    st.plotly_chart(fig, use_container_width=True)
            # Histogram
            if 'score' in edf.columns:
                fig = px.histogram(edf, x='score', nbins=20, color='label')
                fig.update_layout(template='plotly_dark', height=320)
                st.plotly_chart(fig, use_container_width=True)
            # Table
            st.dataframe(edf[['name','radius_Re','a_AU','S_earth','Teq_K','score','label']].round(3), use_container_width=True)

# ------------------ Details ------------------
with details_tab:
    st.subheader('Planet Details')
    if db:
        docs = db.list_planets({}, limit=1000)
        names = [d['name'] for d in docs]
        if not names:
            st.info('No planets yet. Insert via **Analyze**.')
        else:
            sel = st.selectbox('Choose planet', names)
            d = db.get(sel)
            if d:
                col1, col2 = st.columns([0.45, 0.55])
                with col1:
                    st.markdown(f"### {d.get('name')}")
                    st.markdown(f"**Class:** {d.get('label')}  |  **Score:** {d.get('score'):.1f}")
                    st.markdown(f"**Radius:** {d.get('radius_Re'):.2f} Re  |  **a:** {d.get('a_AU'):.3f} AU")
                    st.markdown(f"**S:** {d.get('S_earth'):.2f} ⊕  |  **Teq:** {d.get('Teq_K'):.1f} K")
                    if d.get('S_inner') and d.get('S_outer'):
                        st.caption(f"HZ bounds: inner {d['S_inner']:.2f} ⊕, outer {d['S_outer']:.2f} ⊕ (Kopparapu)")
                    st.caption('Note: scoring is heuristic for education, not a definitive habitability claim.')
                    # Favorites & notes
                    c3, c4 = st.columns(2)
                    if c3.button('⭐ Favorite'):
                        db.favorite(d['name'])
                        st.success('Added to favorites')
                    note = c4.text_input('Add a note')
                    if st.button('Save note') and note.strip():
                        db.add_note(d['name'], note.strip())
                        st.success('Note saved')
                    notes = db.list_notes(d['name'])
                    if notes:
                        st.markdown('**Your notes:**')
                        for n in notes:
                            st.markdown(f"- {n}")
                with col2:
                    # Radial gauge for score
                    val = d.get('score', 0)
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=val,
                        number={'suffix':"/100", 'font':{'color':'#e6ecff'}},
                        gauge={'axis':{'range':[0,100]},
                               'bar':{'color':'#9b59ff'},
                               'steps':[{'range':[0,40],'color':'#552244'},
                                        {'range':[40,70],'color':'#283a6b'},
                                        {'range':[70,100],'color':'#1f5f4a'}]},
                        title={'text':'Habitability Score','font':{'color':'#d9e1ff'}}
                    ))
                    fig.update_layout(template='plotly_dark', height=360)
                    st.plotly_chart(fig, use_container_width=True)

# ------------------ Library ------------------
with library_tab:
    st.subheader('Favorites')
    if db:
        favs = db.list_favorites()
        if not favs:
            st.info('No favorites yet.')
        else:
            st.write(', '.join(sorted(set(favs))))

st.caption('HZ bounds implemented per Kopparapu et al. (2013/2014). See README for references.')
