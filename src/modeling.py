import pandas as pd
import numpy as np
import os
import json
import time
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.cluster import KMeans, AgglomerativeClustering, MiniBatchKMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.decomposition import PCA
from mlxtend.frequent_patterns import apriori, fpgrowth, association_rules
import pickle

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
PROC_DIR = os.path.join(DATA_DIR, 'processed')
OUTPUTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'outputs'))

def run_classification(events_df, sessions_df):
    print("Running classification...")
    # Identify sessions with >= 3 views
    view_events = events_df[events_df['event'] == 'view']
    view_counts = view_events.groupby('session_uid').size()
    eligible_sessions = view_counts[view_counts >= 3].index

    # Get the timestamp of the 3rd view
    third_views = view_events[view_events['session_uid'].isin(eligible_sessions)].groupby('session_uid').nth(2)
    
    # Filter out sessions that had a purchase at or before the 3rd view
    # Join the third view timestamp
    cutoff_times = third_views[['timestamp']].rename(columns={'timestamp': 'cutoff_time'})
    events_with_cutoff = events_df.merge(cutoff_times, on='session_uid', how='inner')
    
    # Purchases before cutoff
    early_purchases = events_with_cutoff[(events_with_cutoff['event'] == 'transaction') & (events_with_cutoff['timestamp'] <= events_with_cutoff['cutoff_time'])]
    eligible_sessions = set(eligible_sessions) - set(early_purchases['session_uid'])
    
    events_with_cutoff = events_with_cutoff[events_with_cutoff['session_uid'].isin(eligible_sessions)]
    
    # Build features at cutoff
    pre_cutoff = events_with_cutoff[events_with_cutoff['timestamp'] <= events_with_cutoff['cutoff_time']]
    
    features = pre_cutoff.groupby('session_uid').agg(
        visitorid=('visitorid', 'first'),
        start_time=('timestamp', 'min'),
        cutoff_time=('cutoff_time', 'first'),
        view_count=('event', lambda x: (x == 'view').sum()),
        cart_count=('event', lambda x: (x == 'addtocart').sum()),
        unique_categories=('categoryid', 'nunique'),
    ).reset_index()
    
    features['elapsed_to_cutoff'] = (features['cutoff_time'] - features['start_time']) / 1000.0 # seconds
    
    # Target: Did they purchase strictly AFTER cutoff?
    post_cutoff = events_with_cutoff[events_with_cutoff['timestamp'] > events_with_cutoff['cutoff_time']]
    purchasers = post_cutoff[post_cutoff['event'] == 'transaction']['session_uid'].unique()
    features['target'] = features['session_uid'].isin(purchasers).astype(int)
    
    # If the dataset is too big, sample to avoid long wait
    if len(features) > 20000:
        features = features.sample(20000, random_state=42)
    
    X = features[['elapsed_to_cutoff', 'cart_count', 'unique_categories']]
    y = features['target']
    groups = features['visitorid']
    
    # Split by visitor
    gss = GroupShuffleSplit(n_splits=1, train_size=0.7, random_state=42)
    train_idx, test_idx = next(gss.split(X, y, groups))
    
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    models = {
        'Dummy': DummyClassifier(strategy='prior'),
        'Naive Bayes': GaussianNB(),
        'KNN': KNeighborsClassifier(n_neighbors=5),
        'Decision Tree': DecisionTreeClassifier(max_depth=5, random_state=42)
    }
    
    results = {}
    best_model = None
    best_f1 = -1
    
    for name, model in models.items():
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        try:
            y_prob = model.predict_proba(X_test_scaled)[:, 1]
            auc = roc_auc_score(y_test, y_prob)
        except:
            auc = np.nan
            
        f1 = f1_score(y_test, y_pred, zero_division=0)
        results[name] = {
            'Accuracy': accuracy_score(y_test, y_pred),
            'Precision': precision_score(y_test, y_pred, zero_division=0),
            'Recall': recall_score(y_test, y_pred, zero_division=0),
            'F1': f1,
            'ROC-AUC': auc,
            'Confusion Matrix': confusion_matrix(y_test, y_pred).tolist()
        }
        
        if f1 > best_f1 and name != 'Dummy':
            best_f1 = f1
            best_model = model
            
    with open(os.path.join(OUTPUTS_DIR, 'clf_results.json'), 'w') as f:
        json.dump(results, f, indent=4)
        
    with open(os.path.join(OUTPUTS_DIR, 'best_clf_model.pkl'), 'wb') as f:
        pickle.dump(best_model, f)
        
    with open(os.path.join(OUTPUTS_DIR, 'scaler.pkl'), 'wb') as f:
        pickle.dump(scaler, f)
        
    print("Classification done.")

def run_clustering(sessions_df):
    print("Running clustering...")
    features = sessions_df[['elapsed_duration', 'view_count', 'cart_count', 'unique_items', 'unique_categories']].copy()
    features = features.fillna(0)
    
    # Sample for clustering evaluation (hierarchical is O(N^2))
    if len(features) > 10000:
        sample_idx = np.random.choice(features.index, 10000, replace=False)
        X_sample = features.loc[sample_idx]
    else:
        X_sample = features
        
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_sample)
    
    models = {
        'K-Means': KMeans(n_clusters=3, n_init=10, random_state=42),
        'MiniBatchKMeans': MiniBatchKMeans(n_clusters=3, n_init=10, random_state=42),
        'Agglomerative': AgglomerativeClustering(n_clusters=3)
    }
    
    results = {}
    for name, model in models.items():
        start = time.time()
        labels = model.fit_predict(X_scaled)
        runtime = time.time() - start
        
        sil = silhouette_score(X_scaled, labels)
        db = davies_bouldin_score(X_scaled, labels)
        
        results[name] = {
            'Silhouette': float(sil),
            'Davies-Bouldin': float(db),
            'Runtime_s': float(runtime),
            'Cluster_Sizes': pd.Series(labels).value_counts().to_dict()
        }
        
        if name == 'K-Means':
            # Save PCA for k-means
            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(X_scaled)
            pca_df = pd.DataFrame(X_pca, columns=['PCA1', 'PCA2'])
            pca_df['Cluster'] = labels
            pca_df.to_csv(os.path.join(OUTPUTS_DIR, 'kmeans_pca.csv'), index=False)
            
            # Save centers
            centers = pd.DataFrame(scaler.inverse_transform(model.cluster_centers_), columns=features.columns)
            centers.to_csv(os.path.join(OUTPUTS_DIR, 'cluster_profiles.csv'), index=False)
            
    with open(os.path.join(OUTPUTS_DIR, 'cluster_results.json'), 'w') as f:
        json.dump(results, f, indent=4)
        
    print("Clustering done.")

def run_association(events_df):
    print("Running association rules...")
    # Baskets: session_uid -> list of categories
    # Drop rows without categoryid
    df_cat = events_df.dropna(subset=['categoryid'])
    
    # Sample sessions to avoid memory explosion (e.g. max 50000 sessions)
    sessions = df_cat['session_uid'].unique()
    if len(sessions) > 50000:
        np.random.seed(42)
        sessions = np.random.choice(sessions, 50000, replace=False)
        df_cat = df_cat[df_cat['session_uid'].isin(sessions)]
        
    baskets = df_cat.groupby('session_uid')['categoryid'].apply(lambda x: list(set(x))).reset_index()
    
    # Need boolean matrix for mlxtend
    from sklearn.preprocessing import MultiLabelBinarizer
    mlb = MultiLabelBinarizer()
    X = mlb.fit_transform(baskets['categoryid'])
    basket_df = pd.DataFrame(X, columns=mlb.classes_)
    
    # Apriori
    start = time.time()
    frequent_itemsets_ap = apriori(basket_df, min_support=0.01, use_colnames=True)
    time_ap = time.time() - start
    
    # FP-Growth
    start = time.time()
    frequent_itemsets_fp = fpgrowth(basket_df, min_support=0.01, use_colnames=True)
    time_fp = time.time() - start
    
    rules = association_rules(frequent_itemsets_fp, metric="confidence", min_threshold=0.1, num_itemsets=2)
    # Convert frozensets to lists for JSON
    rules['antecedents'] = rules['antecedents'].apply(list)
    rules['consequents'] = rules['consequents'].apply(list)
    
    rules.to_csv(os.path.join(OUTPUTS_DIR, 'association_rules.csv'), index=False)
    
    results = {
        'Apriori_Runtime_s': float(time_ap),
        'FPGrowth_Runtime_s': float(time_fp),
        'Num_Rules_Found': len(rules)
    }
    with open(os.path.join(OUTPUTS_DIR, 'assoc_results.json'), 'w') as f:
        json.dump(results, f, indent=4)
        
    print("Association done.")

def generate_synthetic_data():
    print("Generating synthetic data for web content, structure, spatial...")
    
    # Web Content
    content = pd.DataFrame({
        'page_id': range(1, 11),
        'text': ['sale cheap electronics', 'buy latest phone', 'electronics sale phone', 
                 'home appliances kitchen', 'kitchen blender sale', 'laptop deals electronics',
                 'fashion shoes latest', 'shoes buy', 'phone cases deals', 'blender kitchen appliances']
    })
    content.to_csv(os.path.join(PROC_DIR, 'synth_content.csv'), index=False)
    
    # Web Structure (Edges)
    edges = pd.DataFrame({
        'source': [1, 1, 2, 3, 4, 5, 2, 6, 7, 8],
        'target': [2, 3, 3, 1, 5, 4, 6, 9, 8, 7]
    })
    edges.to_csv(os.path.join(PROC_DIR, 'synth_structure.csv'), index=False)
    
    # Spatial
    spatial = pd.DataFrame({
        'region_id': ['North', 'South', 'East', 'West', 'Central'],
        'lat': [40.7, 34.0, 42.3, 37.7, 41.8],
        'lon': [-74.0, -84.3, -71.0, -122.4, -87.6],
        'visitors': [1500, 1200, 900, 2000, 1100]
    })
    spatial.to_csv(os.path.join(PROC_DIR, 'synth_spatial.csv'), index=False)

if __name__ == '__main__':
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    events = pd.read_csv(os.path.join(PROC_DIR, 'events_cleaned.csv'))
    sessions = pd.read_csv(os.path.join(PROC_DIR, 'sessions.csv'))
    
    run_classification(events, sessions)
    run_clustering(sessions)
    run_association(events)
    generate_synthetic_data()
