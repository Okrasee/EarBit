# EarBit
‘EarBit’ is an experimental wearable system that automatically monitors users’ eating activities. Within the system, the head-mounted proximity sensor collects data from a number of sensing modalities and send the data to a mobile application via Bluetooth. The mobile app then exchanges the raw data and outputs of a machine learning model with a server.

## Pipeline
![alt text](https://github.com/Okrasee/EarBit/blob/master/pipeline.png)

## Data Processing
A 5-second chunk of data is retrieved every second. The machine learning model would then make a prediction on the average. 

## Machine Learning Model
A `Random Forest Classifier` is trained based on 17 features which characterize jaw movement when chewing. Except the camera and position features, they are essentially 5 features computed for each axes of the gyroscopes placed on the ear and back. There are four possible activities: chewing, drinking, talking and stationary. In this research project, we consider chewing as an indication of eating. 
```
classifier = RandomForestClassifier(n_estimators = 100, max_depth = 5, min_samples_split = 15, max_features = 5, min_samples_leaf = 7, oob_score = True, n_jobs = -1, random_state = 1)
```
The hyperparameters are optimized through the implementation of a `gridSearchCV classifier`. 
```
grid_search = GridSearchCV(classifier, param_grid, scoring = scorers, refit = 'accuracy_score', cv = 3, return_train_score = True, n_jobs = -1)
```

## Future Step
The next step is to synchronize the app with the Calendar App on the phone such that each eating event will be logged at the time it takes place and the user could have a better understanding of his own diet by checking the time and frequency of his eating activities. 
