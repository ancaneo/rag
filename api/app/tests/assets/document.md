# RAG
Aplicación Python de Recuperación de Generación Aumentada  (RAG por sus sigla en inglés: Retrieval-Augmented Generation) que permite inyectar datos de documentos y responder preguntas usando LLM (Gemini) y visibilidad mediante Langsmith.

## Claves secretas
Las siguientes claves debe inyectar en .env. Es fundamental ingresar estas claves antes de la ejecución del proyecto.
- LANGSMITH_API_KEY: Clave de langsmith. Puede obtener una en https://smith.langchain.com/
- GOOGLE_API_KEY: Clave para usar en Gemini. Puede obtener una en https://aistudio.google.com/api-keys

## Otras variables de entorno:
- LANGSMITH_TRACING: Booleano (True o False) para indicar si se realiza rastreo de las llamadas a LLM.
- USER_AGENT: User agent que se desea usar para las llamadas web desde el LLM.

## Microservicios
El proyecto cuenta con 2 microservicios:
- db: Instancia una base de datos PostgreSQL con PGVector para el almenamiento de vectores.
- api: Instancia una api de FastAPI para responder a las llamadas de inyección de nueva información de documentos PDF, HTML, MDy  TXT como de páginas web; y responder a preguntas de aquella información.

Ambos servicios se levantan ejecutando con docker compose, que en v2:
- docker compose build api: Para crear la imagen de api. db no necesita creación de imagen ya que usa capa definida por pgvector.
- docker compose create [servicio: api y/o db]: Para crear la instancia del microservicio.
- docker compose start [servicio: api y/o db]: En cuanto api depende de db, si se levanta api, db se levantará automáticamente si no está corriendo ya.

O bien si se prefiere puede usar el comando up que crea imagen, contener e inicia.

Para detener un servicio:
- docker compose stop [servicio: api y/o db]

O bien use down si se quiere remover instancia, imágenes y volúmenes al momento de detener servicio.

La API es accesible en http://localhost:8080/docs
