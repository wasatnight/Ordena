# Ordena 1.1.1 — Español

Aplicación gratuita de escritorio para Windows que organiza una carpeta local. **Se abre inicialmente en inglés. Selecciona Español arriba a la derecha para traducir la interfaz.** Recuerda idioma, reglas y última carpeta seleccionada.

## Abrir

Extrae todo el ZIP portable y abre `Ordena/Ordena.exe`. Conserva `_internal` junto al ejecutable. No requiere Python ni permisos de administrador. Esta primera compilación no está firmada y falta probarla en un Windows limpio.

## Usar

1. Selecciona una carpeta o arrástrala a la ventana.
2. Revisa archivos, tamaños, destinos y estados de la vista previa.
3. Desmarca archivos o categorías. Usa **Editar categorías** para cambiar nombres y extensiones.
4. Pulsa **Organizar** y confirma la carpeta y cantidad.
5. Revisa el resumen; **Deshacer última organización** funciona incluso después de cerrar y volver a abrir.

Solo analiza archivos del primer nivel. No recorre subcarpetas. Deja los archivos sin categoría en su ubicación. El idioma de la interfaz no cambia los nombres físicos de las carpetas; para destinos como «Imágenes» o «Documentos», edita sus nombres en las reglas.

No sobrescribe archivos. Los nombres repetidos se resuelven en la vista previa. Si aparece una nueva colisión, el movimiento se omite y debes actualizar la vista previa. Omite ocultos, archivos de sistema, enlaces, accesos directos y descargas incompletas. Rechaza raíces de unidad y carpetas protegidas. La clasificación usa solo extensiones; las sumas SHA-256 leen bytes para detectar cambios, sin interpretar ni ejecutar su contenido.

Cancelar detiene los siguientes movimientos cuando termina la comprobación del archivo actual. El registro de los movimientos completados queda disponible para deshacer. La restauración verifica la identidad y contenido del archivo; si la ubicación original está ocupada o el archivo cambió, lo deja intacto e informa el conflicto. Puedes reintentar. Solo elimina carpetas vacías creadas por esa operación.

Preferencias y registro se guardan bajo Local AppData, en la ubicación por usuario de Qt `IvanSolano/Ordena`. No borres el historial si aún necesitas deshacer. No usa internet durante su funcionamiento.

## Desarrollo en Windows / VS Code

Instala Python 3.12 de 64 bits y abre PowerShell en esta carpeta:

```powershell
.\setup.ps1
.\.venv\Scripts\python.exe main.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\build.ps1
```

Selecciona `.venv` como intérprete en VS Code. `build.ps1` genera `dist/Ordena/Ordena.exe`; distribuye la carpeta completa. Puedes pasar `-Python RUTA_AL_PYTHON_DEL_ENTORNO` al script de compilación.

Consulta [VALIDATION.md](VALIDATION.md) para conocer pruebas y limitaciones, [CONTEXTO_PROYECTO.md](CONTEXTO_PROYECTO.md) para continuar el proyecto y [README.md](README.md) para los detalles técnicos. No se probaron carpetas personales. Quedan fuera de esta versión vigilancia automática, inicio con Windows, recursión, IA, eliminación de duplicados, nube y donaciones. Instalador, firma de editor y prueba en otro Windows están pendientes.

Referencia de la versión 1.0: **35 pruebas aprobadas, compilación y arranque del ejecutable sin Python en PATH**. [Ver ejecución en Windows](https://github.com/wasatnight/Ordena/actions/runs/39929305957). El portable entregado proviene de esa compilación.


## Novedades de esta versión

Icono original en ventana, barra de tareas y ejecutable; acento rosa casi blanco; nombre centrado con subtítulo debajo; casillas visibles y estables; menú de idioma con contraste uniforme. Ya no se resalta toda una fila al pulsarla. Pulsa la casilla o el nombre para incluir/excluir; también puedes usar Espacio. No se reconstruye la tabla en cada clic y conserva el desplazamiento. Un guion en una categoría significa selección parcial.

Las instrucciones se encuentran en el botón **?**, con pasos y ejemplos en el idioma elegido. El icono incluye nueve tamaños de Windows (16 a 256 px); sus fuentes están en `ordena/assets/` y se pueden regenerar con `python tools/generate_icons.py`.

Esta versión incorpora nueve pruebas de regresión de interfaz: 44 pruebas en total. Consulta [VALIDATION.md](VALIDATION.md) y las [ejecuciones de Windows](https://github.com/wasatnight/Ordena/actions) para los resultados de la versión actual.


## Ajuste visual 1.1.1

Toda la interfaz tiene fondos rosa claro y letras azules, incluidos tabla, menús, editor de categorías y ayuda. El subtítulo centrado dice «Tus carpetas ordenadas» en español y «Your folders, organized» en inglés. Se conservan distribución, icono, selecciones estables y ayuda.
