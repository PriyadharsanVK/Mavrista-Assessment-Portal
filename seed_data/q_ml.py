#!/usr/bin/env python3
"""Machine Learning MCQ questions – 65 questions (20 Easy, 30 Medium, 15 Hard)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from seed_data.common import make_mcq, insert_domain_questions

DOMAIN = "Machine Learning"

questions = [
    # ── EASY (20) ──────────────────────────────────────────────────
    make_mcq(
        "Which type of learning uses labeled data to train a model?",
        ["Unsupervised learning", "Supervised learning", "Reinforcement learning", "Semi-supervised learning"],
        "B", "Easy"),
    make_mcq(
        "K-Means is an example of which type of learning?",
        ["Supervised learning", "Reinforcement learning", "Unsupervised learning", "Transfer learning"],
        "C", "Easy"),
    make_mcq(
        "In reinforcement learning, what does an agent try to maximize?",
        ["Training loss", "Cumulative reward", "Number of features", "Bias"],
        "B", "Easy"),
    make_mcq(
        "What does MSE stand for in regression evaluation?",
        ["Maximum Squared Error", "Mean Squared Error", "Minimum Squared Error", "Median Squared Error"],
        "B", "Easy"),
    make_mcq(
        "Which activation function is used in logistic regression?",
        ["ReLU", "Tanh", "Sigmoid", "Softmax"],
        "C", "Easy"),
    make_mcq(
        "What is the primary goal of feature scaling?",
        ["Increase model complexity", "Bring features to a similar range", "Remove outliers", "Reduce the number of features"],
        "B", "Easy"),
    make_mcq(
        "Which metric represents the proportion of variance explained by a regression model?",
        ["MSE", "MAE", "R-squared", "Log-loss"],
        "C", "Easy"),
    make_mcq(
        "What does KNN stand for?",
        ["K-Nearest Neighbors", "K-Node Network", "Kernel Normalized Nodes", "K-Nominal Neighbors"],
        "A", "Easy"),
    make_mcq(
        "What is overfitting?",
        ["Model performs well on training data but poorly on unseen data",
         "Model performs poorly on both training and test data",
         "Model has too few parameters",
         "Model is too simple to capture patterns"],
        "A", "Easy"),
    make_mcq(
        "What does PCA stand for?",
        ["Primary Component Approach", "Principal Component Analysis", "Partial Cluster Analysis", "Predictive Correlation Algorithm"],
        "B", "Easy"),
    make_mcq(
        "Which algorithm builds an ensemble of decision trees using bootstrap samples?",
        ["K-Means", "Logistic Regression", "Random Forest", "Naive Bayes"],
        "C", "Easy"),
    make_mcq(
        "In a confusion matrix, what does a True Positive represent?",
        ["Correctly predicted negative instance", "Incorrectly predicted positive instance",
         "Correctly predicted positive instance", "Incorrectly predicted negative instance"],
        "C", "Easy"),
    make_mcq(
        "Which of the following is a supervised learning algorithm?",
        ["K-Means clustering", "PCA", "Linear Regression", "DBSCAN"],
        "C", "Easy"),
    make_mcq(
        "What is the purpose of cross-validation?",
        ["To increase training speed", "To estimate model performance on unseen data",
         "To reduce the number of features", "To tune the learning rate only"],
        "B", "Easy"),
    make_mcq(
        "What type of problem does logistic regression solve?",
        ["Regression", "Classification", "Clustering", "Dimensionality reduction"],
        "B", "Easy"),
    make_mcq(
        "Which loss function is commonly used in logistic regression?",
        ["Mean Squared Error", "Hinge Loss", "Cross-Entropy Loss", "Huber Loss"],
        "C", "Easy"),
    make_mcq(
        "Precision measures the proportion of true positives out of all:",
        ["Actual positives", "Predicted positives", "True negatives", "All samples"],
        "B", "Easy"),
    make_mcq(
        "What is the 'k' in K-Means clustering?",
        ["Number of features", "Number of clusters", "Number of iterations", "Number of samples"],
        "B", "Easy"),
    make_mcq(
        "Naive Bayes is called 'naive' because it assumes:",
        ["Features are dependent", "Features are conditionally independent given the class",
         "The dataset is small", "Only binary features are allowed"],
        "B", "Easy"),
    make_mcq(
        "Which scaling technique transforms features to have zero mean and unit variance?",
        ["Min-Max Scaling", "Standardization (Z-score)", "Log Transformation", "Robust Scaling"],
        "B", "Easy"),

    # ── MEDIUM (30) ────────────────────────────────────────────────
    make_mcq(
        "In linear regression, which assumption states that errors should have constant variance?",
        ["Multicollinearity", "Normality", "Homoscedasticity", "Independence"],
        "C", "Medium"),
    make_mcq(
        "What does the Gini impurity measure in a decision tree?",
        ["The depth of the tree", "The probability of misclassifying a randomly chosen element",
         "The number of leaf nodes", "The variance of the target variable"],
        "B", "Medium"),
    make_mcq(
        "In SVM, what is the purpose of the kernel trick?",
        ["To reduce training time", "To map data into a higher-dimensional space for linear separation",
         "To prune the decision boundary", "To normalize the features"],
        "B", "Medium"),
    make_mcq(
        "Which regularization technique adds the absolute value of coefficients as a penalty?",
        ["L2 (Ridge)", "L1 (Lasso)", "Elastic Net", "Dropout"],
        "B", "Medium"),
    make_mcq(
        "What is the bias-variance tradeoff?",
        ["Increasing bias always decreases variance and vice versa, requiring a balance",
         "Both bias and variance always increase together",
         "Bias only affects training error, variance only affects test error",
         "It only applies to neural networks"],
        "A", "Medium"),
    make_mcq(
        "In k-fold cross-validation with k=5, how many times is the model trained?",
        ["1", "4", "5", "10"],
        "C", "Medium"),
    make_mcq(
        "What is the F1 score?",
        ["The arithmetic mean of precision and recall",
         "The harmonic mean of precision and recall",
         "The geometric mean of accuracy and precision",
         "The weighted sum of all metrics"],
        "B", "Medium"),
    make_mcq(
        "The ROC curve plots which two metrics against each other?",
        ["Precision vs Recall", "True Positive Rate vs False Positive Rate",
         "Accuracy vs Loss", "Sensitivity vs Specificity"],
        "B", "Medium"),
    make_mcq(
        "What is the main difference between bagging and boosting?",
        ["Bagging trains models sequentially; boosting trains in parallel",
         "Bagging trains models in parallel on bootstrap samples; boosting trains sequentially focusing on errors",
         "Bagging uses only decision trees; boosting uses any algorithm",
         "There is no difference"],
        "B", "Medium"),
    make_mcq(
        "In gradient descent, what happens if the learning rate is too large?",
        ["The model converges faster to the optimal solution",
         "The algorithm may overshoot the minimum and diverge",
         "The weights are not updated",
         "Regularization is automatically applied"],
        "B", "Medium"),
    make_mcq(
        "Which variant of gradient descent updates weights after processing each individual sample?",
        ["Batch Gradient Descent", "Stochastic Gradient Descent (SGD)",
         "Mini-Batch Gradient Descent", "Adaptive Gradient Descent"],
        "B", "Medium"),
    make_mcq(
        "What does entropy measure in the context of decision trees?",
        ["The depth of the tree", "The impurity or randomness of a dataset",
         "The number of splits", "The accuracy of predictions"],
        "B", "Medium"),
    make_mcq(
        "L2 regularization (Ridge) adds which penalty to the loss function?",
        ["Sum of absolute values of weights", "Sum of squared weights",
         "Product of weights", "Maximum of all weights"],
        "B", "Medium"),
    make_mcq(
        "Which ensemble method combines multiple models by training each on the errors of the previous one?",
        ["Bagging", "Stacking", "Boosting", "Blending"],
        "C", "Medium"),
    make_mcq(
        "What is the purpose of pruning in decision trees?",
        ["To increase the depth of the tree",
         "To reduce overfitting by removing unnecessary branches",
         "To add more features", "To convert the tree into a forest"],
        "B", "Medium"),
    make_mcq(
        "In hierarchical clustering, what does a dendrogram represent?",
        ["Feature importance ranking",
         "The nested grouping of data points and the distances at which clusters merge",
         "The loss curve during training",
         "The decision boundary of the model"],
        "B", "Medium"),
    make_mcq(
        "PCA finds new axes (principal components) that maximize:",
        ["The classification accuracy", "The variance in the data",
         "The number of clusters", "The training speed"],
        "B", "Medium"),
    make_mcq(
        "Which of the following is NOT an assumption of linear regression?",
        ["Linearity between features and target",
         "Independence of errors",
         "Features must be categorical",
         "Homoscedasticity of residuals"],
        "C", "Medium"),
    make_mcq(
        "In a Random Forest, how is the final prediction typically made for classification?",
        ["Using the first tree's prediction",
         "Majority voting across all trees",
         "Weighted average of tree depths",
         "Using only the deepest tree"],
        "B", "Medium"),
    make_mcq(
        "What does the 'margin' refer to in Support Vector Machines?",
        ["The error rate of the model",
         "The distance between the decision boundary and the nearest data points of each class",
         "The number of support vectors",
         "The kernel function's output"],
        "B", "Medium"),
    make_mcq(
        "Which gradient descent optimizer uses both momentum and adaptive learning rates?",
        ["SGD with Momentum", "Adagrad", "Adam", "RMSprop"],
        "C", "Medium"),
    make_mcq(
        "Recall (Sensitivity) measures the proportion of true positives out of all:",
        ["Predicted positives", "Actual positives", "Predicted negatives", "Total predictions"],
        "B", "Medium"),
    make_mcq(
        "What type of clustering does DBSCAN perform?",
        ["Partitional clustering", "Hierarchical clustering",
         "Density-based clustering", "Spectral clustering"],
        "C", "Medium"),
    make_mcq(
        "Feature engineering involves:",
        ["Only removing features from the dataset",
         "Creating new features or transforming existing ones to improve model performance",
         "Automatically tuning hyperparameters",
         "Training multiple models simultaneously"],
        "B", "Medium"),
    make_mcq(
        "In XGBoost, what does the 'X' stand for?",
        ["Extra", "Extreme", "Extended", "External"],
        "B", "Medium"),
    make_mcq(
        "Which of the following is true about underfitting?",
        ["The model has low bias and high variance",
         "The model is too complex for the data",
         "The model has high bias and low variance",
         "The model perfectly memorizes the training data"],
        "C", "Medium"),
    make_mcq(
        "What is stacking in ensemble learning?",
        ["Training models on random subsets of data",
         "Using the predictions of base models as features for a meta-learner",
         "Sequentially correcting errors of previous models",
         "Averaging the predictions of all models"],
        "B", "Medium"),
    make_mcq(
        "Mini-batch gradient descent is a compromise between:",
        ["L1 and L2 regularization",
         "Batch gradient descent and stochastic gradient descent",
         "Decision trees and SVMs",
         "Supervised and unsupervised learning"],
        "B", "Medium"),
    make_mcq(
        "Which metric is most appropriate for highly imbalanced classification datasets?",
        ["Accuracy", "F1 Score", "R-squared", "Mean Absolute Error"],
        "B", "Medium"),
    make_mcq(
        "In Naive Bayes, the 'posterior probability' is calculated using:",
        ["Gradient descent", "Bayes' theorem", "Euclidean distance", "Information gain"],
        "B", "Medium"),

    # ── HARD (15) ──────────────────────────────────────────────────
    make_mcq(
        "In the context of SVM, the RBF kernel implicitly maps input data into what kind of space?",
        ["A lower-dimensional space", "A finite-dimensional polynomial space",
         "An infinite-dimensional feature space", "A binary feature space"],
        "C", "Hard"),
    make_mcq(
        "Which condition must hold for the Lasso (L1 regularization) to produce exactly sparse solutions?",
        ["The regularization parameter lambda must be zero",
         "The regularization parameter must be large enough to drive some coefficients to exactly zero",
         "All features must be orthogonal",
         "The number of samples must exceed the number of features by at least ten times"],
        "B", "Hard"),
    make_mcq(
        "In the bias-variance decomposition of expected prediction error, what is the irreducible error?",
        ["Error caused by model complexity",
         "Error due to the inherent noise in the data that no model can eliminate",
         "Error from using too few training samples",
         "Error caused by choosing the wrong algorithm"],
        "B", "Hard"),
    make_mcq(
        "When using XGBoost with the 'dart' booster, what technique is applied to prevent overfitting?",
        ["Gradient clipping", "Dropout of boosting rounds (random tree dropping)",
         "L1 regularization only", "Data augmentation"],
        "B", "Hard"),
    make_mcq(
        "In stratified k-fold cross-validation, what additional property is maintained compared to standard k-fold?",
        ["Each fold has the same number of features",
         "The class distribution in each fold matches the overall dataset",
         "Each fold uses a different random seed",
         "Each fold trains on a different algorithm"],
        "B", "Hard"),
    make_mcq(
        "Which of the following is a consequence of the curse of dimensionality for KNN?",
        ["Distances between points become increasingly uniform, degrading the algorithm's discriminative power",
         "KNN becomes faster in high dimensions",
         "The number of neighbors k must always be 1",
         "Feature scaling becomes unnecessary"],
        "A", "Hard"),
    make_mcq(
        "The kernel trick in SVM avoids explicitly computing the mapping φ(x) by instead computing:",
        ["The gradient of the loss function", "The inner product in the transformed space via a kernel function K(x, x')",
         "The eigenvalues of the data matrix", "The Euclidean distance between clusters"],
        "B", "Hard"),
    make_mcq(
        "In gradient boosting, the negative gradient of the loss function with respect to predictions serves as:",
        ["The learning rate", "Pseudo-residuals that the next weak learner fits",
         "The feature importance score", "The regularization parameter"],
        "B", "Hard"),
    make_mcq(
        "Which statement about Elastic Net regularization is correct?",
        ["It combines L1 and L2 penalties, controlled by a mixing parameter",
         "It is equivalent to L2 regularization with a different lambda",
         "It only works with logistic regression",
         "It eliminates the need for cross-validation"],
        "A", "Hard"),
    make_mcq(
        "When performing PCA, what mathematical operation is applied to the covariance matrix to find principal components?",
        ["Singular value decomposition or eigendecomposition",
         "Gradient descent optimization",
         "K-means clustering",
         "Fourier transform"],
        "A", "Hard"),
    make_mcq(
        "In the context of Random Forests, what does 'feature bagging' (random subspace method) accomplish?",
        ["Increases the correlation between trees",
         "Reduces the correlation between trees, thereby reducing variance of the ensemble",
         "Eliminates the need for bootstrapping",
         "Ensures every tree uses all available features"],
        "B", "Hard"),
    make_mcq(
        "AUC-ROC of 0.5 indicates that the classifier performs:",
        ["Perfectly on the dataset", "Equivalent to random guessing",
         "With 50% precision", "Better than most classifiers"],
        "B", "Hard"),
    make_mcq(
        "In Adagrad, the learning rate is adapted per-parameter by dividing by the square root of:",
        ["The current gradient value", "The sum of squared past gradients for that parameter",
         "The batch size", "The number of epochs completed"],
        "B", "Hard"),
    make_mcq(
        "Which of the following correctly describes the difference between hard and soft margin SVM?",
        ["Hard margin allows no misclassification and requires linearly separable data; soft margin allows some misclassification via slack variables",
         "Soft margin requires linearly separable data; hard margin does not",
         "Hard margin uses kernels; soft margin does not",
         "There is no practical difference between them"],
        "A", "Hard"),
    make_mcq(
        "In hierarchical agglomerative clustering, Ward's linkage criterion minimizes:",
        ["The maximum distance between clusters",
         "The total within-cluster variance (sum of squared deviations)",
         "The number of clusters",
         "The distance between cluster centroids only"],
        "B", "Hard"),
]

if __name__ == "__main__":
    insert_domain_questions(DOMAIN, questions)
