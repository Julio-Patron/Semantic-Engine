# 🧠 ESTADO E INVENTARIO SES (Semantic Engine System)

> **Documento maestro unificado** de revisión de arquitectura, estado actual del proyecto, limpieza de deuda técnica e inventario del repositorio tras consolidación.

---

## 1. Resumen Ejecutivo

**SES Core** es un motor RAG (Retrieval-Augmented Generation) avanzado, diseñado con una filosofía **"offline-first"** rigurosa. Permite procesar repositorios documentales corporativos privados (NAS, SAN, discos locales) extrayendo el contenido sin alterar ni reubicar la información original. Su ecosistema completo garantiza 100% de la privacidad del dato al utilizar LLMs y bases vectoriales enteramente operadas en la infraestructura del cliente. 

El proyecto goza de una ingeniería moderna, combinando un núcleo Python con una API de FastAPI, administración en React/Next.js y una aceleración de memoria zero-copy en Rust. Actualmente cursa una etapa de **Beta Técnica**.

---

## 2. Análisis Arquitectónico y Diagrama de Flujo

El sistema opera bajo un ecosistema de servicios distribuidos localmente, donde el motor semántico actúa como cerebro orquestador:

```mermaid
flowchart TD
    subgraph Archivos Corporativos
        NAS[(Archivos Originales\nSolo Lectura)]
    end

    subgraph SES Core (Núcleo Python + Rust)
        Watcher[Watchdog / Scanner Incremental]
        Extractor[Extracción de Texto y Chunking]
        RustCore[jas_vector_core\nAceleración Rust Coseno]
    end

    subgraph Dependencias Locales (Docker)
        Qdrant[(Qdrant\nBase Vectorial)]
        Redis[(Redis\nCaché y Telemetría)]
        Ollama[Ollama\nMotor LLM Local]
    end
    
    subgraph Capa de Presentación
        Gateway[Enterprise Gateway\nFastAPI / SQLite]
        Portal[Enterprise Portal\nNext.js 16]
        SDK[SDKs\nTypeScript / Go]
    end

    NAS -->|Solo Lectura| Watcher
    Watcher -->|Nuevos / Alterados| Extractor
    Extractor -->|Embeddings| Qdrant
    Extractor -->|Contexto| Redis
    
    Portal --> Gateway
    SDK --> Gateway
    Gateway <-->|Búsqueda RAG| Qdrant
    Gateway <-->|Caché / Límite| Redis
    Gateway <-->|Generación| Ollama
    RustCore -.->|Re-ranking >50 docs| Qdrant
```

### Concepto Clave: Mount Mode (Modo de Montaje)
El mayor valor diferenciador es el diseño no invasivo del *Filesystem Connector*:
* **No Intrusivo:** Accede en *solo lectura*. Qdrant indexa vectores e identificadores pero nunca secuestra el archivo.
* **Trazabilidad (`source_path`):** Conserva la ruta absoluta del origen para permitir auditorías exactas de referencias en la respuesta.
* **Eficiencia (Hashing):** Sincronización "Delta". Analiza metadatos y firmas SHA-256 para evitar reprocesamientos si el archivo no cambió.

---

## 3. Inventario del Repositorio Consolidado

Tras la depuración de deuda técnica y ramas residuales, este es el árbol operativo de SES:

- 📂 **`ses/`**: Núcleo principal de Python. Controla chunking, embeddings, proveedores RAG, reportes y el monitor `ses/watcher`.
- 📂 **`gateway/`**: API FastAPI para control y acceso. Usa SQLite para guardar llaves de forma cifrada y generar telemetría analítica. Sirve un micro-dashboard en `/static`.
- 📂 **`portal/`**: Interfaz visual de administración construida sobre Next.js 16. Mantiene el estado localmente en el browser sin compilaciones riesgosas.
- 📂 **`core_rs/`**: Librería embebida en Rust (`jas_vector_core`) compilada mediante Maturin y PyO3, proveyendo re-ranking veloz directo en memoria.
- 📂 **`sdk/`**: Clientes en TypeScript (`@ses-ai/client`) y Go para facilitarle integración corporativa a los clientes finales.
- 📂 **`docs/`**: Base de conocimiento técnica principal, alimentando la Web oficial (`docs/site`).
- 📂 **`scripts/`**: Automatización del ciclo de vida (generación de secretos criptográficos `deploy_production.py`, verificación de checksums).
- 📂 **`tests/`**: Extensa suite (Pytest, End-to-End, benchmarking sintético y pruebas de fallos (Circuit-Breakers)).

---

## 4. Registro de Limpieza y Depuración (Changelog)

Se saneó la base del repositorio para facilitar el mantenimiento y evitar deudas técnicas:
* 🗑️ **Eliminación del directorio residual `doc/`**: No era rastreado en Git y causaba conflicto nominal y confusión con el real (`docs/`).
* 🗑️ **Limpieza del archivo obsoleto `tests/performance/.gitkeep`**: Removido por carecer de función alguna dado que la ruta ahora opera con código activo (`benchmark.py`).
* 🗑️ **Depuración de cachés y targets binarios**: Se eliminaron por completo `ses/__pycache__/` y `core_rs/target/`, previniendo que binarios desactualizados interfirieran con el entorno de los desarrolladores.
* 🌿 **Alineación de ramas de Git**: Revisión en local y en remoto de `git branch` para confirmar el enfoque centralizado exclusivo en `main`.

---

## 5. Próximos Pasos y Roadmap (Deuda Arquitectónica Pendiente)

El proyecto declara honestamente en su documentación las limitantes actuales. El camino para salir de la *Beta Técnica* requiere:

1. **Pruebas End-to-End Masivas:** Demostrar y documentar *Throughput* con repositorios de 40 a 60 GB comprobables, validando la estabilidad multihilo.
2. **Transacciones Distribuidas:** El ciclo "Manifiesto JSON -> Qdrant" en *Mount Mode* actualmente no forma una única transacción estricta. Si falla a la mitad, se maneja mediante encolado diferido (defer). Esto debe mitigarse o encapsularse.
3. **Validación con PostgreSQL:** Reemplazar o validar SQLite como fuente de telemetría y llaves para entornos altamente concurrentes y orquestados (Kubernetes).
4. **Validación de Conectores de Red Reales:** Extender explícitamente y probar el conector para entornos puramente NAS (SMB/CIFS) en lugar de depender únicamente del mapeo del Sistema Operativo.

---

## 6. Guía Rápida para Nuevos Desarrolladores (Onboarding)

Para inicializar tu entorno y continuar el desarrollo en este repositorio limpio, sigue estos comandos estándar provistos por los utilitarios internos:

```powershell
# 1. Preparar Entorno y Dependencias
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,server]"

# 2. Rotar Secretos y generar variables .env
Copy-Item .env.example .env
python scripts/rotate_local_secrets.py

# 3. Levantar dependencias core por detrás (Qdrant, Redis)
Copy-Item .env.compose.example .env.compose
docker compose --env-file .env.compose up -d

# 4. Iniciar Gateway (Backend) y Portal (Frontend)
python gateway/run.py
npm --prefix portal run dev -- --hostname 127.0.0.1 --port 3000
```