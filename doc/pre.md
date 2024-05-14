# Pre-analysis
--------------

## Introducción
Vamos a realizar un análisis análogo al de [este artículo](https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.3002366#sec021).
La idea general es medir cuan bien se puede predecir features de la señal BOLD del FMRI en la corteza auditiva a partir de representaciones internas / activaciones de redes neuronales.
En el artículo original se utilizan distintas redes neuronales entrenadas para resolver diversas tareas de audio. Algunas de estas redes son:
- **AST**: es un transformer que a partir de espectrogramas predice diversas clases de sonidos.
- **Wav2Vec2**: también es un transformer que se entrena de forma auto-supervisada para desenmascarar señales de habla. La misma es utilizada ampliamente mediante transferencia de aprendizaje para resolver tareas de habla como reconocimiento de habla, emociones y hablante.
- **CochlNet**: modelos desarrollados por los autores del artículo para poder realizar análisis más detallados.

**Ampliar con metodologia y resultados del paper**
En este trabajo se realizan diversos experimentos, nosotros nos focalizaremos en dos de los análisis abordados, los cuales detallamos a continuación: 
- En una primer aproximación, se utilizan las activaciones de distintas capas de redes neuronales como entrada en una regresión de Ridge, para estimar la señal de BOLD de cada uno de los voxeles de la corteza auditiva.
- A partir de estos resultados fue posible realizar una comparación directa de la organización jerárquica de las redes neuronales artificiales y del cerebro en el procesamiento del audio. Para esto, se analizó qué capa de la red neuronal era mejor predictor de la señal BOLD de cada voxel, y se encontró que las capas del medio se correspondían mejor con los voxeles de la corteza auditiva primaria, y capas más profundas predecían mejor las regiones vecinas (corteza auditiva secundaria).
- Por otro lado implementaron un análisis de componentes independientes (ICA) sobre la señal BOLD. De esta forma redujeron la dimensionalidad del problema de miles de voxeles a 6 componentes. Dichas componentes ya habían sido calculadas previamente en la publicación original de los datos, donde se encontró que algunas componentes parecían representar las respuestas de la señal BOLD a distintos tipos de estímulos (habla, música, sonidos, etc.)

Nuestros aportes serían:
- Agregar el modelo [EnCodecMAE](https://arxiv.org/abs/2309.07391) al análisis, y variantes del mismo utilizando distintos tipos de audios de pre-entrenamiento (modelos entrenados solo con habla, solo con música, o con una mezcla de sonidos de todo tipo).
- Analizar la correspondencia jerárquica entre las activaciones del modelo de distintas capas y la señal BOLD de voxeles de la corteza auditiva primaria y secundaria.
- Al poseer checkpoints en distintos puntos del entrenamiento, agregaremos una análisis de cómo las predicciones de voxels evolucionan a lo largo del entrenamiento para un mismo modelo. Con esto podemos realizar un gráfico 3D en el que los ejes son: steps de entrenamiento, número de capa y $R^2$ entre predicciones del modelo y activaciones de los voxels.

La motivación es que EnCodecMAE posee características diferentes a los modelos que se analizaron, particularmente:
- Usa una arquitectura transformer, a diferencia de CochlNet y otros modelos que son convolucionales.
- Está entrenado de manera auto-supervisada, a diferencia de la mayoría de los modelos analizados que se entrenan en tareas supervisadas, excepto Wav2Vec2 y VQVAE,...
- Está entrenado en una mezcla de habla, música y sonidos ambientales, a diferencia de la mayoría de los modelos analizados que fueron entrenados en un solo dominio.
- A su vez, poseemos distintas versiones de este modelo, utilizando distintos tipos de datos de entrenamiento y de señales de entrada.

Nuestras hipotesis son:
- EnCodecMAE va a exhibir un comportamiento similar a los resultados mostrados en el artículo para otros modelos. Es decir, las primeras capas serán buenas prediciendo la corteza auditiva primaria mientras que las últimas serán mejores para predecir áreas perifericas a la primaria, involucradas en etapas posteriores del procesamiento de sonidos.
- Las versiones entrenadas solo en un tipo de estímulo serán mejores prediciendo las componentes asociadas a ese estímulo. Por ejemplo, el modelo entrenado solo con habla, será mejor prediciendo las componentes relacionadas con habla.
- El modelo entrenado en una diversidad de estimulos (más parecido a como nosotros nos entrenamos), va a exhibir una mejor correlación promedio con los voxels y componentes.

## Métodos

Los datos que utilizaremos son el dataset NH2015, que es uno de los utilizados en el artículo. El mismo consiste de 18 participantes sin formación musical que fueron analizados en un scanner Siemens Trio de 3T al escuchar 165 estímulos sonoros distintos. Los estímulos corresponden a sonidos cotidianos con 2 segundos de duración y fueron reproducidos en bloques de 5 repeticiones. Tras cada repetición se realizó una medición. Cada volumen funcional (es decir, una única imagen 3D) incluye 15 cortes orientados paralelos al plano temporal superior y que cubre la porción del lóbulo temporal superior e incluye el surco temporal superior (3,4 s TR, 30 ms TE, ángulo de giro de 90 grados). Cada corte tiene un grosor de 4 mm y una resolución en el plano de 2,1 x 2,1 mm. (matriz de 96 x 96, espacio entre cortes de 0,4 mm). Se utilizó iPAT para minimizar el tiempo de adquisición (1 segundos/volumen). También se recogieron imágenes anatómicas ponderadas en T1 para cada sujeto (vóxeles isotrópicos de 1 mm).
Los volúmenes funcionales se preprocesaron utilizando el software FSL y código MATLAB personalizado. Los volúmenes fueron motion-corrected, slice-time-corrected, skull-stripped, linearly detrended, y alineados a los volumenes anatomicos (usando FLIRT y BBRegister; Greve and
Fischl, 2009; Jenkinson and Smith, 2001). Luego se resamplearon los datos de volumen en la superficie cortical reconstruida calculada por FreeSurfer (Dale et al., 1999) y se suavizo usando un kernel FWHM de 3 mm para mejorar la relación señal a ruido.


Los features que utilizaremos son las activaciones del encoder transformer de EnCodecMAE ante los distintos estimulos del dataset NH2015. Al final lo que queremos es comparar cómo procesan los estimulos el modelo y cómo lo hace el cerebro.
En el espiritu de replicar el análisis realizado en el artículo, los modelos que utilizaremos para predecir voxels a partir de los features son regresores lineales con regularización L2 (ridge). Haremos una búsqueda del hiperparámetro $\alpha$. Además agregaremos regresores con regularización L1 (lasso) que puede ser interesante para analizar qué atributos dentro de una capa resultan selectos, y si hay una consistencia entre estos features selectos en regiones del cerebro.
Seguiremos la metodología del artículo original, dividiendo los estimulos en 2 particiones, una para desarrollo y otra de held-out. Se hará leave-one-stimuli out para la búsqueda de hiperparámetros con los datos de desarrollo y luego se evaluará en los estimulos held-out.
