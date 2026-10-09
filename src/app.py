import streamlit as st
import pandas as pd
import sqlite3
import os
import json
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Paths
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
PROC_DIR = os.path.join(DATA_DIR, 'processed')
OUTPUTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'outputs'))
DB_PATH = os.path.join(PROC_DIR, 'db.sqlite')

st.set_page_config(page_title="Website User Behaviour Mining", layout="wide")
st.title("Website User Behaviour Mining")
st.markdown("**Student:** Himesh Bhure | B.Tech CSE | SIT, Nagpur | Batch 2024–2028 | Semester 5 | Section A")

tabs = st.tabs([
    "Overview & KDD", "Statistics & Attribute Relevance", "Classification",
    "Clustering", "Association Rules", "Web Content & Structure",
    "Funnel & Temporal", "Spatial Demo", "Coverage & Downloads"
])

# Utility to load data
@st.cache_data
def load_sessions():
    return pd.read_csv(os.path.join(PROC_DIR, 'sessions.csv'))

@st.cache_data
def load_events():
    return pd.read_csv(os.path.join(PROC_DIR, 'events_cleaned.csv'))

with tabs[0]:
    st.header("Overview & KDD Process")
    st.write("This dashboard presents the data mining process on the Retailrocket dataset.")
    st.write("### KDD Steps Implemented:")
    st.markdown("""
    - **Selection:** Filtering required item properties and relevant events.
    - **Cleaning:** Removing incomplete timestamps, deriving valid 30-min bounded sessions.
    - **Transformation:** Aggregating event-level data to session-level profiles.
    - **Data Mining:** Classification, Clustering, and Association rule mining.
    - **Evaluation:** Using F1-score, Silhouette, Confidence/Lift.
    - **Presentation:** This interactive Streamlit dashboard.
    """)
    if os.path.exists(os.path.join(PROC_DIR, 'sessions.csv')):
        df_sess = load_sessions()
        st.write("### Data Dictionary & Shape")
        st.write(f"Total sessions processed: {len(df_sess)}")
        st.dataframe(df_sess.head())

with tabs[1]:
    st.header("Concept Description & Statistics")
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        st.subheader("Aggregations via SQLite")
        # Purchase vs Non-Purchase
        query = '''
        SELECT has_purchase, COUNT(*) as session_count, 
               AVG(view_count) as avg_views, AVG(elapsed_duration) as avg_duration_sec
        FROM sessions GROUP BY has_purchase
        '''
        stat_df = pd.read_sql(query, conn)
        st.table(stat_df)
        
        st.subheader("Distributions")
        df_sess = load_sessions()
        fig = px.box(df_sess, x='has_purchase', y='view_count', title="View Count Distribution by Purchase Status")
        st.plotly_chart(fig)
        conn.close()

with tabs[2]:
    st.header("Classification")
    st.write("Predicting a purchase strictly AFTER the 3rd product view.")
    clf_res_path = os.path.join(OUTPUTS_DIR, 'clf_results.json')
    if os.path.exists(clf_res_path):
        with open(clf_res_path, 'r') as f:
            res = json.load(f)
        df_res = pd.DataFrame(res).T
        st.dataframe(df_res[['Accuracy', 'Precision', 'Recall', 'F1', 'ROC-AUC']])
        
        st.write("### Comparison")
        fig = px.bar(df_res.reset_index(), x='index', y='F1', title="F1 Score Comparison")
        st.plotly_chart(fig)

with tabs[3]:
    st.header("Clustering")
    st.write("Grouping sessions based on behavioural features.")
    clus_res_path = os.path.join(OUTPUTS_DIR, 'cluster_results.json')
    if os.path.exists(clus_res_path):
        with open(clus_res_path, 'r') as f:
            res = json.load(f)
        df_res = pd.DataFrame(res).T
        st.dataframe(df_res)
        
        st.write("### K-Means Clusters PCA Visualization")
        pca_path = os.path.join(OUTPUTS_DIR, 'kmeans_pca.csv')
        if os.path.exists(pca_path):
            pca_df = pd.read_csv(pca_path)
            fig = px.scatter(pca_df, x='PCA1', y='PCA2', color='Cluster', title="Cluster Scatter (PCA)")
            st.plotly_chart(fig)
            
        prof_path = os.path.join(OUTPUTS_DIR, 'cluster_profiles.csv')
        if os.path.exists(prof_path):
            st.write("### Cluster Centers (Profiles)")
            st.dataframe(pd.read_csv(prof_path))

with tabs[4]:
    st.header("Association Rules")
    st.write("Frequent itemsets of categories within sessions.")
    assoc_path = os.path.join(OUTPUTS_DIR, 'association_rules.csv')
    res_path = os.path.join(OUTPUTS_DIR, 'assoc_results.json')
    if os.path.exists(res_path):
        with open(res_path, 'r') as f:
            st.json(json.load(f))
            
    if os.path.exists(assoc_path):
        rules = pd.read_csv(assoc_path)
        st.write(f"Showing top 20 of {len(rules)} rules found.")
        st.dataframe(rules.sort_values('lift', ascending=False).head(20))
        fig = px.scatter(rules, x='support', y='confidence', color='lift', title="Support vs Confidence")
        st.plotly_chart(fig)

with tabs[5]:
    st.header("Web Content & Structure (Synthetic Demonstration)")
    st.write("Note: This uses a separate synthetic dataset to demonstrate syllabus concepts.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Web Content (TF-IDF & Cosine Similarity)")
        content_path = os.path.join(PROC_DIR, 'synth_content.csv')
        if os.path.exists(content_path):
            content = pd.read_csv(content_path)
            tfidf = TfidfVectorizer()
            mat = tfidf.fit_transform(content['text'])
            sim = cosine_similarity(mat)
            st.write("Cosine Similarity Matrix (Heatmap):")
            fig = px.imshow(sim, labels=dict(color="Similarity"))
            st.plotly_chart(fig)
            
    with col2:
        st.subheader("Web Structure (PageRank)")
        struct_path = os.path.join(PROC_DIR, 'synth_structure.csv')
        if os.path.exists(struct_path):
            edges = pd.read_csv(struct_path)
            G = nx.from_pandas_edgelist(edges, source='source', target='target', create_using=nx.DiGraph())
            pr = nx.pagerank(G)
            pr_df = pd.DataFrame(list(pr.items()), columns=['Page', 'PageRank']).sort_values('PageRank', ascending=False)
            st.dataframe(pr_df)
            
            fig, ax = plt.subplots()
            nx.draw(G, with_labels=True, node_color='lightblue', ax=ax)
            st.pyplot(fig)

with tabs[6]:
    st.header("Funnel & Temporal Analysis")
    if os.path.exists(os.path.join(PROC_DIR, 'events_cleaned.csv')):
        df_ev = load_events()
        
        st.subheader("Conversion Funnel")
        # Strict funnel: view -> addtocart -> transaction
        views = df_ev[df_ev['event']=='view']['session_uid'].nunique()
        carts = df_ev[(df_ev['event']=='addtocart') & (df_ev['session_uid'].isin(df_ev[df_ev['event']=='view']['session_uid']))]['session_uid'].nunique()
        # transactions from carts from views
        trans = df_ev[(df_ev['event']=='transaction') & (df_ev['session_uid'].isin(df_ev[(df_ev['event']=='addtocart')]['session_uid']))]['session_uid'].nunique()
        
        fig = go.Figure(go.Funnel(
            y=['Views', 'Add to Cart', 'Transaction'],
            x=[views, carts, trans]
        ))
        st.plotly_chart(fig)
        
        st.subheader("Temporal Trends (Daily)")
        df_ev['date'] = pd.to_datetime(df_ev['datetime']).dt.date
        daily = df_ev.groupby('date').size().reset_index(name='count')
        fig2 = px.line(daily, x='date', y='count', title='Daily Event Count')
        st.plotly_chart(fig2)

with tabs[7]:
    st.header("Spatial Demonstration (Synthetic)")
    st.write("Synthetic regional dataset for geographical insights demonstration.")
    spatial_path = os.path.join(PROC_DIR, 'synth_spatial.csv')
    if os.path.exists(spatial_path):
        spatial = pd.read_csv(spatial_path)
        fig = px.scatter_mapbox(spatial, lat="lat", lon="lon", size="visitors", color="region_id",
                                zoom=3, height=400, title="Visitors by Region")
        fig.update_layout(mapbox_style="carto-positron")
        st.plotly_chart(fig)

with tabs[8]:
    st.header("Syllabus Coverage & Downloads")
    st.write("### Matrix")
    st.markdown("""
    | Unit | Topic | Implementation | File/Location |
    |---|---|---|---|
    | 1 | KDD Process | Data prep pipeline, SQLite db | `src/data_processing.py` |
    | 2 | Concept Description | Aggregations, distributions | Streamlit App Tab 2 |
    | 3 | Classification | Naive Bayes, KNN, Tree | `src/modeling.py` |
    | 4 | Clustering & Assoc | K-Means, Agglom, FP-Growth | `src/modeling.py` |
    | 5 | Web Mining Apps | Usage, Content, Structure, Spatial | Streamlit App Tabs 6,7,8 |
    """)
