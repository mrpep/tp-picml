# Post-analysis
--------------

## Resultados
Voxelwise:
- Para cada modelo de encodecmae podemos mostrar cada voxel que capa lo predijo mejor. (Scatter x_ras,y_ras,layer)
- Algun ejemplo de r2 por voxel para alguna capa (1 vs 9) (Scatter, x_ras, y_ras, r2)
- Mostrar mediana across voxels r2 para cada modelo vs modelos del paper. (barplot, model, r2)
- Mediana across voxels por region anatomica (plot, layer, r2 por region)

Componentwise:
- Mostrar r2 por componente por capa (Plot, layer, r2 por componente)
- Mostrar para un componente r2 por capa (Plot, layer, r2 por modelo)
- Fig 3 Mostrar r2 por componente en mejor capa (barplot, modelo, r2)
- Mostrar r2 por componente por step de entrenamiento (Plot, step, r2 mejor capa componente)

Tarea:
- yaml de junifer (es complejo el procedure)
- julearn ridge vs lasso para componentes -> ampliar Fig3 con otras variantes del modelo.
## Conclusión
