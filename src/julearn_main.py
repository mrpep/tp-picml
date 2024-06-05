# This file is a version of auditory_brain_dnn/aud_dnn/AUD_main.py but using julearn as much as possible
# Empirically this way was much slower

from utils import *
from julearn.model_selection import ContinuousStratifiedKFold
from julearn import run_cross_validation
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LassoCV
from resources import source_layer_map
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from tqdm import tqdm

DATADIR = (Path(os.getcwd()) / '..' / '..' / 'data').resolve()
RESULTDIR = (Path(os.getcwd()) / '..' / '..' / 'results_test').resolve()
CACHEDIR = '/home/tppicml/braindnn/model_actv' # Adjust this path properly

# Set random seed
import random
np.random.seed(0)
random.seed(0)

date = datetime.datetime.now().strftime("%m%d%Y-%T")

"""
Fits a ridge regression model from source (DNN unit activations) to target (brain or component data).
"""

def main(raw_args=None):
    parser = argparse.ArgumentParser(description='Fit voxel-wise models in the auditory domain')
    parser.add_argument('--source_model', default='mel256-ec-base',
                        type=str, help='Name of source DNN model.'
                                       'Name of the DNN model from which activations will be used as regressors.'
                                       'Should match the folder name in the CACHEDIR which contains the DNN model activations.')
    parser.add_argument('--source_layer', default='9',
                        type=str, help='The source DNN layer from which activations will be used as regressors.')
    parser.add_argument('--target', default='NH2015comp',
                        type=str, help='Target, i.e. neural data or component data. '
                                       'Options are "NH2015", "B2021", "NH2015comp"')
    parser.add_argument('--alphalimit', default=50,
                        type=str, help='Which limit to use for possible alphas in ridge regression.'
                                       'Will be range: 10 ** x for x in range(-alphalimit, alphalimit)')
    parser.add_argument('--randnetw', default='False',
                        type=str, help='If "True": extract DNN model activations from a permuted model. '
                                       'Activations should be suffixed with _randnetw.'
                                       'If "False": extract DNN model activations from the original model (no suffix).')
    parser.add_argument('--save_plot', default='False', type=str, help='Whether to save diagnostic plots')
    parser.add_argument('--save_preds', default='True',
                        type=str, help='Whether to save predictions for each single sound in each cross-validation fold.')
    parser.add_argument('--verbose', default=False,
                        type=bool, help='If True, print progress to console.'
                                        'If False, direct print output to log file.')
    args = parser.parse_args(raw_args)

    print('*' * 40)
    print(vars(args))
    print('*' * 40)

    ##### Stimuli (sounds) #####
    sound_meta = np.load(os.path.join(DATADIR, 
                                      f'neural/NH2015/neural_stim_meta.npy')) # (original indexing, neural data is extracted in this order)

    # Extract wav names in order (this is how the neural data is ordered --> order all activations in the same way)
    stimuli_IDs = []
    for i in sound_meta:
        stimuli_IDs.append(i[0][:-4].decode("utf-8")) # remove .wav

    ##### Load target (neural data or components) #####
    voxel_data, voxel_id = get_target(target=args.target,
                                      stimuli_IDs=stimuli_IDs,
                                      DATADIR=DATADIR)
    n_stim = voxel_data.shape[0]
    n_vox = voxel_data.shape[1]

        
    ##### SOURCE (DNN unit activations) #####
    source_features = get_source_features(source_model=args.source_model,
                                            source_layer=args.source_layer,
                                            source_layer_map=source_layer_map,
                                            stimuli_IDs=stimuli_IDs,
                                            randnetw=args.randnetw,
                                            CACHEDIR=CACHEDIR)
    
    
    ##### Define input DataFrame for julearn cross-validation#####
    # Define names as neuron number and component name
    feature_column_names = [str(i) for i in range(source_features.shape[-1])]
    target_column_names = list(voxel_data.columns.values) 
    column_names = feature_column_names + target_column_names

    df = pd.DataFrame(columns=column_names)

    # Fill df row by row
    for i in range(source_features.shape[0]):
        input_row = list(source_features[i]) + list(voxel_data.iloc[i].values)
        df = pd.concat([df, pd.DataFrame([input_row], columns=df.columns)], ignore_index=True)

    ##### Cross-validation #####
    ## Setup splits ##
    n_CV_splits = 10
    n_train=83

    possible_alphas = [10 ** x for x in range(-args.alphalimit, args.alphalimit)]
    possible_alphas = possible_alphas[::-1]

    # Save results in dictionary
    results = {}

    # Iterate over models
    models = ['ridgecv']
    model_names = ['ridge']
    model_params = ['ridgecv__alphas']
    param_values = [possible_alphas]

    for model, model_name, model_param, param_value in zip(models, model_names, model_params, param_values):
        results[model_name] = {}

        # Iterate over components
        for target in target_column_names:
            results[model_name][target] = []

            # Iterate over splits
            for i in tqdm(range(n_CV_splits)):
                
                # Define train/dev and test sets
                random_idxs = np.random.permutation(np.arange(len(df)))
                
                train_idxs = random_idxs[:n_train]
                test_idxs = random_idxs[n_train:]
                
                df_dev = df.iloc[train_idxs]
                df_test = df.iloc[test_idxs]

                # Rename columns
                df_dev = df_dev.rename(str, axis="columns") 
                df_test = df_test.rename(str, axis="columns") 

                # Define scaler
                scaler = StandardScaler()
                
                # Only run CV for models with parameters
                if model_name != 'linear':

                    #Si tengo tantos splits como muestras estoy haciendo leave one out
                    # cv = ContinuousStratifiedKFold(n_bins=1, n_splits=5)
                
                    # Run cross validation to find best parameters and return model
                    scores_strat, model = run_cross_validation(
                        X=feature_column_names,
                        X_types={'continuous': feature_column_names},
                        y=target,
                        data=df_dev,
                        preprocess="zscore",
                        problem_type="regression",
                        model=model,
                        return_estimator="final",
                        scoring="neg_mean_squared_error", 
                        model_params={model_param: param_value})
                    
                    # Fit scaler
                    scaler.fit(df_dev)
                
                else:
                    # Define linear regression model
                    model = LinearRegression()
                    # Fit and transform scaler to dev data
                    df_dev.loc[:, df_dev.columns] = scaler.fit_transform(df_dev)
                    # Fit linear model
                    model.fit(df_dev[feature_column_names], df_dev[target])
                
    
                # Standarize test data with train parameters
                df_test.loc[:, df_test.columns] = scaler.transform(df_test)

                ## Predict test set ##
                y_pred_test = model.predict(df_test[feature_column_names])

                # Compute correlation and square
                r2 = np.corrcoef(y_pred_test, df_test[target])[1,0] ** 2

                # Save results
                results[model_name][target].append(r2)

        # make dataframe with models results
        df = pd.DataFrame.from_dict(data=results[model_name])  

        df.plot()

        # Define save path
        save_path = RESULTDIR.as_posix() + f'/' + args.source_model  + f'/{model_name}/'
        os.makedirs(save_path, exist_ok=True)

        # Logging
        if not args.verbose:
            sys.stdout = open(os.path.join(save_path, 
                                           f'out-{date}.log'), 'a+')

        # Save plot
        plt.savefig(save_path + f'/{model_name}-layer{args.source_layer}.png')
        
        # Save scroes df
        df.to_csv(save_path + f'/{model_name}-layer{args.source_layer}_scores.csv')
        
        # Save model
        f = open(save_path + f'/{model_name}-layer{args.source_layer}.pkl', 'wb')
        pickle.dump(model, f)
        f.close()

        print(f'Saved results to: {save_path}')


if __name__ == '__main__':
    main()
