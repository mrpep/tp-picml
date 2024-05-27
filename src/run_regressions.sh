cd auditory_brain_dnn/aud_dnn
for model in mel256-ec-base mel256-ec-base-as mel256-ec-base-ll mel256-ec-base-fma
do
    for i in {0..9}
    do
    python AUD_main.py --source_model $model --source_layer $i --target NH2015comp
    done
done