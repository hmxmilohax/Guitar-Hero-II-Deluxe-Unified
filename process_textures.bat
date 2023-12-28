cd "%~dp0textures\xbox"
FOR /F "tokens=*" %%G IN ('dir /b *.png') DO "%~dp0dependencies/magick/magick.exe" convert "%~dp0textures/xbox/%%G" -resize 50%% -filter Box -define dither:diffusion-amount=50%% -dither FloydSteinberg -colors 256 -depth 8 "%~dp0textures\ps2\%%~nG.png"
FOR /F "tokens=*" %%G IN ('dir /b *.png') DO "%~dp0dependencies/windows/superfreq.exe" png2tex "%~dp0textures/xbox/%%G" "%~dp0_ark\dx\custom_textures\gen\%%~nG_keep.png_xbox" --platform x360 --miloVersion 25
cd "%~dp0textures/ps2"
FOR /F "tokens=*" %%G IN ('dir /b *.png') DO "%~dp0dependencies/windows/superfreq.exe" png2tex "%~dp0textures/ps2/%%G" "%~dp0_ark\dx\custom_textures\gen\%%~nG_keep.png_ps2" --platform ps2 --preset gh2
pause