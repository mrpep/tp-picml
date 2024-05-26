from encodecmae.hub import load_model
from pathlib import Path
from tqdm import tqdm
import pickle

models = ['mel256-ec-base', 'mel256-ec-base-as', 'mel256-ec-base-fma', 'mel256-ec-base-ll']
stimuli_dir = '/home/lpepino/braindnn/auditory_brain_dnn/data/stimuli/165_natural_sounds'
out_dir = '/home/lpepino/braindnn/auditory_brain_dnn/model_actv'

for m in models:
    print('Extracting activations for {}'.format(m))
    model = load_model(m)
    for w in tqdm(Path(stimuli_dir).rglob('*.wav')):
        feats = model.extract_features_from_file(w, layer='all')
        feats = {i: v.mean(axis=0) for i,v in enumerate(feats)}
        out_path = Path(out_dir, m, '{}_activations.pkl'.format(w.stem))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, 'wb') as f:
            pickle.dump(feats, f)