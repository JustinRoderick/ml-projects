# -*- coding: utf-8 -*-
"""multi_variable_regression.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/github/JustinRoderick/ml-projects/blob/main/regressions/multi_variable_regression.ipynb

Justin Roderick<div>
CAP 4611<div>
5239523

# Homework 5

This homework asks you to perform various experiments with ensemble methods.

The dataset is the same real estate dataset we previously used from:

https://www.kaggle.com/datasets/mirbektoktogaraev/madrid-real-estate-market

You will write code and discussion into code and text cells in this notebook.

If a code block starts with TODO:, this means that you need to write something there.

There are also markdown blocks with questions. Write the answers to these questions in the specified locations.

Some code had been written for you to guide the project. Don't change the already written code.

## Grading
The points add up to 10. Extensive partial credit will be offered. Thus, make sure that you are at least attempting all problems.

Make sure to comment your code, such that the grader can understand what different components are doing or attempting to do.
"""

import numpy as np
import pandas as pd
import sklearn.linear_model
import sklearn.metrics
import sklearn.ensemble

"""# A. Setup.

In this project we are going to work in a multi-variable setting.

This time, there are 7 explanatory variables: ``sq_mt_built``, ``n_rooms``, ``n_bathrooms``, ``is_renewal_needed``, ``is_new_development`` and ``has_fitted_wardrobes``.

We will first create the training and test data while doing some minimal data cleaning.
"""

from google.colab import drive
drive.mount('/content/drive')

# Reading the CSV file
df = pd.read_csv('/content/drive/MyDrive/houses_Madrid.csv')
#print(f"The columns of the database {df.columns}")

xfields = ["sq_mt_built", "n_rooms", "n_bathrooms", "has_individual_heating", \
           "is_renewal_needed", "is_new_development", "has_fitted_wardrobes"]
yfield = ["buy_price"]
# print (xfields + yfield)
dfsel = df[xfields + yfield]
dfselnona = dfsel.dropna()
df_shuffled = dfselnona.sample(frac=1) # shuffle the rows
x = df_shuffled[xfields].to_numpy(dtype=np.float64)
y = df_shuffled[yfield].to_numpy(dtype=np.float64)
print(x.shape)
training_data_x = x[:8000]
training_data_y = y[:8000]
test_data_x = x[8000:]
test_data_y = y[8000:]
print(f"Training data is composed of {len(training_data_x)} samples.")
print(f"Test data is composed of {len(test_data_x)} samples.")

"""# B. Creating a linear regression multi-variable baseline.

In this section we make a linear regression predictor for the multi-variable case. We also check the performance of the resulting regressor, and print the error.

This part is had been done for you, such that the work does not depend on you importing parts from the previous projects.

You will need to adapt this for the other models.
"""

# training the linear regressor
regressor = sklearn.linear_model.LinearRegression()
regressor.fit(training_data_x, training_data_y)
# We will create the predictions yhat for every x from the training data. We will do this one at a time. This is not an efficient way to do it, but it allows you to write and debug functions that return a scalar number
yhats = []
for x in test_data_x:
    yhat = regressor.predict([x])
    yhats.append(yhat[0])

# Now, print some examples of the quality of the classifier
examples = [45, 67, 170, 189, 207]
for i in examples:
    x = test_data_x[i]
    y = test_data_y[i]
    yhat = regressor.predict([x])[0][0]
    print(f"House {i} with {x[0]} sqmt was sold for {y} euros, but our system predicted {yhat:.2f}")

# Now calculate the root mean square error on the resulting arrays
error = sklearn.metrics.mean_squared_error(yhats, test_data_y, squared=False)
print(f"The mean square error of the linear regression is {error:.2f} euro")

"""# P1: Random Forest using sklearn (5 points)

Use the RandomForestRegressor function from sklearn to predict the prices of the house. Print the resulting error and samples, similar to the way in Section B.

Experiment with the settings of the hyperparameters: n_estimators (try at least values 10, 25, 100, 200) and max_depth (try at least values 1, 2, 4, 8, 16 and None).

Retain the hyperparameter value that gives you the best result.


"""

from sklearn.ensemble import RandomForestRegressor

training_data_y = training_data_y.ravel()
test_data_y = test_data_y.ravel()

# Define hyperparameter settings to test with
n_estimators_list = [10, 25, 100, 200]
max_depth_list = [1, 2, 4, 8, 16, None]

best_error = float('inf')
best_params = {}

examples = [45, 67, 170, 189, 207]

# Iterate over hyperparameter settings
for n_estimators in n_estimators_list:
    for max_depth in max_depth_list:
        # Create and train the RandomForestRegressor
        model = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
        model.fit(training_data_x, training_data_y)

        # Predict on test data
        predictions = model.predict(test_data_x)

        # Calculate mean squared error
        mse = sklearn.metrics.mean_squared_error(predictions, test_data_y, squared=False)

        # Print results for those parameters
        print(f"n_estimators={n_estimators}, max_depth={max_depth}, MSE={mse}")

        # Print house prices for each set of parameters
        for i in examples:
          print(f"House {i} sold for {test_data_y[i]} euros, but Random Forest predicted it to sell for {predictions[i]} euros")
        print()

        # Check if this model has the best performance so far
        if mse < best_error:
            best_error = mse
            best_params = {'n_estimators': n_estimators, 'max_depth': max_depth}

# Print the best hyperparameters and it's error
print(f"Best hyperparameters: {best_params}")
print(f"Best MSE: {best_error}")

"""# Questions:
* Q: Do you find that Random Forest performs better than the previous approaches you implemented? Discuss.
* A: It seems that Random Forest does perform better than multi-variable linear regression because the MSE of Random Forest was less.
* Q: Explain the impact of the number of estimators and max tree depth hyperparameters on the accuracy. Which hyperparameter setting gives you the best value? Is this the same as the default settings in sklearn?
* A: Overall the MSE decreased as the number of estimators went up, but when max depth went up past 8 the MSE would increase. I found that the most accurate hyperparamaters were 200 estimators and a max depth of 8. These are not the default sklearn values of 100 and none.
* Q: Explain the impact of the hyperparameters on the training time.
* A: As the number of n estimators and depth increased so did the training time.

# P2: AdaBoost using sklearn (5 points)

Use the AdaBoost function from sklearn to predict the prices of the house. Print the resulting error and samples, similar to the way in Section B.

Experiment with the settings of the hyperparameters: loss (try "linear", "square" and "exponential) and learning_rate (try at least values 0.2, 0.5, 1 and 2)
"""

from sklearn.ensemble import AdaBoostRegressor
import time

# Define hyperparameter settings to test with
loss_list = ['linear', 'square', 'exponential']
learning_rate_list = [0.2, 0.5, 1, 2]

best_error = float('inf')
best_params = {}

examples = [45, 67, 170, 189, 207]

# Iterate over hyperparameter settings
for loss in loss_list:
    for learning_rate in learning_rate_list:

        start = time.time()
        # Create and train the AdaBoostRegressor
        model = AdaBoostRegressor(loss=loss, learning_rate=learning_rate, random_state=42)
        model.fit(training_data_x, training_data_y)

        # Predict on test data
        predictions = model.predict(test_data_x)

        # Calculate mean squared error
        mse = sklearn.metrics.mean_squared_error(predictions, test_data_y, squared=False)

        # Print results for those parameters
        print(f"loss={loss}, learning_rate={learning_rate}, MSE={mse}")

        # Print house prices for each set of parameters
        for i in examples:
            actual_price = test_data_y[i]
            predicted_price = predictions[i]
            print(f"House {i} sold for {actual_price} euros, but AdaBoost predicted it to sell for {predicted_price} euros")

        # Check if this model has the best performance so far
        if mse < best_error:
            best_error = mse
            best_params = {'loss': loss, 'learning_rate': learning_rate}
        end = time.time()
        print("The time of execution of these parameters was:", (end-start) * 10**3, "ms")
        print()

# Print the best hyperparameters and its error
print(f"Best hyperparameters: {best_params}")
print(f"Best MSE: {best_error}")

"""# Questions:
* Q: Do you find that Adaboost performs better than the previous approaches you implemented? Discuss.
* A: I found that Adaboost performed the worst compared to the other approaches as it had the highest MSE.
* Q: Explain the impact of the loss and the learning_rate hyperparameters on the accuracy. Which hyperparameter setting gives you the best value? Is this the same as the default settings in sklearn?
* A: The Linear loss function performed the best and the squared and exponential performed about the same. As the learning rate increased so did the error. The best parameters where linear with a lr of 0.2. These are almost the default values of sklearn which has linear and 1.0.
* Q: Explain the impact of the hyperparameters on the training time.
* A: As the learning rate increased the execution time decreased. It seems that overall the squared loss was faster.
"""