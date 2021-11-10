from datetime import datetime
from datetime import date
from datetime import timedelta
import dateutil.relativedelta
import pandas as pd

####Funciones
# mes  : Mes base desde que se restará
# meses : cnatidad de meses que se sumará en positivo o que se restará en negativo
def AddSub_Month(mes,meses):
    resultado=(datetime.strptime(str(mes), '%Y%m')+ dateutil.relativedelta.relativedelta(months=int(meses))).strftime('%Y%m')
    return resultado

def PeriodoMasN(mes, N):
    resultado=(datetime.strptime(str(mes), '%Y%m')+ dateutil.relativedelta.relativedelta(months=int(N))).strftime('%Y%m')
    return int(resultado)

def per_missing(X):
    missing_rows = X.isnull().sum()
    missing_rows_per = X.isnull().sum().apply(lambda x: 100*(x/len(X)) )
    return pd.concat([missing_rows,missing_rows_per],axis=1).sort_values(1,ascending=False)

def var_unicos(x):
    df1 = pd.DataFrame( x.apply(lambda x: x.nunique(dropna=False), axis=0), columns=['Unicos'] )

    df1 = df1.reset_index()
    df2 = pd.DataFrame( x.dtypes , columns=['Tipo'] )
    df2 = df2.reset_index()
    return ( pd.concat([df1, df2['Tipo']],axis=1) ).sort_values(by=['Unicos'])
#sort_values() sort_index()
def corr_detail(data, target):
    df = data.corr()[target]
    df = pd.DataFrame(df).reset_index() 
    df['Abs'] = df[target].abs()
    df = df.sort_values('Abs',ascending=False)
    return df

def corr_top(data, target, top):
    df = data.corr()[target]
    df = pd.DataFrame(df).reset_index() 
    df['Abs'] = df[target].abs()
    df = df.sort_values('Abs',ascending=False).head(top+1)['index'].tolist()
    df.remove(target)
    return df

def crear_dummies_n_1( data_X, col ):
    New_ = pd.get_dummies(data_X[col], prefix=col, drop_first=True )
    
    X_ = data_X.copy()
    X_.drop([col], axis=1, inplace=True)
    
    X_ = pd.concat([X_, New_ ],axis=1)
    
    return X_

def crear_dummies( data_X, col ):
    New_ = pd.get_dummies(data_X[col], prefix=col, drop_first=False)
    
    X_ = data_X.copy()
    X_.drop([col], axis=1, inplace=True)
    
    X_ = pd.concat([X_, New_ ],axis=1)
    
    return X_

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (precision_score, recall_score,f1_score,accuracy_score,confusion_matrix, roc_auc_score)

def evaluar_rf( data_X, label_y, model_rf, model_name ):
    X_ = data_X.copy()
    y_ = label_y.copy()
    
    y_pred = model_rf.predict(X_)
    print("Modelo: ",model_name)
    print("Accuracy: %1.3f \tPrecision: %1.3f \tRecall: %1.3f \tF1: %1.3f" %  ( accuracy_score(y_, y_pred), precision_score(y_, y_pred), recall_score(y_, y_pred), f1_score(y_, y_pred) )  )
    print(confusion_matrix(y_,y_pred) )
    print("============================================================================")
    
    df = pd.DataFrame({'modelo': [model_name], 
            'Accuracy': [accuracy_score(y_, y_pred)],
            'Precision': [precision_score(y_, y_pred)],
            'Recall': [recall_score(y_, y_pred)],
            'F1': [f1_score(y_, y_pred)],
            'ROC_AUC': [roc_auc_score(y_, y_pred)],
            'Gini': [2*roc_auc_score(y_, y_pred)-1]})
    
    return df