# Post-analysis
--------------

## Resultados
Voxelwise:
![Anatomical labels](https://github.com/mrpep/tp-picml/blob/main/doc/figs/anatomical_labels.png)
![Voxelwise performance](https://github.com/mrpep/tp-picml/blob/main/doc/figs/voxelwise_best_layer.png)
![Best layer per voxel](https://github.com/mrpep/tp-picml/blob/main/doc/figs/voxelwise_regression_r2.png)
![Voxelwise performance per layer](https://github.com/mrpep/tp-picml/blob/main/doc/figs/voxelwise_regression_r2_per_layer.png)
![Performance across models](https://github.com/mrpep/tp-picml/blob/main/doc/figs/across-models_roi-None_NH2015_CV-splits-nit-10_within_subject_sem_median_r2_test_c_performance_sorted.png)

Componentwise:
- Mostrar para un componente r2 por capa (Plot, layer, r2 por modelo)
![Component predictions](https://github.com/mrpep/tp-picml/blob/main/doc/figs/encodecmae-r2-per-component.png)
- Fig 3 Mostrar r2 por componente en mejor capa (barplot, modelo, r2)
- Mostrar r2 por componente por step de entrenamiento (Plot, step, r2 mejor capa componente)

Tarea:
- yaml de junifer (es complejo el procedure)
- julearn ridge vs lasso para componentes -> ampliar Fig3 con otras variantes del modelo.
- 10 Random splits stimuli (dev - test). RidgeCV en cada dev para buscar alpha. Hacerlo tambien con Lasso. Demeaning de x (activaciones) e y (componentes). R2.
## Conclusión
