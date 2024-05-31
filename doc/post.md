# Post-analysis
--------------

## Resultados
### Voxel-wise analysis:
![Anatomical labels](https://github.com/mrpep/tp-picml/blob/main/doc/figs/anatomical_labels.png)
![Per-region performance](https://github.com/mrpep/tp-picml/blob/main/doc/figs/across-layers_roi-roi_label_general_mel256-ec-base_NH2015_median_r2_test_c.svg)
![Voxelwise performance](https://github.com/mrpep/tp-picml/blob/main/doc/figs/voxelwise_best_layer.png)
![Best layer per voxel](https://github.com/mrpep/tp-picml/blob/main/doc/figs/voxelwise_regression_r2.png)
![Voxelwise performance per layer](https://github.com/mrpep/tp-picml/blob/main/doc/figs/voxelwise_regression_r2_per_layer.png)
![Performance across models](https://github.com/mrpep/tp-picml/blob/main/doc/figs/across-models_roi-None_NH2015_CV-splits-nit-10_within_subject_sem_median_r2_test_c_performance_sorted.png)

### Component-wise analysis:

![Component predictions](https://github.com/mrpep/tp-picml/blob/main/doc/figs/encodecmae-r2-per-component.png)
![Learning dynamics](https://github.com/mrpep/tp-picml/blob/main/doc/figs/learning-dynamics.png)

Tarea:
- yaml de junifer (es complejo el procedure)
- julearn ridge vs lasso para componentes -> ampliar Fig3 con otras variantes del modelo.
- 10 Random splits stimuli (dev - test). RidgeCV en cada dev para buscar alpha. Hacerlo tambien con Lasso. Demeaning de x (activaciones) e y (componentes). R2.
## Conclusión
