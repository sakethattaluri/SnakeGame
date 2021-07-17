from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn import tree
import pandas as pd
import graphviz


def get_threshold_classifier():
    df = pd.read_excel('Data.xlsx', index_col = 0)
    for index, row in df.iterrows():
        df.at[index, 'Left'] = 0 if row['CurDir'] == 1 else row['Left']
        df.at[index, 'Right'] = 0 if row['CurDir'] == -1 else row['Right']
        df.at[index, 'Top'] = 0 if row['CurDir'] == -2 else row['Top']
        df.at[index, 'Bottom'] = 0 if row['CurDir'] == 2 else row['Bottom']
    train, test = train_test_split(df, test_size = 0.1)
    X_train, y_train = train.iloc[:, :-1], train.iloc[:, -1]
    X_test, y_test = test.iloc[:, :-1], test.iloc[:, -1]
    
    clf = tree.DecisionTreeClassifier(max_depth = 4, criterion="gini")
    clf = clf.fit(X_train, y_train)
    
    data = tree.export_graphviz(clf, out_file=None) 
    graph = graphviz.Source(data)
    graph.render("Snake Model")
    
    pr_train = clf.predict(X_train)
    pr_test = clf.predict(X_test)
    
    print(accuracy_score(y_train, pr_train))
    print(accuracy_score(y_test, pr_test))
    return clf

def get_normal_classifier():
    train, test = train_test_split(pd.read_excel('Data.xlsx', index_col = 0), test_size = 0.1)
    X_train, y_train = train.iloc[:, :2], train.iloc[:, -1]
    X_test, y_test = test.iloc[:, :2], test.iloc[:, -1]
    
    clf = tree.DecisionTreeClassifier(max_depth = 3, criterion="gini")
    clf = clf.fit(X_train, y_train)
    
    data = tree.export_graphviz(clf, out_file=None) 
    graph = graphviz.Source(data)
    graph.render("Snake Model 1")
    
    pr_train = clf.predict(X_train)
    pr_test = clf.predict(X_test)
    
    print(accuracy_score(y_train, pr_train))
    print(accuracy_score(y_test, pr_test))
    return clf
