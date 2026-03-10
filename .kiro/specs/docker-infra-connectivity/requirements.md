# Documento de Requisitos

## Introducción

Este documento define los requisitos para mejorar la conectividad entre servicios en la infraestructura Docker Compose del proyecto MLOps. Actualmente, Airflow tiene configurada una cadena de conexión a MySQL pero carece de la dependencia explícita (`depends_on`) para garantizar el orden de arranque. Jupyter no tiene acceso a MySQL ni a un servicio de almacenamiento de objetos, carece de healthcheck y referencia volúmenes no declarados. Se requiere agregar un servicio MinIO, establecer las dependencias correctas entre Airflow y MySQL, conectar Jupyter tanto a MySQL como a MinIO, conectar penguin-api a MinIO, limpiar los volúmenes no declarados de Jupyter, agregar un healthcheck a Jupyter, y documentar la arquitectura resultante en un archivo README.

### Reglas de Conectividad

- Airflow SOLO puede comunicarse con MySQL (base de datos).
- MySQL puede ser LEÍDO por Jupyter.
- Jupyter puede acceder a MinIO.
- penguin-api puede acceder a MinIO.

## Glosario

- **Docker_Compose**: Herramienta de orquestación de contenedores que define y ejecuta aplicaciones multi-contenedor mediante un archivo YAML.
- **Airflow**: Plataforma de orquestación de flujos de trabajo (DAGs) desplegada como conjunto de servicios (webserver, scheduler, worker, triggerer).
- **Jupyter**: Servicio de notebooks interactivos para exploración y procesamiento de datos.
- **MySQL**: Servicio de base de datos relacional (MySQL 8.0) con base de datos `mydatabase`, usuario `user` y contraseña `user1234`.
- **MinIO**: Servicio de almacenamiento de objetos compatible con la API de Amazon S3, utilizado para escritura y lectura de datos.
- **Penguin_API**: Servicio de API REST para predicciones del modelo de pingüinos, desplegado como contenedor Docker.
- **Healthcheck**: Verificación periódica del estado de salud de un contenedor Docker.
- **depends_on**: Directiva de Docker Compose que establece dependencias de arranque entre servicios.
- **Red_Docker**: Red interna de Docker Compose que permite la comunicación entre contenedores por nombre de servicio.
- **README**: Archivo de documentación del proyecto que describe la arquitectura y configuración de los servicios.

## Requisitos

### Requisito 1: Dependencia de Airflow hacia MySQL

**Historia de Usuario:** Como ingeniero de datos, quiero que los servicios de Airflow dependan explícitamente del servicio MySQL con verificación de salud, para que Airflow no intente conectarse a MySQL antes de que este esté disponible.

#### Criterios de Aceptación

1. WHEN el servicio MySQL reporta un estado saludable mediante su healthcheck, THE Airflow_Common_Depends_On SHALL incluir a MySQL como dependencia con la condición `service_healthy`.
2. THE Docker_Compose SHALL definir la dependencia de MySQL en el bloque `x-airflow-common` bajo `depends_on`, de modo que todos los servicios de Airflow (webserver, scheduler, worker, triggerer) hereden la dependencia.
3. IF el servicio MySQL no alcanza un estado saludable dentro del período de reintentos configurado, THEN THE Docker_Compose SHALL impedir el arranque de los servicios de Airflow que dependen de MySQL.
4. THE Docker_Compose SHALL garantizar que Airflow SOLO se comunica con MySQL como servicio de base de datos externo (además de Postgres y Redis que son internos de Airflow).

### Requisito 2: Conectividad de Jupyter hacia MySQL

**Historia de Usuario:** Como científico de datos, quiero que el servicio Jupyter tenga acceso de lectura a la base de datos MySQL, para poder consultar datos directamente desde los notebooks.

#### Criterios de Aceptación

1. THE Docker_Compose SHALL definir las variables de entorno `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD` y `MYSQL_DATABASE` en el servicio Jupyter con los valores correspondientes al servicio MySQL (`mysql`, `3306`, `user`, `user1234`, `mydatabase`).
2. THE Docker_Compose SHALL incluir a MySQL como dependencia del servicio Jupyter con la condición `service_healthy` en `depends_on`.
3. WHEN el servicio MySQL está saludable y Jupyter ha arrancado, THE Jupyter SHALL poder establecer una conexión TCP al host `mysql` en el puerto `3306` a través de la Red_Docker.

### Requisito 3: Servicio MinIO

**Historia de Usuario:** Como ingeniero de datos, quiero que exista un servicio MinIO en la infraestructura Docker Compose, para disponer de almacenamiento de objetos compatible con S3 para el proyecto.

#### Criterios de Aceptación

1. THE Docker_Compose SHALL definir un servicio llamado `minio` basado en la imagen `minio/minio`.
2. THE Docker_Compose SHALL exponer el puerto `9000` para la API de MinIO y el puerto `9001` para la consola web de MinIO.
3. THE Docker_Compose SHALL configurar las variables de entorno `MINIO_ROOT_USER` y `MINIO_ROOT_PASSWORD` en el servicio MinIO.
4. THE Docker_Compose SHALL definir un volumen persistente para el almacenamiento de datos de MinIO en la ruta `/data` del contenedor.
5. THE Docker_Compose SHALL configurar un healthcheck para el servicio MinIO que verifique la disponibilidad del endpoint `/minio/health/live` en el puerto `9000`.
6. THE MinIO SHALL ejecutar el comando `server /data --console-address ":9001"` como comando de inicio del contenedor.

### Requisito 4: Conectividad de Jupyter hacia MinIO

**Historia de Usuario:** Como científico de datos, quiero que el servicio Jupyter tenga acceso al servicio MinIO, para poder escribir y leer datos desde almacenamiento de objetos compatible con S3.

#### Criterios de Aceptación

1. THE Docker_Compose SHALL definir las variables de entorno `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY` y `MINIO_SECRET_KEY` en el servicio Jupyter con los valores correspondientes al servicio MinIO.
2. THE Docker_Compose SHALL incluir a MinIO como dependencia del servicio Jupyter con la condición `service_healthy` en `depends_on`.
3. WHEN el servicio MinIO está saludable y Jupyter ha arrancado, THE Jupyter SHALL poder establecer una conexión HTTP al host `minio` en el puerto `9000` a través de la Red_Docker.

### Requisito 5: Healthcheck del servicio Jupyter

**Historia de Usuario:** Como ingeniero de infraestructura, quiero que el servicio Jupyter tenga un healthcheck configurado, para poder monitorear su estado de salud y que otros servicios puedan depender de él de forma confiable.

#### Criterios de Aceptación

1. THE Docker_Compose SHALL configurar un healthcheck para el servicio Jupyter que verifique la disponibilidad del servicio en el puerto `8888`.
2. THE Jupyter_Healthcheck SHALL ejecutarse con un intervalo, timeout, reintentos y período de inicio configurados.
3. WHEN el healthcheck de Jupyter falla consecutivamente según el número de reintentos configurado, THE Docker_Compose SHALL reportar el servicio Jupyter como no saludable.

### Requisito 6: Limpieza de volúmenes no declarados de Jupyter

**Historia de Usuario:** Como ingeniero de infraestructura, quiero que los volúmenes referenciados por el servicio Jupyter estén correctamente declarados en la sección `volumes` del Docker Compose, para evitar errores de arranque y mantener la configuración consistente.

#### Criterios de Aceptación

1. THE Docker_Compose SHALL eliminar las referencias a los volúmenes `shared_models`, `shared_report`, `shared_data` y `shared_results` del servicio Jupyter, ya que no están declarados en la sección `volumes`.
2. THE Docker_Compose SHALL reemplazar los volúmenes no declarados de Jupyter con bind mounts o volúmenes declarados según corresponda a la estructura del proyecto.
3. THE Docker_Compose SHALL garantizar que todos los volúmenes nombrados referenciados por cualquier servicio estén declarados en la sección `volumes` de nivel superior.

### Requisito 7: Conectividad de penguin-api hacia MinIO

**Historia de Usuario:** Como ingeniero de datos, quiero que el servicio penguin-api tenga acceso al servicio MinIO, para poder leer y escribir datos de modelos y resultados en almacenamiento de objetos compatible con S3.

#### Criterios de Aceptación

1. THE Docker_Compose SHALL definir las variables de entorno `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY` y `MINIO_SECRET_KEY` en el servicio Penguin_API con los valores correspondientes al servicio MinIO.
2. THE Docker_Compose SHALL incluir a MinIO como dependencia del servicio Penguin_API con la condición `service_healthy` en `depends_on`.
3. WHEN el servicio MinIO está saludable y Penguin_API ha arrancado, THE Penguin_API SHALL poder establecer una conexión HTTP al host `minio` en el puerto `9000` a través de la Red_Docker.

### Requisito 8: Documentación en README

**Historia de Usuario:** Como desarrollador del equipo, quiero que exista un archivo README que documente la arquitectura de servicios y las instrucciones de uso, para facilitar la incorporación de nuevos miembros y el mantenimiento del proyecto.

#### Criterios de Aceptación

1. THE README SHALL describir cada servicio definido en el Docker_Compose, incluyendo su propósito, puertos expuestos y dependencias.
2. THE README SHALL incluir un diagrama o descripción textual de la conectividad entre servicios (Airflow→MySQL, Jupyter→MySQL, Jupyter→MinIO, Penguin_API→MinIO).
3. THE README SHALL documentar las variables de entorno configurables para cada servicio con sus valores por defecto.
4. THE README SHALL incluir instrucciones para levantar la infraestructura completa con Docker Compose.
