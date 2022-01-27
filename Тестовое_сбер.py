# Импортируем нужные нам библиотеки
import pandas as pd
import numpy as np

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, StratifiedShuffleSplit, \
    cross_val_score
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

import warnings

warnings.filterwarnings("ignore")
RAND = 10

# Записываем датасет в переменную
df = pd.read_csv('/Users/mz/Downloads/drug_consumption.data', header=None, index_col=0)
# Создаем новый стобец target
df['target'] = 0
# Находим названия столбцов с наркотическими веществами
drag_cols = [x for x in df.columns if df[x].dtype is pd.np.dtype(object)]


class SolutionDrag:

    def __init__(self, data: pd.DataFrame, estimator) -> None:
        self.data = data
        self.estimator = estimator

    def encoder(self) -> None:

        '''
        Кодируем категориальные признаки
        '''

        columns = [x for x in self.data.columns if self.data[x].dtype is pd.np.dtype(object)]

        for col in columns:
            le = LabelEncoder()
            self.data[col] = le.fit_transform(self.data[col])

    def target(self, ls=drag_cols) -> None:

        '''
        Сводим задачу к бинарной классификации
        0 - за последнии 10 лет человек ничего не употреблял из списка
        1 - за последнии 10 лет человек употреблял минимум одну категорию из списка
        '''

        if ls is None:
            ls = drag_cols

        for i in range(len(self.data)):
            if (2 or 3 or 4 or 5 or 6 or 7) in self.data[ls].iloc[i, :].to_list():
                self.data['target'].iloc[i] = 1
            else:
                self.data['target'].iloc[i] = 0

    def fit(self, random_state: int,
            test_size: float,
            X: pd.DataFrame,
            y: pd.Series) -> None:

        '''
        Обучаем модель
        '''

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, stratify=y, shuffle=True, random_state=random_state)

        self.estimator.fit(X_train, y_train)
        roc_auc = roc_auc_score(y_test, self.estimator.predict_proba(X_test)[:, 1])

        print(f'ROC-AUC({self.estimator}) = {roc_auc}')

    def cross_val(self, n_splits: int,
                  test_size: float,
                  X: pd.DataFrame,
                  y: pd.Series) -> None:

        '''
        Делаем кросс-валидацию
        '''

        folds = StratifiedShuffleSplit(n_splits=n_splits, test_size=test_size)
        scores = cross_val_score(self.estimator, X, y, scoring='roc_auc', cv=folds)

        print(f"ShuffleSplit({self.estimator}) = {np.mean(np.abs(scores))}")

    def implementation(self, random_state: int,
                       n_splits: int,
                       test_size: float) -> None:

        '''
        Преобразовываем код и выводим результат
        '''

        _val = SolutionDrag(self.data, self.estimator)
        _val.encoder()
        _val.target()
        _val.fit(random_state, test_size, df.drop(['target'], axis=1), df.target)
        _val.cross_val(n_splits, test_size, df.drop(['target'], axis=1), df.target)


if __name__ == "__main__":

    print('LogisticRegression:')
    model = SolutionDrag(df, LogisticRegression(class_weight='balance'))
    model.implementation(RAND, 3, 0.2)

    print('KNeighborsClassifier:')
    model = SolutionDrag(df, KNeighborsClassifier())
    model.implementation(RAND, 3, 0.2)

    print('RandomForestClassifier:')
    model = SolutionDrag(df, RandomForestClassifier(class_weight='balanced'))
    model.implementation(RAND, 3, 0.2)

    print('GradientBoostingClassifier:')
    model = SolutionDrag(df, GradientBoostingClassifier())
    model.implementation(RAND, 3, 0.2)

else:
    raise NameError('Unknown error')