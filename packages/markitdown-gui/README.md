# MarkItDown GUI

Interfaz gráfica para la librería [MarkItDown](https://github.com/microsoft/markitdown). Esta aplicación permite realizar conversiones masivas de archivos a Markdown de forma sencilla.

## Características

- 🌑 **Tema Oscuro Moderno**: Interfaz elegante basada en `customtkinter`.
- 📂 **Selección Múltiple**: Selecciona uno o varios archivos a la vez.
- 🖱️ **Drag & Drop**: Arrastra archivos directamente desde el explorador de Windows.
- 🔄 **Conversión en Lote**: Procesa todos los archivos seleccionados en un hilo separado para no bloquear la interfaz.
- 📁 **Organización Automática**: Guarda los archivos `.md` en la misma carpeta que los originales.
- 🛠️ **Filtros Inteligentes**: Filtros específicos para documentos, hojas de cálculo, imágenes, audio, etc.

## Requisitos

Si se ejecuta desde el código fuente:
- Python 3.10+
- `customtkinter`
- `tkinterdnd2`
- `markitdown` (y sus dependencias opcionales de conversión)

## Instalación y Uso

1. Instala las dependencias:
   ```bash
   pip install customtkinter tkinterdnd2
   pip install -e 'packages/markitdown[all]'
   ```
2. Ejecuta la aplicación:
   ```bash
   python packages/markitdown-gui/markitdown_gui.py
   ```

## Compilación a Ejecutable (.exe)

Para generar el archivo ejecutable autónomo:
```bash
python packages/markitdown-gui/build_exe.py
```
El archivo resultante se encontrará en `packages/markitdown-gui/dist/MarkItDown.exe`.

## Extensiones Soportadas

Soporta todas las extensiones de la librería MarkItDown, incluyendo:
- **Documentos**: PDF, DOCX, PPTX, EPUB, MSG
- **Hojas de cálculo**: XLSX, XLS, CSV
- **Media**: JPG, PNG, MP3, WAV, MP4, etc.
- **Datos**: JSON, XML, IPYNB
