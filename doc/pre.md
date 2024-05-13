# Pre-analysis
--------------

## Introducción
Vamos a realizar un análisis análogo al de [este artículo](https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.3002366#sec021).
La idea general es medir cuan bien se puede predecir **FEATURES DE LA SEÑAL BOLD DEL FMRI EN LA / la señal BOLD del fMRI en la** corteza auditiva a partir de representaciones internas / activaciones de redes neuronales.
En el artículo original se utilizan distintas redes neuronales entrenadas para resolver diversas tareas de audio. Algunas de estas redes son:
- **AST**: es un transformer que a partir de espectrogramas predice diversas clases de sonidos.
- **Wav2Vec2**: también es un transformer que se entrena de forma auto-supervisada para desenmascarar señales de habla. La misma es utilizada ampliamente mediante transferencia de aprendizaje para resolver tareas de habla como reconocimiento de habla, emociones y hablante.
- **CochlNet**: modelos desarrollados por los autores del artículo para poder realizar análisis más detallados.

**Ampliar con metodologia y resultados del paper**
En este trabajo se realizan diversos experimentos, nosotros nos focalizaremos en dos de los análisis abordados, los caules detallamos a continuación: 
- En una primer aproximación, se utilizan las activaciones de distintas capas de redes neuronales como entrada en una regresión de Ridge, para estimar la señal de BOLD de cada uno de los voxeles de la corteza auditiva.
- A partir de estos resultdos fue posible realizar una comparación directa de la organización jerárquica de las redes neuronales artificiales y del cerebro en el procesamiento del audio. Para esto, se analizó que capa de la red neuronal era mejor predictor de la señal BOLD de cada voxel, y se encontró que las capas del medio se correspondían mejor con los voxeles de la corteza auditiva primaria, y capas más profundas predecían mejor las regiones vecinas (corteza auditiva secundaria).
- Por otro lado implementaron un análisis de componentes principales (PCA) sobre la señal BOLD. De esta forma redujeron la dimensionalidad del problema de miles de voxeles a 6 componentes. Dichas componentes ya habían sido calculadas previamente en la publicación original de los datos, donde se encontró que algunas componentes parecían representar las respuestas de la señal BOLD a distintos tipos de estímulos (habla, música, sonidos, etc.)

Nuestros aportes serían:
- Agregar el modelo [EnCodecMAE](https://arxiv.org/abs/2309.07391) al análisis, y variantes del mismo utilizando distintos tipos de audios de pre-entrenamiento (modelos entrenados solo con habla, solo con música, o con una mezcla de sonidos de todo tipo).
- Analizar la correspondencia gerárquica entre las activaciones del modelo de distintas capas y la señal BOLD de voxeles de la corteza auditiva primaria y secundaria.
- Al poseer checkpoints en distintos puntos del entrenamiento, agregaremos una análisis de cómo las predicciones de voxels evolucionan a lo largo del entrenamiento para un mismo modelo. Con esto podemos realizar un gráfico 3D en el que los ejes son: steps de entrenamiento, número de capa y $R^2$ entre predicciones del modelo y activaciones de los voxels.

La motivación es que EnCodecMAE posee caracteristicas diferentes a los modelos que se analizaron, particularmente:
- Usa una arquitectura transformer, a diferencia de CochlNet y otros modelos que son convolucionales.
- Está entrenado de manera auto-supervisada, a diferencia de la mayoría de los modelos analizados que se entrenan en tareas supervisadas, excepto Wav2Vec2 y VQVAE,...
- Está entrenado en una mezcla de habla, música y sonidos ambientales, a diferencia de la mayoría de los modelos analizados que fueron entrenados en un solo dominio.
- A su vez, poseemos distintas versiones de este modelo, utilizando distintos tipos de datos de entrenamiento y de señales de entrada.

Nuestras hipotesis son:
- EnCodecMAE va a exhibir un comportamiento similar a los resultados mostrados en el artículo para otros modelos. Es decir, las primeras capas serán buenas prediciendo la corteza auditiva primaria mientras que las últimas serán mejores para predecir áreas perifericas a la primaria, involucradas en etapas posteriores del procesamiento de sonidos.
- Las versiones entrenadas solo en un tipo de estímulo serán mejores prediciendo las componentes asociadas a ese estímulo. Por ejemplo, el modelo entrenado solo con habla, será mejor prediciendo las componentes relacionadas con habla.
- El modelo entrenado en una diversidad de estimulos (más parecido a como nosotros nos entrenamos), va a exhibir una mejor correlación promedio con los voxels y componentes.

## Métodos
Los datos que utilizaremos son el dataset NH2015 (No es el B2021 el que tiene 20 participantes?), que es utilizado en el artículo.
**Describir dataset**
El mismo coniste de 20 participantes, 10 de los cuáles son músicos.
Los features que utilizaremos son las activaciones de EnCodecMAE ante los distintos estimulos del dataset NH2015. Al final lo que queremos es comparar cómo procesan los estimulos el modelo y cómo lo hace el cerebro.
En el espiritu de replicar el análisis realizado en el artículo, los modelos que utilizaremos para predecir voxels a partir de los features son regresores lineales con regularización L2 (ridge). Haremos una búsqueda del hiperparámetro $\alpha$. Además agregaremos regresores con regularización L1 (lasso) que puede ser interesante para analizar qué atributos dentro de una capa resultan selectos, y si hay una consistencia entre estos features selectos en regiones del cerebro.
Seguiremos la metodología del artículo original, dividiendo los estimulos en 2 particiones, una para desarrollo y otra de held-out. Se hará leave-one-stimuli out para la búsqueda de hiperparámetros con los datos de desarrollo y luego se evaluará en los estimulos held-out.
