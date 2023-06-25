@REM 2回目以降の起動時
@REM docker run -p 5000:5000 --rm -v C:\Users\Public\Documents\github\Docker_env\chat_gpt\work:/work -w /work --name chat_gpt_env chat_env
docker run -p 5000:5000 --rm --name chat_gpt_env chat_env
