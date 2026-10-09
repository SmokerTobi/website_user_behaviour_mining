# Website User Behaviour Mining - Viva Questions

1. **What is the main objective of this project?**
   *Answer:* To analyze e-commerce user behavior using the KDD process, predict purchases using classification, and discover patterns using clustering and association rules.
2. **What dataset did you use?**
   *Answer:* The Retailrocket e-commerce dataset from Kaggle, containing visitor events and item properties.
3. **What is KDD?**
   *Answer:* Knowledge Discovery in Databases. It involves Selection, Cleaning, Transformation, Data Mining, Evaluation, and Presentation.
4. **How did you handle the timestamps in the raw data?**
   *Answer:* They were in Unix milliseconds, so I parsed them into standard DateTime format.
5. **How did you define a "session"?**
   *Answer:* A session is a period of continuous activity. I grouped events by visitor ID and defined a new session if there was an inactivity gap of more than 30 minutes.
6. **Why did you use a 30-minute threshold for sessions?**
   *Answer:* It's an industry standard (e.g., used by Google Analytics) for web sessionization.
7. **What does the Concept Description unit cover?**
   *Answer:* It summarizes data properties through statistical measures (mean, median) and characterizes data distribution (e.g., view count differences between buyers and non-buyers).
8. **Why did you use SQLite?**
   *Answer:* To demonstrate database-level aggregations (GROUP BY) for data characterization and feature engineering efficiently.
9. **What classification task did you perform?**
   *Answer:* Predicting if a session will result in a purchase *after* the user's 3rd product view, using only data available up to that point.
10. **Why predict after the 3rd view?**
    *Answer:* To prevent data leakage. If we use the whole session, we already know if they bought. Predicting midway is a realistic real-time scenario.
11. **How did you prevent data leakage in the train/test split?**
    *Answer:* I used GroupShuffleSplit grouped by visitor ID so that a single visitor's sessions wouldn't appear in both the training and testing sets.
12. **Which classification models did you compare?**
    *Answer:* Naive Bayes, K-Nearest Neighbors (KNN), and Decision Trees, comparing them against a Dummy baseline.
13. **Why might Naive Bayes perform poorly compared to Decision Trees here?**
    *Answer:* Naive Bayes assumes feature independence, whereas web behavior features (like cart counts and unique categories) are often highly correlated.
14. **What evaluation metrics did you use for classification?**
    *Answer:* Accuracy, Precision, Recall, F1-score, and ROC-AUC.
15. **Why use F1-score over Accuracy?**
    *Answer:* Purchase events are rare (class imbalance), so Accuracy can be misleading. F1 balances Precision and Recall.
16. **What features did you use for clustering?**
    *Answer:* Elapsed duration, view count, cart count, unique items, and unique categories. I excluded purchase labels to do unsupervised learning.
17. **Which clustering algorithms did you implement?**
    *Answer:* K-Means, Agglomerative (Hierarchical), and MiniBatchKMeans.
18. **How did you evaluate the clusters?**
    *Answer:* Using the Silhouette score (measures cohesion/separation) and Davies-Bouldin index.
19. **What is PCA and why was it used?**
    *Answer:* Principal Component Analysis reduces dimensionality. I used it to visualize the multi-dimensional clusters in a 2D scatter plot.
20. **What are Association Rules?**
    *Answer:* They identify items that frequently occur together (e.g., "if category A is viewed, category B is also viewed").
21. **What algorithms were used for Association Rules?**
    *Answer:* Apriori and FP-Growth. FP-Growth is generally faster as it uses an FP-Tree instead of candidate generation.
22. **What do Support, Confidence, and Lift mean?**
    *Answer:* Support is frequency. Confidence is the likelihood of B given A. Lift measures the strength of the association compared to random chance.
23. **What is a Conversion Funnel?**
    *Answer:* A visualization of the user journey, e.g., tracking the drop-off from Views -> Add to Cart -> Transaction.
24. **How did you handle Web Content mining?**
    *Answer:* Using a synthetic dataset to calculate TF-IDF vectors and Cosine Similarity between page texts to find related content.
25. **How did you demonstrate Web Structure mining?**
    *Answer:* By creating a synthetic directed graph of web hyperlinks and applying the PageRank algorithm to find important nodes.
26. **Why did you use synthetic data for Spatial analysis?**
    *Answer:* The raw dataset lacked geographical attributes (like IP/Location), so a synthetic region dataset was used to demonstrate spatial visualization.
27. **What temporal trends did you analyze?**
    *Answer:* Daily and hourly patterns in event counts to identify peak activity periods.
28. **What was the role of Streamlit in this project?**
    *Answer:* It was used to build an interactive dashboard to present the data mining results, models, and visualizations dynamically.
29. **What is a limitation of your association rules?**
    *Answer:* Co-occurrence does not imply a causal navigation sequence; just because two categories are in the same session doesn't mean one led to the other.
30. **What is a potential future scope for this work?**
    *Answer:* Processing the data streams in real-time, or using Deep Learning (like RNNs/LSTMs) for better sequential pattern prediction.
