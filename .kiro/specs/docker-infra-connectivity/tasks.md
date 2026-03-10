# Tareas de Implementación

## Tarea 1: Agregar MySQL como dependencia de Airflow en x-airflow-common

- [x] 1.1 Agregar `mysql` con condición `service_healthy` al bloque `&airflow-common-depends-on` en `docker/docker-compose.yaml`, junto a las dependencias existentes de `redis` y `postgres`.

## Tarea 2: Agregar servicio MinIO al docker-compose

- [x] 2.1 Agregar el servicio `minio` en `docker/docker-compose.yaml` con imagen `minio/minio`, comando `server /data --console-address ":9001"`, puertos `9000:9000` y `9001:9001`, variables de entorno `MINIO_ROOT_USER` y `MINIO_ROOT_PASSWORD`, volumen `minio_data:/data`, healthcheck en `/minio/health/live`, y `restart: always`.
- [x] 2.2 Agregar `minio_data` a la sección `volumes` de nivel superior en `docker/docker-compose.yaml`.

## Tarea 3: Configurar servicio Jupyter con conectividad, healthcheck y limpieza de volúmenes

- [x] 3.1 Reemplazar los volúmenes no declarados (`shared_models`, `shared_report`, `shared_data`, `shared_results`) del servicio `jupyter` en `docker/docker-compose.yaml` con bind mounts relativos (`../models:/app/models`, `../report:/app/report`, `../data:/app/data`, `../results:/app/results`).
- [x] 3.2 Agregar las variables de entorno de MySQL (`MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`) y MinIO (`MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`) al servicio `jupyter` en `docker/docker-compose.yaml`.
- [x] 3.3 Agregar `depends_on` con `mysql` y `minio` (ambos con condición `service_healthy`) al servicio `jupyter` en `docker/docker-compose.yaml`.
- [x] 3.4 Agregar un healthcheck al servicio `jupyter` en `docker/docker-compose.yaml` que verifique el endpoint en el puerto 8888, con interval, timeout, retries y start_period configurados.
- [x] 3.5 Agregar `restart: always` al servicio `jupyter` en `docker/docker-compose.yaml`.

## Tarea 4: Configurar penguin-api con conectividad hacia MinIO

- [x] 4.1 Agregar las variables de entorno de MinIO (`MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`) al servicio `penguin-api` en `docker/docker-compose.yaml`.
- [x] 4.2 Agregar `depends_on` con `minio` (condición `service_healthy`) al servicio `penguin-api` en `docker/docker-compose.yaml`.

## Tarea 5: Crear archivo README de documentación

- [x] 5.1 Crear el archivo `docker/README.md` con descripción general de la infraestructura, tabla de servicios (puertos, propósito, dependencias), diagrama de conectividad, reglas de conectividad, variables de entorno por servicio, e instrucciones de uso con Docker Compose.
