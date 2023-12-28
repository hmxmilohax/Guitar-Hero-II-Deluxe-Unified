xcopy "%~dp0_vanilla\vanilla_ps2\_ark\" "%~dp0_obj\ps2\" /c /i /e /h /y
xcopy "%~dp0_vanilla\vanilla_ps2\IOP\" "%~dp0_build\ps2\IOP" /c /i /e /h /y
xcopy "%~dp0_vanilla\vanilla_ps2\VIDEOS\" "%~dp0_build\ps2\VIDEOS" /c /i /e /h /y
xcopy "%~dp0_ark\" "%~dp0_obj\ps2\" /exclude:dependencies\ps2_excludes.txt /c /i /e /h /y
"%~dp0dependencies\windows\arkhelper.exe" dir2ark "%~dp0_obj\ps2" "%~dp0_build\ps2\GEN" -n "MAIN" -s 4073741823