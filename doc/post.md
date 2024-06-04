# Post-analysis
--------------

## Resultados
### Voxel-wise analysis:
The authors of the paper provide data of the voxels positions in a 2D raster plot. The voxels correspond to the auditory cortex and surrounding areas. In the next figure, the 2d raster of the voxels with anatomical annotations is presented.
![Anatomical labels](https://github.com/mrpep/tp-picml/blob/main/doc/figs/anatomical_labels.png)

In this work, we extracted features from the audio stimuli using EnCodecMAE and trained ridge regressors to predict the activations of the voxels corresponding to neural activity in response to the same stimuli. In the following figure, the $r^2$ between the predictions and voxel activity is aggregated across the anatomical regions taking the median of the $r^2$ across the voxels corresponding to each anatomical region. The procedure is repeated using features extracted from every of the 10 layers of EnCodecMAE. Similarly to the original work results, as we go deeper in the neural network, the representations are better for predicting brain activity across all analysed regions. Particularly, the first layers better predict activities in the primary region, while deeper layers are better predicting lateral and anterior regions. We hypothesize that the hierarchies in the brain are 'mimicked' by the neural network. Primary auditory cortex is the first stage of sound processing, keeping the tonotopical distribution observed in the cochlea, while areas surrounding the primary cortex (A2, A3) perform higher level processing of sounds. 

![Per-region performance](https://github.com/mrpep/tp-picml/blob/main/doc/figs/across-layers_roi-roi_label_general_mel256-ec-base_NH2015_median_r2_test_c.svg)

In the next figure, the median $r^2$ across all voxels can be seen for every layer of 3 different models: 
- Mixture, which is trained in a mixture of speech, music and environmental sounds (around 12k hours)
- Music, which is trained only with music (around 800 hours)
- Speech, which is trained only with speech recordings of people reading audiobooks (around 6k hours).

It can be seen that as we go deeper in the network, the activations are better for predicting brain activity. Also, we can observe that models trained in mixtures of sounds are the best predictors, while models trained only with speech aren't good at predicting brain activity.

![Voxelwise performance per layer](https://github.com/mrpep/tp-picml/blob/main/doc/figs/voxelwise_regression_r2_per_layer.png)

We can corroborate the correspondence between hierarchies in the neural network and the brain in the following figure. It can be seen that the regions close to the primary cortex are better predicted by the first layers while the regions around the primary cortex are better predicted by the last layers. This is a pattern also observed in other models by the original work. We excluded the last layer of the model from the analysis as it mixes information from the first layers (see full explanation at the end).

![Voxelwise performance](https://github.com/mrpep/tp-picml/blob/main/doc/figs/voxelwise_best_layer.png)

We can also observe for specific EnCodecMAE layers, how well the features predict voxel activity. In the following figure, the $r^2$ for each voxel is shown for the second (1) and the last layer (9) of the model. As observed before, the last layers are much better at predicting overall brain activity.

![Best layer per voxel](https://github.com/mrpep/tp-picml/blob/main/doc/figs/voxelwise_regression_r2.png)

When compared with other models, EnCodecMAE is the best overall at predicting brain activity. Particularly the models trained with more diverse signals, like a mixture of speech, music and environmental sounds get the best correlation results. Interestingly, models trained with music only are better predicting brain activity than models trained solely on speech. It is worth noting that the speech dataset is bigger than the music dataset (~6000 vs ~800 hours) so there isn't an advantage in that sense. We hypothesize that this result is due to music signals also containing vocal sounds (singing), and being more complex as they contain mixtures of different and very diverse sounds. Modelling these sounds might capture more complex sound patterns that are also captured by the brain and are not only specific to music.

![Performance across models](https://github.com/mrpep/tp-picml/blob/main/doc/figs/across-models_roi-None_NH2015_CV-splits-nit-10_within_subject_sem_median_r2_test_c_performance_sorted.png)

### Component-wise analysis:

While predicting the activity of each voxel is useful, previous works in the NH2015 dataset have identified 6 brain components using Independent Component Analysis (ICA). Each of these components was **found to have stronger responses to different types of stimuli or features of the stimuli, such as**: low-frequency signals, high-frequency signals, pitch, broadband signals, speech and music. The component values are precalculated and provided by the authors of the paper. For each component, we trained a ridge regressor and reported the $r^2$ between the predictions and the component values. In the following figure, the $r^2$ for each component, using the 3 models (mixture, speech, music) across the 10 layers is reported. The trends are similar to the voxel-wise analysis, with the speech model being the worse at predicting components, and the mixture and music models being the best. However, for some components related to simpler signals like low and high frequencies, the best layers are not the last but earlier ones. More complex components like music and speech exhibit the same behavior (better predictions with deeper layers). It is interesting that the speech model is not the best at predicting the speech component, and the music model is the best at predicting the low-frequency component.

![Component predictions](https://github.com/mrpep/tp-picml/blob/main/doc/figs/encodecmae-r2-per-component.png)


![models_alphas](https://github.com/mrpep/tp-picml/blob/main/doc/figs/models_alphas.png)

Finally, we analysed how the components are learned during the model training. We repeated the analysis above using intermediate checkpoints (spaced by 50k training steps) of EnCodecMAE trained in the mixture, and show the dynamics in the following figure. It can be seen that the last layers don't change too much in terms of predictivity during training for the first components. However, the speech component presents a slope during the first 150k steps, and the music component takes even longer to reach its final $r^2$. This behavior suggests that some components like speech and music are harder to learn and improve with longer trainings. Moreover, for the first layers this slope is more pronounced and is present for every component. This suggests that the first layers take longer to learn components and keep learning them in spite of the last layers being already able to predict them.

![Learning dynamics](https://github.com/mrpep/tp-picml/blob/main/doc/figs/learning-dynamics.png)

**Why did we discard the last layer?**

EnCodecMAE is composed of a stack of transformer layers, and for a more stable training, ResiDual normalization is used. As seen in the following figure, ResiDual normalization is a combination of the pre-layer and post-layer normalizations, each of which have advantages and disadvantages in terms of training dynamics. ResiDual normalization introduces an extra input and output in every transformer layer. When extracting features, a choice has to be taken: extract from left or right branch? As most of the processing blocks are in the left branch, and the right branch is more like a skip connection, the left branch is used. However, in the last layer, both branches are combined with a sum, making its behaviour a bit different from previous layers. 

![ResiDual](https://github.com/mrpep/tp-picml/blob/main/doc/figs/residual.png)

Performing a representational similarity analysis using Centered Kernel Alignment (CKA) between the left (x[0]) and right (x[1]) branches, we found that the right branch carries mostly information from the first layers, as seen in the following Figure:

![CKA ResiDual](https://github.com/mrpep/tp-picml/blob/main/doc/figs/cka_encodecmae_branches.png)

The 11 and 12 layers correspond to the decoder and are not used for feature extraction, but all the layers of the right branch are highly similar to the first 2 layers of the left branch. Summing both branches in the last layer make it 'kind of' a combination of the first layers and the last one, hence breaking some of the analysis performed. This explains some of the sudden boosts, for example, in the primary curve of the second figure, the overall $r^2$ in the third figure, etc...

Tarea:
- yaml de junifer (es complejo el procedure)
- julearn ridge vs lasso para componentes -> ampliar Fig3 con otras variantes del modelo.
- 10 Random splits stimuli (dev - test). RidgeCV en cada dev para buscar alpha. Hacerlo tambien con Lasso. Demeaning de x (activaciones) e y (componentes). R2.
## Conclusión
