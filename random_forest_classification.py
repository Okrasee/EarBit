import socket  
import pandas as pd
import numpy as np
import sklearn
import random
import csv
import random
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, make_scorer 

# create a csv file that stores raw data
with open('collect_data.csv', 'w', newline='') as myfile:
   wr = csv.writer(myfile, quoting=csv.QUOTE_ALL) 
   wr.writerow(['timestamp', 'milisec', 'cam', 
                'gx1', 'gy1', 'gz1', 
                'gx2', 'gy2', 'gz2', 
                'gx3', 'gy3', 'gz3', 
                'gx4', 'gy4', 'gz4', 
                'gx5', 'gy5', 'gz5', 'prox'])
# create a csv file that stores the average of raw data for each five seconds         
with open('avg_data.csv', 'w', newline='') as myfile:
   wr = csv.writer(myfile, quoting=csv.QUOTE_ALL) 
   wr.writerow(['cam', 'gx1', 'gy1', 'gz1', 
                'gx2', 'gy2', 'gz2', 
                'gx3', 'gy3', 'gz3', 
                'gx4', 'gy4', 'gz4', 
                'gx5', 'gy5', 'gz5', 'prox'])    

# build a machine learning model
dataset = pd.read_csv("sensorData.csv")
dataset.head()
X = dataset.drop('pattern', axis = 1)
X = X.drop('time', axis = 1)
y = dataset['pattern']
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1)
# optimize hyperparameters in the random forest classification by gridSearchCV classifier
classifier = RandomForestClassifier(n_jobs = -1)
param_grid = {
  'n_estimators': [80, 100, 150, 200, 250], 
  'max_depth': [5, 10, 15, 20, 25, 30],
  'min_samples_split': [2, 5, 10, 15, 20, 25], 
  'max_features': [3, 5, 10, 15, 17], 
  'min_samples_leaf': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] 
}
# use accuracy_score as the metric
scorers = {'accuracy_score': make_scorer(accuracy_score)}
grid_search = GridSearchCV(classifier, param_grid, scoring = scorers, refit = 'accuracy_score', cv = 3, return_train_score = True, n_jobs = -1)
grid_search.fit(X_train.values, y_train.values)
y_pred = grid_search.predict(X_test.values)
print(accuracy_score(y_test, y_pred))
print('Best params for {}'.format('accuracy_score'))
print(grid_search.best_params_)
# plug in the optimized hyperparameters
classifier = RandomForestClassifier(n_estimators = 100, max_depth = 5, min_samples_split = 15, max_features = 5, min_samples_leaf = 7, oob_score = True, n_jobs = -1, random_state = 1)
classifier.fit(X_train, y_train)
y_predict = classifier.predict(X_test)
accuracy_score(y_test, y_predict)

# create a socket object 
s = socket.socket()
print("Socket successfully created")
# reserve a port on the laptop
port, msg = 7800, " "
# Next bind to the port 
s.bind(('', port))        
print("socket binded to %s" %(port)) 
# put the socket into listening mode 
s.listen(2)    
print("socket is listening") 
c, raddr = s.accept()
# 'data' is the raw data received from the phone
data = c.recv(1024).decode("utf-8")
features = data.split()
# turn the raw data into integers
features_int = list(map(int, features))
# split the timestamp into two parts
# e.g. timestamp = 12495 then the first column is 12 and the second column 495
# it helps locate the five-second chunk of data
features_int.insert(1, features_int[0] % 1000)
features_int[0] = features_int[0] // 1000
# write the raw data into the collect_data.csv file
with open('collect_data.csv', 'a', newline='') as myfile:
  wr = csv.writer(myfile, quoting=csv.QUOTE_ALL) 
  wr.writerow(features_int)
sec, flt = features_int[0], features_int[1]
# 'row' is the row that the five-second chunk of data should start from
# 'curr_row' is the row of the last added piece of data
row, curr_row = 1, 0
c.close() 
n = 1
index_lst = []
while True: 
   # Establish connection with client. 
   c, raddr = s.accept() 
   data = c.recv(1024).decode("utf-8")
   features = data.split()
   try: 
      features_int = list(map(int, features))
      # split the timestamp into two parts
      features_int.insert(1, features_int[0] % 1000)     
      features_int[0] = features_int[0] // 1000
      # a correct piece of data should have 18 fields, i.e. 17 features plus timestamp
      if (len(features) == 18):
         with open('collect_data.csv', 'a', newline='') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL) 
            wr.writerow(features_int)
            curr_sec, curr_flt = features_int[0], features_int[1]
            # increment 'curr_row' since one more line is added
            curr_row += 1
         dataset = pd.read_csv("collect_data.csv")
         # find the row that the next five-second chunk of data should start from
         # if the previous timestamp is 12.495 sec, the next timestamp should be 13.495 sec
         # find the row number of the data that has timestamp >= 13.495 sec
         # and store it in a list
         if ((dataset.iloc[len(dataset) - 1]['timestamp'] == dataset.iloc[len(dataset) - 1 - n]['timestamp'] + 1)):
            if dataset.iloc[len(dataset) - 1]['milisec'] >= flt:
               index_lst.append(len(dataset + 1))
               n = 1
            # if the data has timestamp < 13.495 sec, go to the next row
            else: n += 1
      if (curr_sec == sec + 5 and curr_flt >= flt):
         dataset = pd.read_csv("collect_data.csv") 
         # take out a five-second chunk of data
         curr_range = dataset.iloc[row + 1: curr_row + 3]
         # find the average value of each parameter
         avg_int = [curr_range['cam'][0], curr_range['gx1'].mean(), curr_range['gy1'].mean(), curr_range['gz1'].mean(),
                    curr_range['gx2'].mean(), curr_range['gy2'].mean(), curr_range['gz2'].mean(),
                    curr_range['gx3'].mean(), curr_range['gy3'].mean(), curr_range['gz3'].mean(),
                    curr_range['gx4'].mean(), curr_range['gy4'].mean(), curr_range['gz4'].mean(),
                    curr_range['gx5'].mean(), curr_range['gy5'].mean(), curr_range['gz5'].mean(), curr_range['prox'].mean()]
         # write the average into avg_data.csv file
         with open('avg_data.csv', 'a', newline='') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL) 
            wr.writerow(avg_int)
         test = pd.read_csv("avg_data.csv")
         length = len(test)
         recent = test.iloc[length - 1]
         # make a prediction based on the model
         # y_predict returns a list of outcome
         y_predict = classifier.predict(test[params])
         # y_pred is the last element in the outcome list
         y_pred = y_predict[len(y_predict) - 1]
         if (y_pred == 0): msg = "The user is chewing"
         elif (y_pred == 1): msg = "The user is walking"
         elif (y_pred == 2): msg = "The user is stationary"
         else: msg = "The user is talking"
         row = index_lst[0]
         index_lst.pop(0)
         sec += 1
         s1 = socket.socket() 
         # phone ip   
         s1.connect(('xxx.xxx.xxx.xxx', 8080))
         string = msg.encode('utf-8')
         # encode the message and send it back to the client
         s1.send(string)
         # Close the connection with the client 
         s1.close()
   except ValueError:
      print("")      
   c.close() 

