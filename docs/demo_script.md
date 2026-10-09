# Website User Behaviour Mining - Demo Script
*(Duration: ~5-7 minutes)*

**[0:00 - 1:00] Introduction & Setup**
"Hello everyone. My name is Himesh Bhure, and this is my project on Website User Behaviour Mining. The goal of this project is to apply the full Knowledge Discovery in Databases (KDD) process to raw e-commerce logs from the Retailrocket dataset. 
As you can see, I have built an interactive Streamlit dashboard that encapsulates all five units of our syllabus. Let's start with the first tab."

**[1:00 - 2:00] Tab 1 & 2: KDD Process & Concept Description**
*(Click 'Overview & KDD')*
"Here in the Overview, we see how the raw data—originally just isolated page views—was transformed into 'sessions'. I used a 30-minute inactivity threshold for this.
*(Click 'Statistics & Attribute Relevance')*
"In this tab, we demonstrate Concept Description. The data here is queried directly from a SQLite database via GROUP BY operations. You can see the statistical difference in the average view counts between sessions that resulted in a purchase versus those that didn't."

**[2:00 - 3:30] Tab 3 & 4: Classification & Clustering**
*(Click 'Classification')*
"For classification, I framed a realistic problem: Predicting if a user will buy something strictly after their 3rd product view. I trained Naive Bayes, KNN, and Decision Trees. Notice the F1-scores here—we use F1 because purchase events are highly imbalanced. The split was done by Visitor ID to prevent data leakage."
*(Click 'Clustering')*
"In the Clustering tab, we perform unsupervised learning on session features (excluding any purchase labels). Using K-Means and Agglomerative clustering, we found distinct user segments. This PCA scatter plot visualizes the clusters in 2D space."

**[3:30 - 4:30] Tab 5 & 6: Association Rules & Web Mining Apps**
*(Click 'Association Rules')*
"Here we used FP-Growth to find frequent category itemsets. We can see rules showing which categories are frequently viewed together, ranked by Lift, indicating strong cross-sell potential."
*(Click 'Web Content & Structure')*
"To cover all syllabus requirements, I also implemented demonstrations for Web Content and Web Structure using synthetic data. Here is a Cosine Similarity matrix for webpage text, and a PageRank calculation over a directed hyperlink graph."

**[4:30 - 5:30] Tab 7 & 8: Funnel & Spatial Analysis**
*(Click 'Funnel & Temporal')*
"Back to the real data, here is our Web Usage Funnel. You can clearly see the massive drop-off from Views to Add-to-Cart to Transaction. Below it, the daily temporal trends."
*(Click 'Spatial Demo')*
"And finally, a geographic hotspot demonstration using synthetic regional data, fulfilling the spatial mining requirement."

**[5:30 - 6:00] Conclusion**
"All components, from data cleaning scripts to the generated Word report and PowerPoint presentation, are included in the repository. The project successfully demonstrates the entire lifecycle of a data mining project. Thank you."
