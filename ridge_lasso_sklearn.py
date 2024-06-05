# Run in background: nohup bash -c "python3 sklearn_main.py" &
# to see output in real time: tail -f nohup.out

import scipy.io
import pickle
import numpy as np
from tqdm import tqdm
from sklearn.linear_model import RidgeCV, LassoCV, MultiTaskLassoCV
from sklearn.model_selection import LeaveOneOut, KFold, GridSearchCV
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
import os
from pathlib import Path
import datetime
import sys

components = scipy.io.loadmat('/home/tppicml/braindnn/data/neural/NH2015comp/components.mat') # set correct path
ytrue = components['R']
stim_names = components['stim_names']

x = []
for s in stim_names[0]:
    s_data = []
    filename = f'/home/tppicml/braindnn/model_actv/mel256-ec-base/{s[0]}_activations.pkl' # set correct path
    with open(filename,'rb') as f:
        act_data = pickle.load(f)
        for i in range(10):
            s_data.append(act_data[i])
    x.append(s_data)
x = np.array(x)

cv = KFold()
n_train=83
N_CV=10

for model_name in ['lasso']:
    all_test_r2 = []
    for layer in range(10):
        test_r2 = []
        models = []
        for i in tqdm(range(N_CV)):
            idxs = np.random.permutation(np.arange(len(ytrue)))
            train_idxs = idxs[:n_train]
            test_idxs = idxs[n_train:]
            x_train = x[train_idxs, layer]
            x_test = x[test_idxs, layer]
            y_train = ytrue[train_idxs]
            y_test = ytrue[test_idxs]
            
            alpha_range = 30
            possible_alphas = [10 ** x for x in range(-alpha_range, alpha_range)]

            if model_name == 'lasso':
                # model = GridSearchCV(estimator=LassoCV(), param_grid={'alphas': possible_alphas}, cv=cv, scoring='neg_mean_squared_error')
                model = MultiTaskLassoCV(alphas=possible_alphas, cv=cv)

            if model_name == 'ridge':
                model = RidgeCV(alphas=possible_alphas, cv=cv, scoring='r2')

            scaler_x = StandardScaler(with_std=False)
            scaler_y = StandardScaler(with_std=False)
            x_train = scaler_x.fit_transform(x_train)
            x_test = scaler_x.transform(x_test)
            y_train = scaler_y.fit_transform(y_train)
            model.fit(x_train, y_train)
            yhat_test = model.predict(x_test)
            yhat_test = yhat_test + scaler_y.mean_
            test_r2.append(r2_score(y_test, yhat_test, multioutput='raw_values'))
            models.append(model)

            # Check alpha
            if model.alpha_ == possible_alphas[0] or model.alpha_ == possible_alphas[-1]:
                print(f'WARNING: BEST ALPHA {model.alpha_} IS AT THE EDGE OF THE SEARCH SPACE FOR SPLIT {i}')

        test_r2 = np.array(test_r2)
        all_test_r2.append(test_r2)

    all_test_r2 = np.array(all_test_r2)
    median_test_r2 = np.median(all_test_r2,axis=1)

    fig = plt.figure()
    for c in range(6):
        plt.plot(median_test_r2[:,c], label=c)
    plt.legend()
    plt.xlabel('Layer #')
    plt.ylabel('Median Test r2')
    plt.title(f'{model_name}')
    plt.grid()

    # Define save path
    save_path = f'/home/tppicml/braindnn/results_test/mel256-ec-base/{model_name}/' # set correct path
    os.makedirs(save_path, exist_ok=True)

    # Logging
    sys.stdout = open(os.path.join(save_path, f'out-{datetime.datetime.now().strftime("%m%d%Y-%T")}.log'), 'a+')

    plt.savefig(save_path + f'{model_name}.png')

    # Save scroes
    f = open(save_path + f'{model_name}_scores.pkl', 'wb')
    pickle.dump(all_test_r2, f)
    f.close()
    
    # Save model
    f = open(save_path + f'{model_name}.pkl', 'wb')
    pickle.dump(models, f)
    f.close()

    print(f'Saved results to: {save_path}')
