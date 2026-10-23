# Contexto del proyecto — Ordena

Actualizado: 23 de octubre de 2026.

## Objetivo y alcance

Aplicación gratuita de escritorio para Windows, Python/PySide6, para organizar manualmente archivos del primer nivel de una carpeta local. Inglés como idioma inicial y selector Español. La selección del usuario prevalece sobre el prompt original que pedía solo español. No importar archivos a una biblioteca interna. Confirmar vista previa antes de mover. No usar carpetas personales durante desarrollo.

## Decisiones técnicas

- Python 3.12.14 x64, PySide6 6.10.2 y PyInstaller 6.19.0 instalados en un entorno virtual; instalación global intacta.
- UI Qt Widgets oscura, tipografía Segoe UI y acento menta, coherente con los colores y separación de módulos observados en `wasatnight/FotoLista` (README y comienzo de `fotolista/ui.py` revisados). No se copió código de FotoLista.
- Traducciones en `i18n.py`; las reglas conservan nombres físicos independientes del idioma.
- Reglas validadas, extensiones únicas, nombres de Windows sin rutas ni nombres reservados.
- Planificador de solo lectura. Clasifica por extensión. SHA-256 se usa exclusivamente para comprobar integridad, leyendo bytes sin decodificar ni ejecutar el contenido.
- Movimientos en Windows mediante un handle abierto con lectura y DELETE, compartiendo solo lectura; verifica identidad, metadatos y hash; usa FileRenameInfo sin reemplazar destinos.
- Bloqueos de directorios con FILE_LIST_DIRECTORY, sin FILE_SHARE_DELETE. No basta acceso 0 para impedir reemplazos de directorios; la prueba real detectó y corrigió ese detalle.
- Identificadores de directorio guardados como texto porque los identificadores de Windows pueden exceder un entero SQLite de 64 bits.
- SQLite synchronous=FULL. Intención persistida antes de mover, estado después. Deshacer reconcilia operaciones pendientes interrumpidas, también interrupciones tras restaurar pero antes de confirmar el registro.
- QThread para análisis/movimientos/deshacer; cancelación mediante threading.Event. No aborta un movimiento en curso; un hash de archivo grande debe terminar antes de cancelar.
- Preferencias JSON con reemplazo atómico. Directorio de datos por usuario Qt AppLocalDataLocation; variable ORDENA_DATA_DIR para aislamiento. QLockFile limita una instancia por directorio de datos.

## Funciones terminadas

Selección y arrastre de una carpeta; tabla de vista previa; tamaños y totales; categorías con conteos; exclusión individual y por categoría; edición de categorías/extensiones; validación; conflictos con nombre disponible mostrado antes; confirmación explícita; progreso; cancelación; errores por archivo; resumen parcial/completo; deshacer persistente y conservador; preferencias de idioma/reglas/carpeta; scripts para configurar, probar y empaquetar; README en inglés y español; capturas de interfaz y pruebas automatizadas.

## Verificación

Consultar VALIDATION.md para resultados reales. Las pruebas crean exclusivamente datos sintéticos en TemporaryDirectory. Se verificaron Unicode, mayúsculas, colisiones, archivos bloqueados/cambiados/desaparecidos, cancelación, integridad y deshacer después de una interrupción real de otro proceso. También se probó la integración de la interfaz.

## Comandos para continuar

Desde esta carpeta, con Python 3.12 instalado:

```powershell
.\setup.ps1
.\.venv\Scripts\python.exe main.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\build.ps1
```

En esta sesión concreta el entorno está en `..\..\.venv`, fuera de la carpeta del código para no incluir dependencias en la entrega. El script admite `build.ps1 -Python RUTA_AL_PYTHON_DEL_ENTORNO`.

## Pendientes

- Probar enlaces físicos/junctions reales en un Windows que permita crearlos; el sandbox bloqueó su creación y esas pruebas se omiten con explicación.
- Validar en un Windows limpio y en carpetas grandes/unidades externas; revisión de accesibilidad adicional.
- Definir licencia del código propio con el autor. Gratuito no implica por sí solo licencia de código abierto.
- Instalador, firma Authenticode y eventual distribución certificada.
- Fuera del alcance actual: vigilancia automática, ejecución en segundo plano/inicio con Windows, recursión, IA, eliminación de duplicados, nube y donaciones.

## Estado para otra sesión

Código y pruebas completos en esta carpeta, con empaquetado portable disponible en `dist/Ordena`. Repositorio público creado: https://github.com/wasatnight/Ordena. El conector de GitHub respondió 403 al intentar escribir en el nuevo repositorio; se usa el navegador autenticado para subir el código. No hay claves ni credenciales dentro del proyecto. El historial y preferencias de prueba se mantuvieron fuera del código entregado.
