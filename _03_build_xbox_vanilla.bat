xcopy "%~dp0_vanilla\vanilla_xbox\_ark\" "%~dp0_obj\xbox\" /c /i /e /h /y
xcopy "%~dp0_vanilla\vanilla_xbox\videos\" "%~dp0_build\xbox\videos" /c /i /e /h /y
xcopy "%~dp0_ark\" "%~dp0_obj\xbox\" /exclude:"%~dp0dependencies\xbox_excludes.txt" /c /i /e /h /y
"%~dp0dependencies\windows\arkhelper.exe" dir2ark "%~dp0_obj\xbox" "%~dp0_build\xbox\GEN" -e -n "main" -s 4073741823