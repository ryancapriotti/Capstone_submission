# -*- coding: utf-8 -*-
"""forecast_script

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-Z_g2m6peeJImzfHSodWlozQF_pF59ig
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import torch.utils.data as data
from datetime import date
from datetime import timedelta
from datetime import datetime
from scipy.stats import t
from google.colab import files

targets = pd.read_csv('https://data.ecoforecast.org/neon4cast-targets/aquatics/aquatics-targets.csv.gz')
targets = targets.dropna()
targetsTemp = targets[targets.variable == "temperature"]
targetsOxygen = targets[targets.variable == "oxygen"]
targetsChla = targets[targets.variable == "chla"]

# defineing all the function we will use

#this function will turn our data in to a tensor for our model to able to use
def convert_tensor(dataset, lb):
    X, y = [], []
    for i in range(len(dataset) - lb):
        X.append(dataset[i:i+lb])
        y.append(dataset[i+1:i+lb+1])
    return torch.tensor(X), torch.tensor(y)


# def the model
class WaterQmodel(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(input_size=1, hidden_size=10, num_layers=1, batch_first=True)
        self.linear = nn.Linear(10, 1)
    def forward(self, x):
        x, _ = self.lstm(x)
        x = self.linear(x)
        return x

#Train the data
def training(model,number_epochs):
  dataloads = torch.utils.data.DataLoader(torch.utils.data.TensorDataset(X_train, y_train), shuffle=True, batch_size=9)
  optimizer = optim.Adam(model.parameters())
  lossfn = nn.MSELoss()
  for epoch in range(number_epochs):
    model.train()
    for X_batch, y_batch in dataloads:
        y_pred = model(X_batch)
        loss = lossfn(y_pred, y_batch)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    model.eval()
    if epoch % 100 != 0:
        continue
    with torch.no_grad():
        y_pred = model(X_train)
        train_rmse = np.sqrt(lossfn(y_pred, y_train))
    print("Epoch %d: train RMSE %.4f" % (epoch, train_rmse))

# prediction 
def predict(timeseries, data , types = ('temperature','oxygen','chla'),site_id = ('BARC','CRAM','LIRO','PRLA','PRPO','SUGG','TOOK')):
  edate = datetime.strptime(data.iloc[-1, 0], "%Y-%m-%d").date()
  date_left = (today - edate).days
  number_of_days_to_pred = date_left + 30
  input_seq = torch.Tensor(timeseries)
  output = model(input_seq)
  j = 0
  i = -1
  pred = [0]*number_of_days_to_pred

  while i > -1*number_of_days_to_pred-1:
    pred[j] = output[i].item()
    i -= 1
    j += 1

  ref_date = today - timedelta(days = (today - edate).days)

  date_range = [0]*number_of_days_to_pred

  for i in range (number_of_days_to_pred):
    date = ref_date + timedelta(days = i+1)
    date_range[i] = date.strftime("%Y-%m-%d")
  variable = [types]*number_of_days_to_pred
  site_id = [site_id]*number_of_days_to_pred

  dat = {'datetime':date_range, 'site_id': site_id,'variable':variable, 'prediction':pred}
  dataf = pd.DataFrame(dat, columns = ['datetime', 'site_id','variable', 'prediction'])
  dataf = dataf.iloc[date_left:, :].reset_index(drop=True)
  dataf.insert(2, 'family', 'ensemble')
  return dataf

"""BARC - Temperature,Oxygen,Chla"""

targets_BARCO_Temp = targetsTemp[targetsTemp['site_id'].str.contains('BARC')]
data_targets_BARCO_Temp = targets_BARCO_Temp[['datetime', 'observation', 'site_id']]
data_targets_BARCO_Temp = data_targets_BARCO_Temp.sort_values('datetime')
data_targets_BARCO_Temp = data_targets_BARCO_Temp.reset_index(drop=True)
targets_BARCO_Temp = data_targets_BARCO_Temp[["observation"]].values.astype('float32')

X_train, y_train = convert_tensor(targets_BARCO_Temp, lb=14)
today =date.today()
model = WaterQmodel()

# Define the number of times to train the model
num_trainings = 3

# Initialize an DataFrame
results_df = pd.DataFrame()
for i in range(num_trainings):

    training(model,number_epochs=300)

    predictions = predict(targets_BARCO_Temp , data_targets_BARCO_Temp ,types = 'temperature' , site_id = 'BARC')
    predictions.insert(3, 'parameters', i+1)
    results_i = pd.DataFrame(predictions)
    if i == 0:
        results_df = results_i
    else:
        results_df = pd.concat([results_df,results_i], ignore_index=True)

BARC_Temp = results_df
BARC_Temp

targets_BARCO_Oxy = targetsOxygen[targetsOxygen['site_id'].str.contains('BARC')]
data_targets_BARCO_Oxy = targets_BARCO_Oxy[['datetime', 'observation', 'site_id']]
data_targets_BARCO_Oxy = data_targets_BARCO_Oxy.sort_values('datetime')
data_targets_BARCO_Oxy = data_targets_BARCO_Oxy.reset_index(drop=True)
targets_BARCO_Oxy = data_targets_BARCO_Oxy[["observation"]].values.astype('float32')

X_train, y_train = convert_tensor(targets_BARCO_Oxy, lb=14)
today =date.today()
model = WaterQmodel()

# Define the number of times to train the model
num_trainings = 3

# Initialize an DataFrame
results_df = pd.DataFrame()
for i in range(num_trainings):

    training(model,number_epochs=300)

    predictions = predict(targets_BARCO_Oxy , data_targets_BARCO_Oxy ,types = 'oxygen' , site_id = 'BARC')
    predictions.insert(3, 'parameters', i+1)
    results_i = pd.DataFrame(predictions)
    if i == 0:
        results_df = results_i
    else:
        results_df = pd.concat([results_df,results_i], ignore_index=True)

BARC_Oxy = results_df 
BARC_Oxy

targets_BARCO_Chla = targetsChla[targetsChla['site_id'].str.contains('BARC')]
data_targets_BARCO_Chla = targets_BARCO_Chla[['datetime', 'observation', 'site_id']]
data_targets_BARCO_Chla = data_targets_BARCO_Chla.sort_values('datetime')
data_targets_BARCO_Chla = data_targets_BARCO_Chla.reset_index(drop=True)
targets_BARCO_Chla = data_targets_BARCO_Chla[["observation"]].values.astype('float32')

X_train, y_train = convert_tensor(targets_BARCO_Chla, lb=14)
today =date.today()
model = WaterQmodel()

# Define the number of times to train the model
num_trainings = 3

# Initialize an DataFrame
results_df = pd.DataFrame()
for i in range(num_trainings):

    training(model,number_epochs=300)

    predictions = predict(targets_BARCO_Chla , data_targets_BARCO_Chla ,types = 'chla' , site_id = 'BARC')
    predictions.insert(3, 'parameters', i+1)
    results_i = pd.DataFrame(predictions)
    if i == 0:
        results_df = results_i
    else:
        results_df = pd.concat([results_df,results_i], ignore_index=True)

BARC_Chla = results_df 
BARC_Chla

# download as csv
BARC = pd.concat([BARC_Temp, BARC_Oxy, BARC_Chla], axis=0, ignore_index=True)
BARC.to_csv('BARC.csv', encoding = 'utf-8-sig') 
files.download('BARC.csv')

"""CRAM - Temperature, Oxygen, Chla

"""

targets_CRAM_Temp = targetsTemp[targetsTemp['site_id'].str.contains('CRAM')]
data_targets_CRAM_Temp = targets_CRAM_Temp[['datetime', 'observation', 'site_id']]
data_targets_CRAM_Temp = data_targets_CRAM_Temp.sort_values('datetime')
data_targets_CRAM_Temp = data_targets_CRAM_Temp.reset_index(drop=True)
targets_CRAM_Temp = data_targets_CRAM_Temp[["observation"]].values.astype('float32')

X_train, y_train = convert_tensor(targets_CRAM_Temp, lb=14)
today =date.today()
model = WaterQmodel()

# Define the number of times to train the model
num_trainings = 3

# Initialize an DataFrame
results_df = pd.DataFrame()
for i in range(num_trainings):

    training(model,number_epochs=300)

    predictions = predict(targets_CRAM_Temp , data_targets_CRAM_Temp ,types = 'temperature' , site_id = 'CRAM')
    predictions.insert(3, 'parameters', i+1)
    results_i = pd.DataFrame(predictions)
    if i == 0:
        results_df = results_i
    else:
        results_df = pd.concat([results_df,results_i], ignore_index=True)

CRAM_Temp = results_df
CRAM_Temp

targets_CRAM_Oxy = targetsOxygen[targetsOxygen['site_id'].str.contains('CRAM')]
data_targets_CRAM_Oxy = targets_CRAM_Oxy[['datetime', 'observation', 'site_id']]
data_targets_CRAM_Oxy = data_targets_CRAM_Oxy.sort_values('datetime')
data_targets_CRAM_Oxy = data_targets_CRAM_Oxy.reset_index(drop=True)
targets_CRAM_Oxy = data_targets_CRAM_Oxy[["observation"]].values.astype('float32')

X_train, y_train = convert_tensor(targets_CRAM_Oxy, lb=14)
today =date.today()
model = WaterQmodel()

# Define the number of times to train the model
num_trainings = 3

# Initialize an DataFrame
results_df = pd.DataFrame()
for i in range(num_trainings):

    training(model,number_epochs=300)

    predictions = predict(targets_CRAM_Oxy , data_targets_CRAM_Oxy ,types = 'oxygen' , site_id = 'CRAM')
    predictions.insert(3, 'parameters', i+1)
    results_i = pd.DataFrame(predictions)
    if i == 0:
        results_df = results_i
    else:
        results_df = pd.concat([results_df,results_i], ignore_index=True)

CRAM_Oxy = results_df 
CRAM_Oxy

targets_CRAM_Chla = targetsChla[targetsChla['site_id'].str.contains('CRAM')]
data_targets_CRAM_Chla = targets_CRAM_Chla[['datetime', 'observation', 'site_id']]
data_targets_CRAM_Chla = data_targets_CRAM_Chla.sort_values('datetime')
data_targets_CRAM_Chla = data_targets_CRAM_Chla.reset_index(drop=True)
targets_CRAM_Chla = data_targets_CRAM_Chla[["observation"]].values.astype('float32')

X_train, y_train = convert_tensor(targets_CRAM_Chla, lb=14)
today =date.today()
model = WaterQmodel()

# Define the number of times to train the model
num_trainings = 3

# Initialize an DataFrame
results_df = pd.DataFrame()
for i in range(num_trainings):

    training(model,number_epochs=300)

    predictions = predict(targets_CRAM_Chla , data_targets_CRAM_Chla ,types = 'chla' , site_id = 'CRAM')
    predictions.insert(3, 'parameters', i+1)
    results_i = pd.DataFrame(predictions)
    if i == 0:
        results_df = results_i
    else:
        results_df = pd.concat([results_df,results_i], ignore_index=True)

CRAM_Chla = results_df 
CRAM_Chla

# download as csv
CRAM = pd.concat([CRAM_Temp, CRAM_Oxy, CRAM_Chla], axis=0, ignore_index=True)
CRAM.to_csv('CRAM.csv', encoding = 'utf-8-sig') 
files.download('CRAM.csv')

"""LIRO - Temperature,Oxygen,Chla"""

targets_LIRO_Temp = targetsTemp[targetsTemp['site_id'].str.contains('LIRO')]
data_targets_LIRO_Temp = targets_LIRO_Temp[['datetime', 'observation', 'site_id']]
data_targets_LIRO_Temp = data_targets_LIRO_Temp.sort_values('datetime')
data_targets_LIRO_Temp = data_targets_LIRO_Temp.reset_index(drop=True)
targets_LIRO_Temp = data_targets_LIRO_Temp[["observation"]].values.astype('float32')

X_train, y_train = convert_tensor(targets_LIRO_Temp, lb=14)
today =date.today()
model = WaterQmodel()

# Define the number of times to train the model
num_trainings = 3

# Initialize an DataFrame
results_df = pd.DataFrame()
for i in range(num_trainings):

    training(model,number_epochs=300)

    predictions = predict(targets_LIRO_Temp , data_targets_LIRO_Temp ,types = 'temperature' , site_id = 'LIRO')
    predictions.insert(3, 'parameters', i+1)
    results_i = pd.DataFrame(predictions)
    if i == 0:
        results_df = results_i
    else:
        results_df = pd.concat([results_df,results_i], ignore_index=True)

LIRO_Temp = results_df 
LIRO_Temp

targets_LIRO_Oxy = targetsOxygen[targetsOxygen['site_id'].str.contains('LIRO')]
data_targets_LIRO_Oxy = targets_LIRO_Oxy[['datetime', 'observation', 'site_id']]
data_targets_LIRO_Oxy = data_targets_LIRO_Oxy.sort_values('datetime')
data_targets_LIRO_Oxy = data_targets_LIRO_Oxy.reset_index(drop=True)
targets_LIRO_Oxy = data_targets_LIRO_Oxy[["observation"]].values.astype('float32')

X_train, y_train = convert_tensor(targets_LIRO_Oxy, lb=14)
today =date.today()
model = WaterQmodel()

# Define the number of times to train the model
num_trainings = 3

# Initialize an DataFrame
results_df = pd.DataFrame()
for i in range(num_trainings):

    training(model,number_epochs=300)

    predictions = predict(targets_LIRO_Oxy , data_targets_LIRO_Oxy ,types = 'oxygen' , site_id = 'LIRO')
    predictions.insert(3, 'parameters', i+1)
    results_i = pd.DataFrame(predictions)
    if i == 0:
        results_df = results_i
    else:
        results_df = pd.concat([results_df,results_i], ignore_index=True)

LIRO_Oxy = results_df 
LIRO_Oxy

targets_LIRO_Chla = targetsChla[targetsChla['site_id'].str.contains('LIRO')]
data_targets_LIRO_Chla = targets_LIRO_Chla[['datetime', 'observation', 'site_id']]
data_targets_LIRO_Chla = data_targets_LIRO_Chla.sort_values('datetime')
data_targets_LIRO_Chla = data_targets_LIRO_Chla.reset_index(drop=True)
targets_LIRO_Chla = data_targets_LIRO_Chla[["observation"]].values.astype('float32')

X_train, y_train = convert_tensor(targets_LIRO_Chla, lb=14)
today =date.today()
model = WaterQmodel()

# Define the number of times to train the model
num_trainings = 3

# Initialize an DataFrame
results_df = pd.DataFrame()
for i in range(num_trainings):

    training(model,number_epochs=300)

    predictions = predict(targets_LIRO_Chla , data_targets_LIRO_Chla ,types = 'chla' , site_id = 'LIRO')
    predictions.insert(3, 'parameters', i+1)
    results_i = pd.DataFrame(predictions)
    if i == 0:
        results_df = results_i
    else:
        results_df = pd.concat([results_df,results_i], ignore_index=True)

LIRO_Chla = results_df 
LIRO_Chla

# download as csv
LIRO = pd.concat([LIRO_Temp, LIRO_Oxy, LIRO_Chla], axis=0, ignore_index=True)
LIRO.to_csv('LIRO.csv', encoding = 'utf-8-sig') 
files.download('LIRO.csv')

"""PRLA - Temperature,Oxygen,Chla"""

targets_PRLA_Temp = targetsTemp[targetsTemp['site_id'].str.contains('PRLA')]
data_targets_PRLA_Temp = targets_PRLA_Temp[['datetime', 'observation', 'site_id']]
data_targets_PRLA_Temp = data_targets_PRLA_Temp.sort_values('datetime')
data_targets_PRLA_Temp = data_targets_PRLA_Temp.reset_index(drop=True)
targets_PRLA_Temp = data_targets_PRLA_Temp[["observation"]].values.astype('float32')

X_train, y_train = convert_tensor(targets_PRLA_Temp, lb=14)
today =date.today()
model = WaterQmodel()

# Define the number of times to train the model
num_trainings = 3

# Initialize an DataFrame
results_df = pd.DataFrame()
for i in range(num_trainings):

    training(model,number_epochs=300)

    predictions = predict(targets_PRLA_Temp , data_targets_PRLA_Temp ,types = 'temperature' , site_id = 'PRLA')
    predictions.insert(3, 'parameters', i+1)
    results_i = pd.DataFrame(predictions)
    if i == 0:
        results_df = results_i
    else:
        results_df = pd.concat([results_df,results_i], ignore_index=True)

PRLA_Temp = results_df 
PRLA_Temp

targets_PRLA_Oxy = targetsOxygen[targetsOxygen['site_id'].str.contains('PRLA')]
data_targets_PRLA_Oxy = targets_PRLA_Oxy[['datetime', 'observation', 'site_id']]
data_targets_PRLA_Oxy = data_targets_PRLA_Oxy.sort_values('datetime')
data_targets_PRLA_Oxy = data_targets_PRLA_Oxy.reset_index(drop=True)
targets_PRLA_Oxy = data_targets_PRLA_Oxy[["observation"]].values.astype('float32')

X_train, y_train = convert_tensor(targets_PRLA_Oxy, lb=14)
today =date.today()
model = WaterQmodel()

# Define the number of times to train the model
num_trainings = 3

# Initialize an DataFrame
results_df = pd.DataFrame()
for i in range(num_trainings):

    training(model,number_epochs=300)

    predictions = predict(targets_PRLA_Oxy , data_targets_PRLA_Oxy ,types = 'oxygen' , site_id = 'PRLA')
    predictions.insert(3, 'parameters', i+1)
    results_i = pd.DataFrame(predictions)
    if i == 0:
        results_df = results_i
    else:
        results_df = pd.concat([results_df,results_i], ignore_index=True)

PRLA_Oxy = results_df 
PRLA_Oxy

targets_PRLA_Chla = targetsChla[targetsChla['site_id'].str.contains('PRLA')]
data_targets_PRLA_Chla = targets_PRLA_Chla[['datetime', 'observation', 'site_id']]
data_targets_PRLA_Chla = data_targets_PRLA_Chla.sort_values('datetime')
data_targets_PRLA_Chla = data_targets_PRLA_Chla.reset_index(drop=True)
targets_PRLA_Chla = data_targets_PRLA_Chla[["observation"]].values.astype('float32')

X_train, y_train = convert_tensor(targets_PRLA_Chla, lb=14)
today =date.today()
model = WaterQmodel()

# Define the number of times to train the model
num_trainings = 3

# Initialize an DataFrame
results_df = pd.DataFrame()
for i in range(num_trainings):

    training(model,number_epochs=300)

    predictions = predict(targets_PRLA_Chla , data_targets_PRLA_Chla ,types = 'chla' , site_id = 'PRLA')
    predictions.insert(3, 'parameters', i+1)
    results_i = pd.DataFrame(predictions)
    if i == 0:
        results_df = results_i
    else:
        results_df = pd.concat([results_df,results_i], ignore_index=True)

PRLA_Chla = results_df 
PRLA_Chla

# download as csv
PRLA = pd.concat([PRLA_Temp, PRLA_Oxy, PRLA_Chla], axis=0, ignore_index=True)
PRLA.to_csv('PRLA.csv', encoding = 'utf-8-sig') 
files.download('PRLA.csv')

"""PRPO - Temperature,Oxygen,Chla"""

targets_PRPO_Temp = targetsTemp[targetsTemp['site_id'].str.contains('PRPO')]
data_targets_PRPO_Temp = targets_PRPO_Temp[['datetime', 'observation', 'site_id']]
data_targets_PRPO_Temp = data_targets_PRPO_Temp.sort_values('datetime')
data_targets_PRPO_Temp = data_targets_PRPO_Temp.reset_index(drop=True)
targets_PRPO_Temp = data_targets_PRPO_Temp[["observation"]].values.astype('float32')

X_train, y_train = convert_tensor(targets_PRPO_Temp, lb=14)
today =date.today()
model = WaterQmodel()

# Define the number of times to train the model
num_trainings = 3

# Initialize an DataFrame
results_df = pd.DataFrame()
for i in range(num_trainings):

    training(model,number_epochs=300)

    predictions = predict(targets_PRPO_Temp , data_targets_PRPO_Temp ,types = 'temperature' , site_id = 'PRPO')
    predictions.insert(3, 'parameters', i+1)
    results_i = pd.DataFrame(predictions)
    if i == 0:
        results_df = results_i
    else:
        results_df = pd.concat([results_df,results_i], ignore_index=True)

PRPO_Temp = results_df
PRPO_Temp

targets_PRPO_Oxy = targetsOxygen[targetsOxygen['site_id'].str.contains('PRPO')]
data_targets_PRPO_Oxy = targets_PRPO_Oxy[['datetime', 'observation', 'site_id']]
data_targets_PRPO_Oxy = data_targets_PRPO_Oxy.sort_values('datetime')
data_targets_PRPO_Oxy = data_targets_PRPO_Oxy.reset_index(drop=True)
targets_PRPO_Oxy = data_targets_PRPO_Oxy[["observation"]].values.astype('float32')

X_train, y_train = convert_tensor(targets_PRPO_Oxy, lb=14)
today =date.today()
model = WaterQmodel()

# Define the number of times to train the model
num_trainings = 3

# Initialize an DataFrame
results_df = pd.DataFrame()
for i in range(num_trainings):

    training(model,number_epochs=300)

    predictions = predict(targets_PRPO_Oxy , data_targets_PRPO_Oxy ,types = 'oxygen' , site_id = 'PRPO')
    predictions.insert(3, 'parameters', i+1)
    results_i = pd.DataFrame(predictions)
    if i == 0:
        results_df = results_i
    else:
        results_df = pd.concat([results_df,results_i], ignore_index=True)

PRPO_Oxy = results_df 
PRPO_Oxy

targets_PRPO_Chla = targetsChla[targetsChla['site_id'].str.contains('PRPO')]
data_targets_PRPO_Chla = targets_PRPO_Chla[['datetime', 'observation', 'site_id']]
data_targets_PRPO_Chla = data_targets_PRPO_Chla.sort_values('datetime')
data_targets_PRPO_Chla = data_targets_PRPO_Chla.reset_index(drop=True)
targets_PRPO_Chla = data_targets_PRPO_Chla[["observation"]].values.astype('float32')

X_train, y_train = convert_tensor(targets_PRPO_Chla, lb=14)
today =date.today()
model = WaterQmodel()

# Define the number of times to train the model
num_trainings = 3

# Initialize an DataFrame
results_df = pd.DataFrame()
for i in range(num_trainings):

    training(model,number_epochs=300)

    predictions = predict(targets_PRPO_Chla , data_targets_PRPO_Chla ,types = 'chla' , site_id = 'PRPO')
    predictions.insert(3, 'parameters', i+1)
    results_i = pd.DataFrame(predictions)
    if i == 0:
        results_df = results_i
    else:
        results_df = pd.concat([results_df,results_i], ignore_index=True)

PRPO_Chla = results_df 
PRPO_Chla

# download as csv
PRPO = pd.concat([PRPO_Temp, PRPO_Oxy, PRPO_Chla], axis=0, ignore_index=True)
PRPO.to_csv('PRPO.csv', encoding = 'utf-8-sig') 
files.download('PRPO.csv')

"""SUGG - Temperature,Oxygen,Chla"""

targets_SUGG_Temp = targetsTemp[targetsTemp['site_id'].str.contains('SUGG')]
data_targets_SUGG_Temp = targets_SUGG_Temp[['datetime', 'observation', 'site_id']]
data_targets_SUGG_Temp = data_targets_SUGG_Temp.sort_values('datetime')
data_targets_SUGG_Temp = data_targets_SUGG_Temp.reset_index(drop=True)
targets_SUGG_Temp = data_targets_SUGG_Temp[["observation"]].values.astype('float32')

X_train, y_train = convert_tensor(targets_SUGG_Temp, lb=14)
today =date.today()
model = WaterQmodel()

# Define the number of times to train the model
num_trainings = 3

# Initialize an DataFrame
results_df = pd.DataFrame()
for i in range(num_trainings):

    training(model,number_epochs=300)

    predictions = predict(targets_SUGG_Temp , data_targets_SUGG_Temp ,types = 'temperature' , site_id = 'SUGG')
    predictions.insert(3, 'parameters', i+1)
    results_i = pd.DataFrame(predictions)
    if i == 0:
        results_df = results_i
    else:
        results_df = pd.concat([results_df,results_i], ignore_index=True)

SUGG_Temp = results_df
SUGG_Temp

targets_SUGG_Oxy = targetsOxygen[targetsOxygen['site_id'].str.contains('SUGG')]
data_targets_SUGG_Oxy = targets_SUGG_Oxy[['datetime', 'observation', 'site_id']]
data_targets_SUGG_Oxy = data_targets_SUGG_Oxy.sort_values('datetime')
data_targets_SUGG_Oxy = data_targets_SUGG_Oxy.reset_index(drop=True)
targets_SUGG_Oxy = data_targets_SUGG_Oxy[["observation"]].values.astype('float32')

X_train, y_train = convert_tensor(targets_SUGG_Oxy, lb=14)
today =date.today()
model = WaterQmodel()

# Define the number of times to train the model
num_trainings = 3

# Initialize an DataFrame
results_df = pd.DataFrame()
for i in range(num_trainings):

    training(model,number_epochs=300)

    predictions = predict(targets_SUGG_Oxy , data_targets_SUGG_Oxy ,types = 'oxygen' , site_id = 'SUGG')
    predictions.insert(3, 'parameters', i+1)
    results_i = pd.DataFrame(predictions)
    if i == 0:
        results_df = results_i
    else:
        results_df = pd.concat([results_df,results_i], ignore_index=True)

SUGG_Oxy = results_df 
SUGG_Oxy

targets_SUGG_Chla = targetsChla[targetsChla['site_id'].str.contains('SUGG')]
data_targets_SUGG_Chla = targets_SUGG_Chla[['datetime', 'observation', 'site_id']]
data_targets_SUGG_Chla = data_targets_SUGG_Chla.sort_values('datetime')
data_targets_SUGG_Chla = data_targets_SUGG_Chla.reset_index(drop=True)
targets_SUGG_Chla = data_targets_SUGG_Chla[["observation"]].values.astype('float32')

X_train, y_train = convert_tensor(targets_SUGG_Chla, lb=14)
today =date.today()
model = WaterQmodel()

# Define the number of times to train the model
num_trainings = 3

# Initialize an DataFrame
results_df = pd.DataFrame()
for i in range(num_trainings):

    training(model,number_epochs=300)

    predictions = predict(targets_SUGG_Chla , data_targets_SUGG_Chla ,types = 'chla' , site_id = 'SUGG')
    predictions.insert(3, 'parameters', i+1)
    results_i = pd.DataFrame(predictions)
    if i == 0:
        results_df = results_i
    else:
        results_df = pd.concat([results_df,results_i], ignore_index=True)

SUGG_Chla = results_df 
SUGG_Chla

# download as csv
SUGG = pd.concat([SUGG_Temp, SUGG_Oxy, SUGG_Chla], axis=0, ignore_index=True)
SUGG.to_csv('SUGG.csv', encoding = 'utf-8-sig') 
files.download('SUGG.csv')

"""TOOK - Temperature,Oxygen,Chla"""

targets_TOOK_Temp = targetsTemp[targetsTemp['site_id'].str.contains('TOOK')]
data_targets_TOOK_Temp = targets_TOOK_Temp[['datetime', 'observation', 'site_id']]
data_targets_TOOK_Temp = data_targets_TOOK_Temp.sort_values('datetime')
data_targets_TOOK_Temp = data_targets_TOOK_Temp.reset_index(drop=True)
targets_TOOK_Temp = data_targets_TOOK_Temp[["observation"]].values.astype('float32')

# train the model to predict enough datas for future prediction
X_train, y_train = convert_tensor(targets_TOOK_Temp, lb=14)
today =date.today()
model = WaterQmodel()
training(model,number_epochs=300)

## predict more data to predict next 30 days from today

edate = datetime.strptime(data_targets_TOOK_Temp.iloc[-1, 0], "%Y-%m-%d").date()
new = len(data_targets_TOOK_Temp)
input_seq = torch.Tensor(targets_TOOK_Temp)
output = model(input_seq)
j = 0
i = -1
pred = [0]*new
while i > -1*new - 1:
    pred[j] = output[i].item()
    i -= 1
    j += 1
ref_date = edate

date_range = [0]*new

for i in range (new):
    date = ref_date + timedelta(days = i+1)
    date_range[i] = date.strftime("%Y-%m-%d")
variable = ["temperature"]*new
site_id = ['TOOK']*new

dat = {'datetime':date_range, 'site_id': site_id, 'observation':pred}
new_Took_temperature = pd.DataFrame(dat, columns = ['datetime', 'observation' , 'site_id'])

# combine dataset
TOOK_Temperature = pd.concat([data_targets_TOOK_Temp,new_Took_temperature], ignore_index=True)
TOOK_Temperature

Data_TOOK_Temp = TOOK_Temperature[['datetime', 'observation', 'site_id']]
Data_TOOK_Temp = Data_TOOK_Temp.sort_values('datetime')
Data_TOOK_Temp = Data_TOOK_Temp.reset_index(drop=True)
TOOK_Temperature = Data_TOOK_Temp[["observation"]].values.astype('float32')

X_train, y_train = convert_tensor(TOOK_Temperature, lb=14)
today =date.today()
model = WaterQmodel()

# Define the number of times to train the model
num_trainings = 2

# Initialize an DataFrame
results_df = pd.DataFrame()
for i in range(num_trainings):

    training(model,number_epochs=50)

    predictions = predict(TOOK_Temperature , Data_TOOK_Temp ,types = 'temperature' , site_id = 'TOOK')
    predictions.insert(3, 'parameters', i+1)
    results_i = pd.DataFrame(predictions)
    if i == 0:
        results_df = results_i
    else:
        results_df = pd.concat([results_df,results_i], ignore_index=True)

TOOK_Temp = results_df 
TOOK_Temp

targets_TOOK_Oxy = targetsOxygen[targetsOxygen['site_id'].str.contains('TOOK')]
data_targets_TOOK_Oxy = targets_TOOK_Oxy[['datetime', 'observation', 'site_id']]
data_targets_TOOK_Oxy = data_targets_TOOK_Oxy.sort_values('datetime')
data_targets_TOOK_Oxy = data_targets_TOOK_Oxy.reset_index(drop=True)
targets_TOOK_Oxy = data_targets_TOOK_Oxy[["observation"]].values.astype('float32')

# train the model to predict enough datas for future prediction
X_train, y_train = convert_tensor(targets_TOOK_Oxy, lb=14)
today =date.today()
model = WaterQmodel()
training(model,number_epochs=300)

## predict more data to predict next 30 days from today

edate = datetime.strptime(data_targets_TOOK_Oxy.iloc[-1, 0], "%Y-%m-%d").date()
new = len(data_targets_TOOK_Oxy)
input_seq = torch.Tensor(targets_TOOK_Oxy)
output = model(input_seq)
j = 0
i = -1
pred = [0]*new
while i > -1*new - 1:
    pred[j] = output[i].item()
    i -= 1
    j += 1
ref_date = edate

date_range = [0]*new

for i in range (new):
    date = ref_date + timedelta(days = i+1)
    date_range[i] = date.strftime("%Y-%m-%d")
variable = ["oxygen"]*new
site_id = ['TOOK']*new

dat = {'datetime':date_range, 'site_id': site_id, 'observation':pred}
new_Took_Oxy = pd.DataFrame(dat, columns = ['datetime', 'observation' , 'site_id'])

# combine dataset
TOOK_Oxy = pd.concat([data_targets_TOOK_Oxy,new_Took_Oxy], ignore_index=True)
TOOK_Oxy

Data_TOOK_Oxy = TOOK_Oxy[['datetime', 'observation', 'site_id']]
Data_TOOK_Oxy = Data_TOOK_Oxy.sort_values('datetime')
Data_TOOK_Oxy = Data_TOOK_Oxy.reset_index(drop=True)
TOOK_Oxy = Data_TOOK_Oxy[["observation"]].values.astype('float32')

X_train, y_train = convert_tensor(TOOK_Oxy, lb=14)
today =date.today()
model = WaterQmodel()

# Define the number of times to train the model
num_trainings = 2

# Initialize an DataFrame
results_df = pd.DataFrame()
for i in range(num_trainings):

    training(model,number_epochs=50)

    predictions = predict(TOOK_Oxy , Data_TOOK_Oxy ,types = 'oxygen' , site_id = 'TOOK')
    predictions.insert(3, 'parameters', i+1)
    results_i = pd.DataFrame(predictions)
    if i == 0:
        results_df = results_i
    else:
        results_df = pd.concat([results_df,results_i], ignore_index=True)

TOOK_Oxy = results_df 
TOOK_Oxy

targets_TOOK_Chla = targetsChla[targetsChla['site_id'].str.contains('TOOK')]
data_targets_TOOK_Chla = targets_TOOK_Chla[['datetime', 'observation', 'site_id']]
data_targets_TOOK_Chla = data_targets_TOOK_Chla.sort_values('datetime')
data_targets_TOOK_Chla = data_targets_TOOK_Chla.reset_index(drop=True)
targets_TOOK_Chla = data_targets_TOOK_Chla[["observation"]].values.astype('float32')

# train the model to predict enough datas for future prediction
X_train, y_train = convert_tensor(targets_TOOK_Chla, lb=14)
today =date.today()
model = WaterQmodel()
training(model,number_epochs=300)

## predict more data to predict next 30 days from today

edate = datetime.strptime(data_targets_TOOK_Chla.iloc[-1, 0], "%Y-%m-%d").date()
new = len(data_targets_TOOK_Chla)
input_seq = torch.Tensor(targets_TOOK_Chla)
output = model(input_seq)
j = 0
i = -1
pred = [0]*new
while i > -1*new - 1:
    pred[j] = output[i].item()
    i -= 1
    j += 1
ref_date = edate

date_range = [0]*new

for i in range (new):
    date = ref_date + timedelta(days = i+1)
    date_range[i] = date.strftime("%Y-%m-%d")
variable = ["chla"]*new
site_id = ['TOOK']*new

dat = {'datetime':date_range, 'site_id': site_id, 'observation':pred}
new_Took_Chla = pd.DataFrame(dat, columns = ['datetime', 'observation' , 'site_id'])

# combine dataset
TOOK_Chla = pd.concat([data_targets_TOOK_Chla,new_Took_Chla], ignore_index=True)
TOOK_Chla

Data_TOOK_Chla = TOOK_Chla[['datetime', 'observation', 'site_id']]
Data_TOOK_Chla = Data_TOOK_Chla.sort_values('datetime')
Data_TOOK_Chla = Data_TOOK_Chla.reset_index(drop=True)
TOOK_Chla = Data_TOOK_Chla[["observation"]].values.astype('float32')

X_train, y_train = convert_tensor(TOOK_Chla, lb=14)
today =date.today()
model = WaterQmodel()

# Define the number of times to train the model
num_trainings = 2

# Initialize an DataFrame
results_df = pd.DataFrame()
for i in range(num_trainings):

    training(model,number_epochs=50)

    predictions = predict(TOOK_Chla , Data_TOOK_Chla ,types = 'chla' , site_id = 'TOOK')
    predictions.insert(3, 'parameters', i+1)
    results_i = pd.DataFrame(predictions)
    if i == 0:
        results_df = results_i
    else:
        results_df = pd.concat([results_df,results_i], ignore_index=True)

TOOK_Chla = results_df 
TOOK_Chla

# download as csv
TOOK = pd.concat([TOOK_Temp, TOOK_Oxy, TOOK_Chla], axis=0, ignore_index=True)
TOOK.to_csv('TOOK.csv', encoding = 'utf-8-sig') 
files.download('TOOK.csv')

csv_files = ['BARC.csv', 'CRAM.csv', 'LIRO.csv', 'PRLA.csv', 'SUGG.csv', 'PRPO.csv', 'TOOK.csv']

# Create an empty DataFrame to hold the merged data
merged_data = pd.DataFrame()

# Loop through the CSV files and append them to the merged_data DataFrame
for file in csv_files:
    data = pd.read_csv(file)
    merged_data = merged_data.append(data)

# Write the merged data to a new CSV file
merged_data.to_csv('lake.csv.gz', index=False, compression='gzip')

files.download('lake.csv.gz')
