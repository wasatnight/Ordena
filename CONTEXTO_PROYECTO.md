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

- Enlaces físicos y junctions verificados en CI Windows: 35 pruebas aprobadas sin omisiones. Falta verificar enlaces simbólicos reales y más variantes de sistemas de archivos.
- Validar en un Windows limpio y en carpetas grandes/unidades externas; revisión de accesibilidad adicional.
- Definir licencia del código propio con el autor. Gratuito no implica por sí solo licencia de código abierto.
- Instalador, firma Authenticode y eventual distribución certificada.
- Fuera del alcance actual: vigilancia automática, ejecución en segundo plano/inicio con Windows, recursión, IA, eliminación de duplicados, nube y donaciones.

## Estado para otra sesión

Código y pruebas completos en esta carpeta, con empaquetado portable disponible en `dist/Ordena`. Repositorio público creado: https://github.com/wasatnight/Ordena. El conector de GitHub respondió 403 al intentar escribir en el nuevo repositorio; se usa el navegador autenticado para subir el código. No hay claves ni credenciales dentro del proyecto. El historial y preferencias de prueba se mantuvieron fuera del código entregado.

La validación independiente de Windows terminó correctamente: 35 pruebas aprobadas, compilación y arranque sin Python en PATH. Ejecución: https://github.com/wasatnight/Ordena/actions/runs/39929305957. El ZIP portable de la entrega proviene de ese artefacto verificado; la compilación local no pudo confirmar arranque en el sandbox. Repositorio publicado completo y copia de código local comparada con el árbol remoto.


## Actualización 1.1.0

Solicitud del usuario: icono propio, acento rosa casi blanco, título centrado con subtítulo del mismo estilo debajo, selecciones estables y ayuda en un botón ?.

Implementado en `theme.py`, `controls.py`, `help_content.py` y `ui.py`. La selección ya no invoca `render()` para reconstruir la tabla; `update_selection()` actualiza casillas, estados y conteos en los mismos objetos. Se probaron clics reales con QTest, teclado, scroll conservado y selección parcial. El botón ? abre ejemplos localizados sin conexión.

Icono vectorial original en `ordena/assets/app.svg`; generador de ICO/PNG en `tools/generate_icons.py`; ICO con nueve tamaños. Se aplica QIcon a la aplicación/ventanas, AppUserModelID a Windows y --icon/--add-data al empaquetado. `tools/verify_build.py` compara los recursos RT_ICON del EXE con las imágenes originales del ICO. El smoke test confirma versión e iconos empaquetados en smoke.json dentro del directorio de datos de prueba.

Pruebas: 44 en total (17 de interfaz). En el sandbox local se omiten las dos pruebas de creación de enlaces por restricciones del entorno; todas las pruebas de interfaz están aprobadas. Los resultados del nuevo runner Windows se registran en VALIDATION.md. El motor de movimientos y el registro persistente no han cambiado.

Cierre de la versión 1.1.0: 44 pruebas aprobadas en Windows sin omisiones; compilación, nueve iconos incrustados y arranque sin Python en PATH aprobados. Ejecución https://github.com/wasatnight/Ordena/actions/runs/39935344875; código probado 0a357bfac82a673d993930f7f2c47f6ea3b3d0d7; artefacto 12494005484. La entrega usa los binarios de ese artefacto, con documentación actualizada, sin modificar EXE/DLL/PYD. El código completo está publicado en main, incluidas fuentes vectoriales del icono, generador y verificador. Las últimas modificaciones posteriores al código probado son solo este contexto y el informe de validación.
