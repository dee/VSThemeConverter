# VSThemeConverter

This script converts Visual Studio editor color schemes into ones for Qt Creator.

Before (VS 2022):\
<picture>
    <image src="doc/vs_coding_horror.png" width="600" />
</picture>

After (QtCreator):\
<picture>
    <image src="doc/qc_coding_horror.png" width="600" />
</picture>

# Usage
python main.py <file or directory with *.vssettings>

Automatically detects existing QtCreator instances. At the moment only Windows is supported.
`%APPDATA%\Roaming\QtProject\qtcreator\styles`


Work in progress.
