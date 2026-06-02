# **Propuesta de Arquitectura Analítica Modular (Prototipo v0.1)**

## **Documento de Diseño Arquitectónico (ADD)**

**Autor:** Arquitectura de Soluciones \- Proyecto SAEIL

**Fecha:** Abril 2026

**Nivel de Audiencia:** Ingeniería de Datos, Desarrolladores Backend, Analistas Cuantitativos.

## **1\. Resumen Ejecutivo y Marco Teórico**

El presente documento delinea la arquitectura de un prototipo analítico modular diseñado para la extracción, procesamiento y proyección topológica de datos sociopolíticos. El objetivo es trascender el análisis de sentimiento escalar unidimensional, implementando metodologías de reducción de dimensionalidad (PCA y UMAP) y agrupamiento en grafos (Leiden) sobre matrices dispersas de inferencia de lenguaje natural (NLI).

La solución se concibe bajo el paradigma de microservicios o *crates* independientes, permitiendo la interoperabilidad matemática sin acoplamiento estricto, facilitando su despliegue tanto en entornos locales (prototipado) como en Google Cloud Platform (producción).

## **2\. Arquitectura de Módulos (Crates)**

El sistema se estructura en una tubería de procesamiento secuencial (*pipeline*), donde la salida ( *output*) de un *crate* sirve como entrada estructurada (*input*) para el siguiente.

### **Crate 1: Extracción y Limpieza (social\_collector\_engine)**

* **Función:** Ingesta de datos no estructurados desde APIs (Apify, redes sociales, fuentes abiertas).  
* **Procesamiento:** Estructuración JSON, limpieza de caracteres especiales, y filtrado inicial de ruido (heurísticas de *anti-spam*).  
* **Salida:** Conjunto de datos relacional primario (ID de usuario, timestamp, texto crudo).

### **Crate 2: Inferencia de Postura (sentiment\_nli\_processor)**

* **Función:** Transformación del texto natural a vectores numéricos direccionales.  
* **Técnica:** Utilización de un modelo LLM (ej. DeepSeek local o Vertex AI Gemini) parametrizado para *Natural Language Inference* (NLI), no para sentimiento general.  
* **Proceso:** El modelo evalúa el texto ![][image1] frente a un tema ![][image2] (hipótesis) y clasifica la relación:  
  * *Entailment* (Apoyo): ![][image3]  
  * *Contradiction* (Rechazo): ![][image4]  
  * *Neutral/Unrelated*: ![][image5]  
* **Salida:** *Tuplas* de (ID\_Usuario, ID\_Tema, Valor\_Postura).

### **Crate 3: Construcción de Espacio Vectorial (matrix\_builder\_core)**

* **Función:** Ensamblaje de la matriz fundamental de análisis ![][image6].  
* **Técnica:** Construcción de una matriz dispersa (*Sparse Matrix*) de ![][image7] usuarios por ![][image8] temas.  
* **Tratamiento Matemático:** Implementación de algoritmos de imputación de valores faltantes (NaN) y centrado de medias (*mean-centering*), requerimiento estricto para las transformaciones ortogonales posteriores.  
* **Salida:** Matriz imputada y centrada ![][image9].

### **Crate 4: Motor de Topología y Reducción Dimensional (topology\_analytics\_engine)**

Este es el núcleo algorítmico del prototipo, implementando dos flujos matemáticos divergentes según la necesidad analítica:

#### **Flujo 4A: Análisis de Componentes Principales (PCA) \- Enfoque Lineal**

* **Propósito:** Extracción de índices latentes y varianza explicada.  
* **Técnica:** Descomposición en Valores Singulares Truncada (Truncated SVD) sobre la matriz ![][image9]. ![][image10].  
* **Aplicación:** Extracción del Primer Componente Principal (PC1) como un "Índice General de Polarización" unidimensional. Útil para modelos predictivos (regresión) y asignación de presupuestos.

#### **Flujo 4B: UMAP \+ Agrupamiento de Leiden \- Enfoque Topológico**

* **Propósito:** Identificación de estructuras no lineales, comunidades orgánicas y cámaras de eco (*Echo Chambers*).  
* **Técnica:**  
  1. Proyección de ![][image9] a un espacio bidimensional utilizando topología algebraica (*Uniform Manifold Approximation and Projection* \- UMAP).  
  2. Construcción de un grafo de K-vecinos más cercanos (KNN) sobre las proyecciones de UMAP.  
  3. Aplicación del algoritmo de partición de grafos de **Leiden** para maximizar la modularidad y descubrir comunidades (clústeres).  
* **Aplicación:** Detección de facciones políticas, segmentación de audiencias y localización de zonas de consenso (la "Táctica Polis").

## **3\. Consideraciones de Implementación (Software Engineering)**

1. **Manejo de Memoria:** Dado que la matriz ![][image11] es altamente dispersa (la mayoría de los usuarios no opinan de todos los temas), el módulo matrix\_builder\_core debe implementar estructuras de datos optimizadas (ej. scipy.sparse.csr\_matrix en Python) para evitar desbordamientos de RAM (OOM errors) durante las operaciones de SVD y KNN.  
2. **Desacoplamiento:** Cada *Crate* debe exponer una interfaz estandarizada (ej. funciones que reciben y retornan pandas.DataFrame o tensores). Esto permite actualizar el motor LLM en el Crate 2 sin afectar la lógica matemática del Crate 4\.  
3. **Procesamiento Asíncrono:** La ingesta y la inferencia NLI (Crates 1 y 2\) son procesos dependientes de I/O y latencia de red. Deben diseñarse con flujos asíncronos (asyncio), mientras que los cálculos matriciales (Crate 4\) son dependientes de CPU y pueden paralelizarse.

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAYCAYAAADKx8xXAAAA+0lEQVR4Xu1RqwoCQRTd5CP4CFqWnX3L4gb/wKbRZrL5IUYxG/wTQdBkEMRisAiCzS8QNIjouetdGAecbNgDB/aex87dHcPIoIdt233HcV7gEzyCK/DK2gPcIrNm/yWEaCdFDHNw5Pt+JX2Z67pLClmW1Ug1z/Na0G6madaMMAzLGBapyaUCBcCTrBOgHZIHhIYYBrKJtbq85kzWcXoR2iodGjg1LwdgjqlI3y7rcRznoDdl7QswN1TENlXV+4koikooPVDaqZ4WWK/Ha05UTwucNOViR/W0QGkP3ulKVO8nEHb5Gj6/XAdcRZ2CzAsXiWfSgiAQaifD3+EN50VCY79qhP8AAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAAYCAYAAAD3Va0xAAABHElEQVR4Xu2TvUoDURSEk2AT0phqm/2zMw8gFiksbNLZWJk38AlsLCwCpg6pUlrYCXaBgIZ0WmjnGwTBRm2EIEG/owfhzia2FmZgYPd8s3P3XnZLpZX+RmmaNrMsG+FX/IHf8jyf4Ba4DB8ye3A2Z36Lu9rzI0IXHt5YwA6MUXCkTFUm+ITvFJiYn1lRkiRbygKx0raveKoMrcFe8CPXFYWBCB1bEeexq4zyHd/yubKC7HA9/JsP9blAlKx78EqZifnYeUNZILazb0EKT5RFUVSDzfFUWUGE+la05Hz2/G0GygrKvj+2WRzH1QWs50VtZYFYcdOD18pMzO/9bevKvmTfDfCG0LsXTfHIt1eBX3L/7Mxsv1BHe1b61/oEqzRduiuaDboAAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAAXCAYAAAD+4+QTAAAAuUlEQVR4XmNgGAUDBZSUlPhlZGSE0MWpARiBBqvKycmlysvLXwPiInQF+AAzUMM8dEF0oKCgsBKo7ggQLwbi/yRZYmxszArUsBldHBcAWmZBsiUqKirsNLcEqIlj1BJ0OTAASlyAKiAWN6ObgWRJMbocTkCBT+hiSQm6HE5AgSWl6HI4AamWANU6giwB6mtEl8MJiLUEqK4AqO4qEP+F+gSEzwDLshnoajEAsZZQDGRlZU3QxUbB8AAAVqRQS+DiXg0AAAAASUVORK5CYII=>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAAXCAYAAAD+4+QTAAAAk0lEQVR4XmNgGAUDBZSUlPhlZGSE0MWpARiBBqvKycmlysvLXwPiInQFFAMFBYWVQIOPAPFiIP5PE0tgAGiZxaglRINhaUkxuhwYANO4DVByN5F4m6ioKA+6GQQtoQZAsqQEXY5qAMmSUnQ5qgGg4Y4gS4CWNaLLUQyAhhYADb8KxH+hPgHhM8B4noGudhSMAuoDAI0COjwG7iyPAAAAAElFTkSuQmCC>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAWCAYAAAD5Jg1dAAAA9klEQVR4XmNgGHigoKAgIS8vPxeI98vJyZ0E4lR0NQxSUlIiQIWXgIqyQHxlZWVZIPs2UKwBRSFQsBekEFkMyM8Air8xNjZmhQsCBR4AJVYiqQOJOQHxf1lZWVuwANRt/4H0TGSFQDcag8SBuAYsANRhAhWYgqxQRkZGFyQO1DAfLAA0yR6bQqACLaj4ErAAkGGJTSGQrwkSBxq0ECwAChqowrnICoFOMoWK18IFgdbcAgqsRVIHMtETqtALWbAFiG8CmYxIYqVA/BwlHIHu4AAKHgXSASA+0MecIFuAOAauCAaAkkJAhRVAyQVATbOAOBBdzcgDAOujQWUQDGB3AAAAAElFTkSuQmCC>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAF0AAAAYCAYAAACY5PEcAAAEnUlEQVR4Xu2Ya4hVVRTH74xTUvawYhqdx933zkxNTWHJJEQFkVGaGZRPJJTQij6YMVihklYOEz7SYuiplaESiAyi4IcY9YNpUUT2raAvUqBEUEFglAzT7+/ZO/dd3pl758LgyJw//Nlrr7X2a5191t7nZDIpUow08vn8FOfcYTgA3w36bDa7mPrf8Gwul+uM25QD2j0CT8B/YJ/nT3BfU1NTvfUfcyAI0wjypwTkj7q6uglBT7A3wlti3+GA/l6CR4yuj7E+iHVjEtrJDQ0NNxCQX+CyoEfeFvvV19dfie/dsU7QQ6utrb3K6mnfC9ca3Xf0sSHWXXLwwdKrexoe8rJe6W/hSdjPIvdTPoF7lW0vYH8tlPgd9+oa5K3nvRKg6yHId0X1qfCdzIV9V6P/DU4PCuQHNKeWlpYbY8cCkO/uwOlLeBYO8Fr8bH1iYJ8tP88f4XvWZ6Sg3dPc3JxtbGy8HvnDoGcOS5nXMz6gu+I2HgpOlwSC0YTcT1Bvp819tFlonQV8VmK/TakH+UVrF7Dd6ZKHvx6upb6a8pXW1tZa61sUDLCDBscVzPb29sutXcDnOuxr5AM3W/tIgzG7CXgri5uEvCW2hYegXKqDM7a5ZKfOjep7YY8CpL5i3xjYt8I3rT4A20p4zOrLBo1P+Cc1wMJusnYB+yJNVD7IM619KCgf0m69DjP4uTt/2vfR1+PWvxjcEEGn/olK+l6APCe2oXsh3n08lIfx+Qvujv1i0KYZ+3bK9zWmtQvY97ki6aksaGcoGHrVfEBnWB8thMEbKI/AMzpwrM9gICXcTJ9HGeNBaxsOGLdriKB/pJIx3kC+NbbhvzGugyp8fnCDpEatk35eRayB1cjrOFcajZtS1u/Y5ht9eWBSnTReAjt80J+L7W1tbVdjm6cS+7+wL7aXgA6rL5RDrWG4YF6vFws68pNwUy7J6Tsjf+Xj3fAM7A56b+vMFc/nNQpypvDQrNLYIe3S13TqBxQr2KtzMfItD+pAl3l25LU+6AXXHeqrKcZhm+UHKrgiDQUWsAIutvpKoIXrtVfQ4VHm8Rn1t11yDTyGbhUP5QrbbtSho6PjMib8Vagjn2Lye0Id+Sm9Ad62SUGnfm+wlwL+H1NUW30lUNDpL6+gU26hnKFAM5+H7EYZ1WCy97vohNYOgt9I1pcbtuXBpocD/8wkua4sEJCvXXRoFiM+C2y7YsC3K5fg//RCuRPm4a6KXvOLAS2ERc8O9az/VPa2p/UmSOb0v8Yld/ne4FsO8D9I2/FWXwnoq5vAujjoOuCo79HHCLrDl0R60U5UQKP6Opfk9YXxfRfdo9Jjfz7oygH+z9JuqdVXAgXdB9kepMvhXMZ6zA1yIxk10KcukzyJOC7omPiSYsHVYqTX9S/Wl4J2OUE6YD9YKgH9bGAOk3XnZn5vRSbdLvb729VmbC9HttEBBdvn2n4FEp4KKQb5HpdcCc8dflqcS24H8jvnC3sKOiwBAjJRKUBvkXaptZeCTx3h34t+0er/y6/S6beAfLLJdfd7b9c8C66IYxYuSVHbfQDjL9JF1jdFihQpUqRIkSLFxcR/hC5KM2U99VEAAAAASUVORK5CYII=>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAAYCAYAAAD3Va0xAAABQElEQVR4Xu2Qr0tDURzFJ8iKP7A8nuDj/YAHb7xkGjjEYDAsmU2u+Ads1bJisQ2DQTCYZMEkbKwtDRkIBrW5omlpYcWwfe64m/d9n8sr78Dh3XvO+d7v4eVyGVYDz/NKsAO/4AT2ZMZ13Rb6r/Z/fN+vy8wChNuEBiocBEFR+uhVMvdST8C27Q2CH2w611ufZAbtBh5LPQEanBBqxHGcN1pFZoYlL8o3tRQYvCZ4qs813aox93mUq/f8N7EEhPphGG6rs2VZm9yHcMTjO0rj31xwryanBNhmM9A1NQavdKuauuM/wn0zkwLhM3hpagztoo3hdxRFW3w/Tf9fELqDJanT6la3elCUfgqE3vmsS51WBf3QhHNF+gkQKsNXjmvSU8Brqoccx9mT3gzUPiTQn2+EA376kcyhH9DmTeoZMoApq+NPyBGhdEQAAAAASUVORK5CYII=>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAYCAYAAAAlBadpAAAA8klEQVR4XmNgGAXkA1lZWVN5efndQPwOiP8D8XUof7ecnNxBkDiQni8lJSWCrhcOgIqWgTQDDdNBE9cE4m8gw5DFUQBQ8jEQP0EXBwGg+EWQwYqKiurocgxAQT2okxejy4mKivJAbf4GdL4gujzI5FKo5iR0OQUFhQyoXBO6HBgAFewCKZCRkVGBiYFsAYonAMVfAdntQCEmJC0QAHXWT6jpoFDeB1T8COrUWUBsiK4HDoAKfaEaMfxLEAA1TQJpBjoxHl2OIABqvAvVLIEuhxcAnawE1XgKXQ4nAGqyBmo6AcS/oP59Lg8JLC90taNgyAIANg1GJlOcRi0AAAAASUVORK5CYII=>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAAXCAYAAAAGAx/kAAABBklEQVR4XmNgGAUDAxQVFeXl5OQOysvLfwXi/1B8VkZGRhUkD2TPRhJ/D1ILFGZBMwYBZGVllaGKbwO5TEjiUkCxJ0AD4pDF8QKghnUgwxQUFAJAfBUVFXYgeyMQm6OrxQuAhjhBXbVPSkqKC0ivAbrEGl0dUQCo+SrUVYeAhriiyxMNgJpzoa5ajy5HNNDS0mIDGrAWiD8B8U9gzAmhq8ELQIEK1LgaiINBfKC3NKCuusxAbEwZGxuzgrwB1OyBLA704k5oWEUgi2MFysrKYiBDgLgXXQ4oFgR11Xl0OTgA2hYCVHAGiH9BFb8EitnA5IH8HCB+D5X7D5Q7CaSnIpsxCkY8AACmsUbleOA76QAAAABJRU5ErkJggg==>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGMAAAAYCAYAAADu3kOXAAAEFklEQVR4Xu2YWYiOYRTHX/saWcZolu/9ZhEmNxpbSChLskwoLkRxQdmiXLiwRbayZMIFc0GDNMZ6IRkTQhS5sIyIG1uWmtCkGYnfMecdjzPzNd8wM5+a91+n93nO/zznOc951u/zvBAhWgp83y9EniCXkYfIFy2LVCLjbZsQTYDk5OQuJPs4xbZSj0aj26mfCXjKOzMyMvyaBiGaDiQ/Lz09fUhQJ/lXI5HISqe+hU+roN6iQHKWkIAfKjfkqCA51/iWIR8dTuSAbd9QZGZmRoKy7pJKd3KysrLSg3ItyJbR4CqcoO6lpaX1E57yIUdfLraebsHmAgkdS9+3kW8aR4XGPE75jpRvIt+Vf41urXCaEDm/f9Dm4J+ePS8lJaUztpPg3yAXVN1Kysgn9SdSht0Ity26Aod/CT/H5elvgvjwGpovZi9LnT6j2trRp6B7heP5rj4RYLDXJUZ39bmA3wGfb/UsuGG+ThTjmW55gU7IfaOboTk57OodtJY25GaaJQS03+T/nuCGgYanpXOc5Ek9Ozu7A+VzyHBr29xgwD2I7RvfO5YLAH8FGWj1Atqt18S+Z3KSLS+AKzP1wdrmoqsPgM/lcJutPgBcSVR3aINB4/HaealsX76n6HCUtUsEiGWmxMbgNlpOoMfRQ6t3IKu4VMdXaEkBY53Hp01QZzF2U/s/JklAHH3FnxfjCNL8fcVurOXiBg4e6aCvy5ln+fpAm9k6gHilKikpqav1Y4FdvthHzbkdQI+UXVbvIjU1NQ2bd+In1tFige1bpNIzLyB0R9lh/V2dgD56wa1Djmm855HF1i4u6NaTJNW8jf8HEM9jpNyLcW/JZMW6D1xgN0XH98KL4csFdrfE3j3ayNFUdKtdu0ZHTk5OezopRj4jlbyoelqbRIDBZ0pC+J61XAD4MjlWrN5C757n8d6D2B7XyRgmdR4P3UXnNeVvhWAiCHIBAe/R1bPM2iUCwW6NOD+eXLBosuFLrN5CHiTYlUbNEzQA3E7PuTME9LlVczFTbXbTPuraNCo0yCJkltTpa4AG8MCLYyu7+Is7o6K+FY3Pg2LLMTTUcgLi3SH9Wr0Fdkew22D1Crng67qoF0vftFvBdySyyNo0GnJzc9vRwRk6nezq6fySBIF+rqtPBPzqC1EmY5DlOD7GEOM5q7fAZhU+Tlh9ABlnpI5nM/4n6qLZB7/N8o0Gfpr3kYnw63iF+PqU9M0PoURA/g0gjo8kY6+jboNuKVIkz0hHXwvYrEFu4qeT5eR4lomA/4AUWx5dhuSBvp/ST2/L/zP0KLmLVGnC36EbHfDUlyHlykkgd/jud300N3RCCkjcSd21JchCr56LNFr9V8qvccQhtX69e9XHVxV+JlkiRIgQIUKECBEiRIgQNfgJDQ1ZNN1RzRAAAAAASUVORK5CYII=>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAYCAYAAAAVibZIAAABhUlEQVR4Xu2SPyxDURTGG8VAEFOTp++9tnk0eQPDMzEYCSaRNBYxGAwMxgoWiyCRGLrWarBYJQYJwmI1CklXJgMRfkfvbW5vn80ieV9ycs8533e/+zeVSvD/kM/nR3zfvyY+iC/P855sjQn4WdGpeCAqtqYBxFUEVyIOw7DT5gVo+uE3lOG+zbcA0X0ulyvLhGw2O2jzAvgF+E3RkE/ZfBO4gmF2cYywpCZM2hr6cyw2wHhBvDmO02VrmoDJOqaLRKRMV0y+WCz2wM3LCP9OnJt8LDA5c13XKRQKfcp01+LLDGm4aXWfWybfgiiKOhDd6Jq8hsmJrsmX5ASK2xNT6nHNx4JJEwgPjPqSuJM8k8l0w61qThYnXknbdS8WiHbk7+laHozei+KW5SSSB0HQ69f/8qnW/gpMbmWCUW/LEdltSX6F7tObUUdf071Y8DijCB9J07onvyBuMr2K9HnMIbPfgJjJDhF9ipCo6SsgH/PrX6ZNavqH1M9K96MljpoMEyT4e3wDwQtoqENtvs0AAAAASUVORK5CYII=>