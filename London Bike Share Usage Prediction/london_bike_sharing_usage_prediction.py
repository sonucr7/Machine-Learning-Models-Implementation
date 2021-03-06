# -*- coding: utf-8 -*-
"""London Bike Sharing Usage Prediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1wIUO8OANRUnGesSflXVkiA1mjiRCxwsI
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline

data = pd.read_csv("london_merged.csv")

data

"""Metadata:
- "timestamp" - timestamp field for grouping the data
- "cnt" - the count of a new bike shares
- "t1" - real temperature in C
- "t2" - temperature in C "feels like"
- "hum" - humidity in percentage
- "windspeed" - wind speed in km/h
- "weathercode" - category of the weather
- "isholiday" - boolean field - 1 holiday / 0 non holiday
- "isweekend" - boolean field - 1 if the day is weekend
"season" - category field meteorological seasons: 0-spring ; 1-summer; 2-fall; 3-winter.

- "weather_code" category description:
1 = Clear ; mostly clear but have some values with haze/fog/patches of fog/ fog in vicinity 2 = scattered clouds / few clouds 3 = Broken clouds 4 = Cloudy 7 = Rain/ light Rain shower/ Light rain 10 = rain with thunderstorm 26 = snowfall 94 = Freezing Fog
"""

data.info()

data['weather_code'].value_counts()
#one hot encoding required

data['is_weekend'].value_counts()

data['is_holiday'].value_counts()

data.isna().sum()

"""## Preprocessing"""

def data_preparation(df):
  df = df.copy()

  #Handling the timestamp column. Extract month, day, and hour from it.
  df['timestamp'] = pd.to_datetime(df['timestamp']) #datetime object
  df['month'] = df['timestamp'].apply(lambda x: x.month) #extract month from datetime object
  df['day'] = df['timestamp'].apply(lambda x: x.day) #extract day from the datetime object
  df['hour'] = df['timestamp'].apply(lambda x: x.hour) #extract hour from the datetime object

  #Now we can drop the actual timestamp column
  df = df.drop("timestamp", axis=1)

  

  return df

X = data_preparation(data)

X

"""# Using PyCaret"""

!pip install pycaret

import pycaret.regression as pyr

pyr.setup(
    data = X,
    target = 'cnt',
    train_size = 0.7,
    normalize = True
)

pyr.compare_models()

best_model = pyr.create_model('lightgbm')

pyr.evaluate_model(best_model)

X

unseen_data = X.drop("cnt", axis=1)
unseen_data

result = pyr.predict_model(best_model, data=unseen_data)
print(result)

result.to_csv("prediction.csv")

"""# Using Sklearn's Pipeline"""

from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

def pipeline_data(df):
  df = df.copy()

  #Handling the timestamp column. Extract month, day, and hour from it.
  df['timestamp'] = pd.to_datetime(df['timestamp']) #datetime object
  df['month'] = df['timestamp'].apply(lambda x: x.month) #extract month from datetime object
  df['day'] = df['timestamp'].apply(lambda x: x.day) #extract day from the datetime object
  df['hour'] = df['timestamp'].apply(lambda x: x.hour) #extract hour from the datetime object

  #Now we can drop the actual timestamp column
  df = df.drop("timestamp", axis=1)

  #X and y
  X = df.drop("cnt", axis=1)
  y = df['cnt']

  #split
  X_train, X_test, y_train, y_test = train_test_split(X,y, train_size=0.7, shuffle=True, random_state=1)

  

  return X_train, X_test, y_train, y_test

X_train, X_test, y_train, y_test = pipeline_data(data)

X_train

y_train

"""## Building the Pipeline"""

nominal_transformer = Pipeline(steps=[
                                      ("onehot", OneHotEncoder(sparse=False))
])

preprocessor = ColumnTransformer(transformers=[
                                               ("nominal", nominal_transformer, ['weather_code'])
], remainder = 'passthrough')

model = Pipeline(steps=[
                        ('preprocessor', preprocessor),
                        ('regressor', RandomForestRegressor())
])

estimator = model.fit(X_train, y_train)

"""## Evaluation

# R-Square
"""

y_true = np.array(y_test)
print(y_true)
y_pred = estimator.predict(X_test)
print(y_pred)

print("Model R^2 Score: {:.4f}".format(r2_score(y_true, y_pred)))

"""## RMSE"""

print(np.mean((y_test - y_pred) ** 2))

rmse = np.sqrt(np.mean((y_test - y_pred) ** 2))
print("RMSE is:", rmse)