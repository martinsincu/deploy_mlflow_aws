import mlflow
import mlflow.sklearn

from utilSD import per_missing, var_unicos, corr_top, corr_detail, crear_dummies, evaluar_rf
import pandas as pd
import numpy as np
import time
import datetime as dt

from sklearn.ensemble import RandomForestClassifier

mlflow.set_experiment("fraude_classification_model")


Data_raw = pd.read_csv(".\data\ds_challenge_2021.csv", sep=",")

Data_raw['fraude'] = Data_raw['fraude'].astype(int)

dispositivo_json_cols = list(eval(Data_raw['dispositivo'].loc[0]).keys())
list_data = list(Data_raw['dispositivo'].apply( lambda x: list( map(lambda x:str(x),list(eval(x).values()))) ) )
Data_raw.loc[:,dispositivo_json_cols] = pd.DataFrame(list_data,columns = dispositivo_json_cols)

Data_raw['fecha'] = pd.to_datetime(Data_raw['fecha'])
Data_raw['dia'] = Data_raw['fecha'].dt.dayofweek

weekDays = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
Data_raw['dia_name'] = Data_raw['dia'].map(lambda x : weekDays[x] )

Data_raw['establecimiento'] = Data_raw['establecimiento'].fillna('No_definido')
Data_raw['ciudad'] = Data_raw['ciudad'].fillna('No_definido')
Data_raw['genero'] = Data_raw['genero'].replace({ "--" : "No_definido"})
Data_raw['os'] = Data_raw['os'].replace({ "%%" : "PERCENT" , "." : "POINT" })

Data_raw['monto_cat'] = "CTE"
Data_raw['monto_cat'] = np.where( Data_raw['monto']<=245, "A_<245]" , Data_raw['monto_cat'] )
Data_raw['monto_cat'] = np.where( (Data_raw['monto']>245)&(Data_raw['monto']<=500), "B_<245-500]" , Data_raw['monto_cat'] )
Data_raw['monto_cat'] = np.where( (Data_raw['monto']>500)&(Data_raw['monto']<=750), "C_<500-750]" , Data_raw['monto_cat'] )
Data_raw['monto_cat'] = np.where( (Data_raw['monto']>750), "D_<+750>" , Data_raw['monto_cat'] )
Data_raw.drop(['monto'], axis=1, inplace=True)

Data_raw['cashback_cat'] = "CTE"
Data_raw['cashback_cat'] = np.where( Data_raw['cashback']<=2.5, "A_<2.5]" , Data_raw['cashback_cat'] )
Data_raw['cashback_cat'] = np.where( (Data_raw['cashback']>2.5)&(Data_raw['cashback']<=5.6), "B_<2.5-5.6]" , Data_raw['cashback_cat'] )
Data_raw['cashback_cat'] = np.where( (Data_raw['cashback']>5.6)&(Data_raw['cashback']<=8.5), "C_<5.6-8.5]" , Data_raw['cashback_cat'] )
Data_raw['cashback_cat'] = np.where( (Data_raw['cashback']>8.5), "D_<+8.5>" , Data_raw['cashback_cat'] )
Data_raw.drop(['cashback'], axis=1, inplace=True)

Data_raw['dcto_cat'] = "CTE"
Data_raw['dcto_cat'] = np.where( Data_raw['dcto']<=10, "A_<10]" , Data_raw['dcto_cat'] )
Data_raw['dcto_cat'] = np.where( (Data_raw['dcto']>10)&(Data_raw['dcto']<=60), "B_<10-60]" , Data_raw['dcto_cat'] )
Data_raw['dcto_cat'] = np.where( (Data_raw['dcto']>60), "C_<+60>" , Data_raw['dcto_cat'] )
Data_raw.drop(['dcto'], axis=1, inplace=True)

Data_raw['linea_tc_cat'] = "CTE"
Data_raw['linea_tc_cat'] = np.where( Data_raw['linea_tc']<=44000, "A_<44000]" , Data_raw['linea_tc_cat'] )
Data_raw['linea_tc_cat'] = np.where( (Data_raw['linea_tc']>44000)&(Data_raw['linea_tc']<=62000), "B_<44000-62000]" , Data_raw['linea_tc_cat'] )
Data_raw['linea_tc_cat'] = np.where( (Data_raw['linea_tc']>62000)&(Data_raw['linea_tc']<=82000), "C_<62000-82000]" , Data_raw['linea_tc_cat'] )
Data_raw['linea_tc_cat'] = np.where( (Data_raw['linea_tc']>82000), "D_<+82000>" , Data_raw['linea_tc_cat'] )
Data_raw.drop(['linea_tc'], axis=1, inplace=True)

Data_raw['interes_tc_cat'] = "CTE"
Data_raw['interes_tc_cat'] = np.where( Data_raw['interes_tc']<=40, "A_<40]" , Data_raw['interes_tc_cat'] )
Data_raw['interes_tc_cat'] = np.where( (Data_raw['interes_tc']>40)&(Data_raw['interes_tc']<=50), "B_<40-50]" , Data_raw['interes_tc_cat'] )
Data_raw['interes_tc_cat'] = np.where( (Data_raw['interes_tc']>50)&(Data_raw['interes_tc']<=60), "C_<50-60]" , Data_raw['interes_tc_cat'] )
Data_raw['interes_tc_cat'] = np.where( (Data_raw['interes_tc']>60), "D_<+61>" , Data_raw['interes_tc_cat'] )
Data_raw.drop(['interes_tc'], axis=1, inplace=True)

#col_to_dummy = ['tipo_tc', 'genero', 'status_txn', 'os', 'device_score', 'ciudad', 'establecimiento', 'dia_name']
col_to_dummy = ['tipo_tc', 'genero', 'dcto_cat', 'status_txn', 'linea_tc_cat', 'interes_tc_cat', 'os', 'monto_cat', 'cashback_cat', 'ciudad', 'device_score', 'establecimiento', 'dia_name']

for col in col_to_dummy:
    Data_raw = crear_dummies(Data_raw, col )

data_DF = Data_raw.copy()

from sklearn.model_selection import train_test_split
X_train, X_test = train_test_split(data_DF, test_size = 0.3, random_state = 101)

# Balanceo
# Conteo de las Clases
target = 'fraude'

count_class_0,count_class_1 = X_train[target].value_counts()
# Dividimos las Clases
df_class_0 = X_train[X_train[target] == 0]
df_class_1 = X_train[X_train[target] == 1]

# Under Sampling
df_class_0_under = df_class_0.sample(count_class_1, replace=True)
df_balanceado_under = pd.concat([df_class_1, df_class_0_under], axis=0)

print('---> Random under-sampling:')
print(df_balanceado_under[target].value_counts())

data_under = df_balanceado_under.copy()
print("X_train shape:\t", X_train.shape)
print("data_under shape:\t", data_under.shape)


X_train_ALL = X_train.iloc[:, ~X_train.columns.isin([target])].copy()
y_train_ALL = X_train.iloc[:, X_train.columns == target].copy()

X_VAL = X_test.iloc[:, ~X_test.columns.isin([target])].copy()
y_VAL = X_test.iloc[:, X_test.columns == target].copy()


drivers = ['hora','dia','establecimiento_No_definido','ciudad_No_definido','interes_tc_cat_A_<40]','linea_tc_cat_A_<44000]','device_score_1']

with mlflow.start_run(run_name="Model experiment F") as run:

    num_estimators = 250
    mlflow.log_param("num_estimators", num_estimators)

    rf_under = RandomForestClassifier(n_estimators=num_estimators)
    rf_under.fit(data_under[drivers],  data_under[target].ravel() )

    mlflow.sklearn.log_model(rf_under, 'random-forest-model')

    metricas = evaluar_rf( X_VAL[drivers], y_VAL, rf_under, "rf_under")

    mlflow.log_metric('Recall', float(metricas['Recall']))
    mlflow.log_metric('F1-score', float(metricas['F1']))

    print(metricas)

    run_id = run.info.run_uuid
    experiment_id = run.info.experiment_id
    mlflow.end_run()
    print(f'artifact_uri = {mlflow.get_artifact_uri()}')
    print(f'runID: {run_id}')

