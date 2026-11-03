#!/usr/bin/env python3
"""Data Science - 65 MCQ questions (20 Easy, 30 Medium, 15 Hard)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from seed_data.common import make_mcq, insert_domain_questions

DOMAIN = "Data Science"

questions = [
    # ── EASY (20) ──────────────────────────────────────────────────────
    make_mcq(
        "In pandas, which method is used to combine two DataFrames based on a common column?",
        ["concat()", "merge()", "append()", "stack()"],
        "B", "Easy"),
    make_mcq(
        "What does the pandas `groupby()` method do?",
        ["Sorts the DataFrame by a column", "Splits data into groups based on a criterion and applies aggregate functions",
         "Merges two DataFrames", "Removes duplicate rows"],
        "B", "Easy"),
    make_mcq(
        "Which NumPy function creates an array of evenly spaced values within a given interval?",
        ["np.zeros()", "np.arange()", "np.ones()", "np.full()"],
        "B", "Easy"),
    make_mcq(
        "What is the default join type in pandas `merge()`?",
        ["Left join", "Right join", "Outer join", "Inner join"],
        "D", "Easy"),
    make_mcq(
        "Which pandas method is used to check for missing values in a DataFrame?",
        ["df.empty()", "df.isnull()", "df.missing()", "df.check_na()"],
        "B", "Easy"),
    make_mcq(
        "What does the `shape` attribute of a NumPy array return?",
        ["The data type of the array", "The number of elements in the array",
         "A tuple of the array's dimensions", "The memory size of the array"],
        "C", "Easy"),
    make_mcq(
        "Which method removes duplicate rows from a pandas DataFrame?",
        ["df.unique()", "df.drop_duplicates()", "df.remove_dups()", "df.distinct()"],
        "B", "Easy"),
    make_mcq(
        "What type of chart is best suited for showing the distribution of a single continuous variable?",
        ["Pie chart", "Histogram", "Scatter plot", "Bar chart"],
        "B", "Easy"),
    make_mcq(
        "In statistics, what does the mean represent?",
        ["The most frequently occurring value", "The middle value in a sorted dataset",
         "The arithmetic average of all values", "The range of the data"],
        "C", "Easy"),
    make_mcq(
        "Which pandas function is used to read a CSV file into a DataFrame?",
        ["pd.load_csv()", "pd.read_csv()", "pd.open_csv()", "pd.import_csv()"],
        "B", "Easy"),
    make_mcq(
        "What does EDA stand for in data science?",
        ["Extensive Data Arrangement", "Exploratory Data Analysis",
         "External Data Acquisition", "Estimated Data Accuracy"],
        "B", "Easy"),
    make_mcq(
        "Which library is commonly used for creating static visualizations in Python?",
        ["NumPy", "pandas", "matplotlib", "scikit-learn"],
        "C", "Easy"),
    make_mcq(
        "What is the median of the dataset [1, 3, 5, 7, 9]?",
        ["3", "5", "7", "4"],
        "B", "Easy"),
    make_mcq(
        "In a normal distribution, what percentage of data falls within one standard deviation of the mean?",
        ["50%", "68%", "95%", "99.7%"],
        "B", "Easy"),
    make_mcq(
        "Which pandas method fills missing values with a specified value?",
        ["df.replace_na()", "df.fillna()", "df.impute()", "df.fill()"],
        "B", "Easy"),
    make_mcq(
        "What does the term 'feature' refer to in a machine learning context?",
        ["The target variable to predict", "An input variable or column used for prediction",
         "A row of data", "The model's accuracy score"],
        "B", "Easy"),
    make_mcq(
        "Which plot type is best for visualizing the relationship between two continuous variables?",
        ["Bar chart", "Pie chart", "Scatter plot", "Box plot"],
        "C", "Easy"),
    make_mcq(
        "What does `df.describe()` return in pandas?",
        ["The first five rows of the DataFrame", "Summary statistics of numeric columns",
         "The data types of all columns", "The shape of the DataFrame"],
        "B", "Easy"),
    make_mcq(
        "In a box plot, what does the box represent?",
        ["The full range of the data", "The interquartile range (IQR) from Q1 to Q3",
         "One standard deviation from the mean", "The confidence interval"],
        "B", "Easy"),
    make_mcq(
        "Which of the following is a measure of central tendency?",
        ["Variance", "Standard deviation", "Median", "Range"],
        "C", "Easy"),

    # ── MEDIUM (30) ────────────────────────────────────────────────────
    make_mcq(
        "What is the purpose of the pandas `melt()` function?",
        ["To merge multiple DataFrames", "To convert wide-format data to long-format data",
         "To drop columns with missing values", "To aggregate data by groups"],
        "B", "Medium"),
    make_mcq(
        "Which pandas method transforms long-format data into a wide-format summary table?",
        ["df.stack()", "df.unstack()", "df.pivot_table()", "df.transpose()"],
        "C", "Medium"),
    make_mcq(
        "In NumPy broadcasting, what happens when you add a (3,1) array to a (1,4) array?",
        ["An error is raised", "The result is a (3,4) array", "The result is a (1,1) array", "The result is a (3,1) array"],
        "B", "Medium"),
    make_mcq(
        "What is the primary purpose of a correlation matrix in EDA?",
        ["To identify missing values", "To measure linear relationships between pairs of variables",
         "To reduce the dimensionality of data", "To perform hypothesis testing"],
        "B", "Medium"),
    make_mcq(
        "Which method is appropriate for handling outliers by limiting extreme values to a threshold?",
        ["Deletion", "Mean imputation", "Winsorization (capping)", "Log transformation"],
        "C", "Medium"),
    make_mcq(
        "What does a p-value less than 0.05 typically indicate in hypothesis testing?",
        ["The null hypothesis is proven true", "There is strong evidence to reject the null hypothesis",
         "The alternative hypothesis is proven false", "The sample size is too small"],
        "B", "Medium"),
    make_mcq(
        "In a t-test, what assumption is made about the underlying data?",
        ["The data must be categorical", "The data should be approximately normally distributed",
         "The data must have no outliers", "The sample size must exceed 1000"],
        "B", "Medium"),
    make_mcq(
        "What is the difference between `pd.merge()` with how='left' and how='inner'?",
        ["Left join keeps all rows from the left DataFrame; inner keeps only matching rows",
         "Left join keeps only matching rows; inner keeps all rows",
         "They produce identical results", "Left join removes duplicates; inner does not"],
        "A", "Medium"),
    make_mcq(
        "Which seaborn function creates a heatmap from a correlation matrix?",
        ["sns.barplot()", "sns.heatmap()", "sns.pairplot()", "sns.distplot()"],
        "B", "Medium"),
    make_mcq(
        "What is a Type I error in hypothesis testing?",
        ["Failing to reject a false null hypothesis", "Rejecting a true null hypothesis",
         "Using an incorrect test statistic", "Having a biased sample"],
        "B", "Medium"),
    make_mcq(
        "Which sampling method gives every member of the population an equal chance of selection?",
        ["Stratified sampling", "Convenience sampling", "Simple random sampling", "Quota sampling"],
        "C", "Medium"),
    make_mcq(
        "What does the chi-square test of independence evaluate?",
        ["Whether two continuous variables are correlated",
         "Whether there is a significant association between two categorical variables",
         "Whether the means of two groups differ", "Whether a dataset follows a normal distribution"],
        "B", "Medium"),
    make_mcq(
        "In a confidence interval of 95%, what does the '95%' represent?",
        ["95% of the data falls within the interval",
         "If the sampling were repeated many times, 95% of the intervals would contain the true parameter",
         "The probability that the null hypothesis is true",
         "The test has 95% power"],
        "B", "Medium"),
    make_mcq(
        "Which feature engineering technique converts a categorical variable into binary columns?",
        ["Label encoding", "One-hot encoding", "Standard scaling", "Min-max normalization"],
        "B", "Medium"),
    make_mcq(
        "What does PCA (Principal Component Analysis) primarily achieve?",
        ["Increases the number of features", "Reduces dimensionality while preserving maximum variance",
         "Performs classification", "Fills missing values"],
        "B", "Medium"),
    make_mcq(
        "In a time series, what does 'stationarity' mean?",
        ["The series has an upward trend", "The statistical properties of the series do not change over time",
         "The series has seasonal patterns", "The series has no missing values"],
        "B", "Medium"),
    make_mcq(
        "What is the purpose of an A/B test?",
        ["To compare the performance of two variants to determine which performs better",
         "To perform dimensionality reduction", "To test for normal distribution",
         "To calculate the median of a dataset"],
        "A", "Medium"),
    make_mcq(
        "Which statistical test is used to compare means across three or more groups?",
        ["t-test", "Chi-square test", "ANOVA", "Z-test"],
        "C", "Medium"),
    make_mcq(
        "What is the key difference between correlation and causation?",
        ["They are the same thing", "Correlation implies a direct cause-effect relationship",
         "Correlation measures the strength of association; causation implies one variable directly affects another",
         "Causation can exist without any correlation"],
        "C", "Medium"),
    make_mcq(
        "Which pandas method is used to apply a custom function to each element, row, or column of a DataFrame?",
        ["df.map()", "df.apply()", "df.transform()", "df.applymap()"],
        "B", "Medium"),
    make_mcq(
        "What does the seaborn `pairplot()` function display?",
        ["A single scatter plot of two variables",
         "Pairwise relationships across all numeric columns in a DataFrame",
         "A box plot for each variable", "A time series line chart"],
        "B", "Medium"),
    make_mcq(
        "In stratified sampling, what is the defining characteristic?",
        ["Samples are taken at regular intervals", "The population is divided into subgroups and samples are drawn from each",
         "Samples are taken from convenient locations", "All members of the population are surveyed"],
        "B", "Medium"),
    make_mcq(
        "What does the Interquartile Range (IQR) measure?",
        ["The range between the minimum and maximum", "The spread of the middle 50% of data",
         "The variance of the dataset", "The distance from the mean to the median"],
        "B", "Medium"),
    make_mcq(
        "Which distribution is appropriate for modeling the number of events in a fixed interval of time?",
        ["Normal distribution", "Binomial distribution", "Poisson distribution", "Uniform distribution"],
        "C", "Medium"),
    make_mcq(
        "What is the binomial distribution used to model?",
        ["Continuous measurements", "The number of successes in a fixed number of independent yes/no trials",
         "The time between events", "The rank of items"],
        "B", "Medium"),
    make_mcq(
        "What does `df.pivot_table(values='Sales', index='Region', columns='Year', aggfunc='sum')` produce?",
        ["A filtered DataFrame showing only sales data",
         "A summary table with Regions as rows, Years as columns, and summed Sales values",
         "A melted DataFrame in long format", "A DataFrame sorted by Sales"],
        "B", "Medium"),
    make_mcq(
        "In a normal distribution, approximately what percentage of data falls within two standard deviations of the mean?",
        ["68%", "90%", "95%", "99.7%"],
        "C", "Medium"),
    make_mcq(
        "Which method is commonly used to detect outliers using the IQR?",
        ["Values above the mean are outliers", "Values beyond 1.5 × IQR above Q3 or below Q1",
         "Values with z-score exactly 0", "Values that are missing"],
        "B", "Medium"),
    make_mcq(
        "What is the purpose of cross-validation in model selection?",
        ["To increase the training data size", "To evaluate model performance on unseen data by splitting data into folds",
         "To select features", "To scale the data"],
        "B", "Medium"),
    make_mcq(
        "Which of the following is NOT a component of a time series?",
        ["Trend", "Seasonality", "Noise", "Cardinality"],
        "D", "Medium"),

    # ── HARD (15) ──────────────────────────────────────────────────────
    make_mcq(
        "When performing a pandas `merge()` on DataFrames with overlapping non-key column names, what happens by default?",
        ["The overlapping columns are dropped", "Suffixes '_x' and '_y' are appended to distinguish them",
         "An error is raised", "The values from the right DataFrame overwrite the left"],
        "B", "Hard"),
    make_mcq(
        "In PCA, what do the eigenvalues of the covariance matrix represent?",
        ["The correlation between original features", "The amount of variance captured by each principal component",
         "The number of data points in each cluster", "The p-values of the features"],
        "B", "Hard"),
    make_mcq(
        "What is the curse of dimensionality?",
        ["Having too few features to train a model",
         "The phenomenon where the feature space becomes increasingly sparse as dimensions grow, degrading model performance",
         "When features are highly correlated", "When the dataset has too many rows"],
        "B", "Hard"),
    make_mcq(
        "In a two-sample t-test, what does the Welch's correction address?",
        ["Non-normal distributions", "Unequal variances between the two groups",
         "Small sample sizes", "Multiple comparisons"],
        "B", "Hard"),
    make_mcq(
        "What is the Bonferroni correction used for?",
        ["Normalizing skewed distributions",
         "Adjusting the significance level when performing multiple hypothesis tests to control family-wise error rate",
         "Calculating confidence intervals", "Reducing dimensionality"],
        "B", "Hard"),
    make_mcq(
        "In t-SNE dimensionality reduction, what key hyperparameter controls the balance between local and global structure?",
        ["Learning rate", "Perplexity", "Number of components", "Random state"],
        "B", "Hard"),
    make_mcq(
        "When is the Mann-Whitney U test preferred over an independent samples t-test?",
        ["When both samples are normally distributed", "When the data is ordinal or the normality assumption is violated",
         "When comparing more than two groups", "When the sample size exceeds 1000"],
        "B", "Hard"),
    make_mcq(
        "What does the Augmented Dickey-Fuller (ADF) test assess in time series analysis?",
        ["Seasonality", "Whether a time series is stationary (has a unit root)",
         "The trend direction", "Auto-correlation strength"],
        "B", "Hard"),
    make_mcq(
        "In an A/B test, what is 'statistical power'?",
        ["The probability of detecting a true effect when it exists",
         "The probability of a Type I error", "The sample size of the test",
         "The magnitude of the treatment effect"],
        "A", "Hard"),
    make_mcq(
        "Which technique addresses multicollinearity among features before regression modeling?",
        ["One-hot encoding", "Variance Inflation Factor (VIF) analysis followed by feature removal",
         "Label encoding", "Data augmentation"],
        "B", "Hard"),
    make_mcq(
        "What is the main limitation of PCA when applied to non-linear data?",
        ["PCA is too slow for large datasets",
         "PCA only captures linear relationships and may fail to uncover non-linear structure",
         "PCA requires labeled data", "PCA cannot handle more than 10 features"],
        "B", "Hard"),
    make_mcq(
        "In experiment design, what is a confounder?",
        ["A variable that is measured as the outcome",
         "An extraneous variable that is correlated with both the independent and dependent variable, distorting the true relationship",
         "The control group in an experiment", "A metric used to measure effect size"],
        "B", "Hard"),
    make_mcq(
        "What does the Kolmogorov-Smirnov test evaluate?",
        ["Whether two groups have equal means",
         "Whether a sample follows a specified distribution by comparing CDFs",
         "Whether two categorical variables are independent",
         "Whether a time series is stationary"],
        "B", "Hard"),
    make_mcq(
        "When using NumPy, what is the result of broadcasting a (256,256,3) array with a (3,) array in an arithmetic operation?",
        ["An error because shapes are incompatible", "A (256,256,3) array where the operation is applied element-wise along the last axis",
         "A (3,) array", "A (256,256,1) array"],
        "B", "Hard"),
    make_mcq(
        "In feature engineering, what is target encoding and what risk does it introduce?",
        ["Encoding features as integers; risk of losing ordinality",
         "Replacing categories with the mean of the target variable for that category; risk of data leakage and overfitting",
         "Scaling features to zero mean; risk of negative values",
         "Dropping low-variance features; risk of information loss"],
        "B", "Hard"),
]

if __name__ == "__main__":
    insert_domain_questions(DOMAIN, questions)
