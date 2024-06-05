# Trabajo final del curso de Neuro/ML a gran escala

### Integrantes:
- Leonardo Pepino
- Facundo González
- Agustín Sansone

### Instructions:

**0) Initial setup**

Clone this repository and we also recommend executing [this script](https://github.com/mrpep/auditory_brain_dnn/blob/main/setup_utils/download_files.py) from original repository to download dataset.

**1) Extract activations from EnCodecMAE models**

There are 2 options:
a) Clone and install [EnCodecMAE repository](https://github.com/habla-liaa/encodecmae). Then run:
```bash extract_activations.sh```
This will extract the activations in a model_actv folder.
b) Download precomputed activations from EnCodecMAE and other models from [here](https://huggingface.co/datasets/lpepino/neural_stimuli/blob/main/model_actv.tar.gz)

**2) Run regressions**

⚠️ Warning this might take a long time (around 3 days with a 24-core CPU). If you want faster results, calculating only components will be faster (should take a few minutes). Alternatively, precomputed results can be downloaded from [here](https://huggingface.co/datasets/lpepino/neural_stimuli/blob/main/results.tar.gz)

```bash run_regressions.sh```

**3) Generate plots**

Plots can be generated using the notebooks in /src

