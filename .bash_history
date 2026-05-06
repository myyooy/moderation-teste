main.py
mv bot.py main.py
bot.py
ls
echo "worker: python main.py" > Procfile
mv bot.py main.py
ls
git add .
git commit -m "Renomeando para main.py para o Railway aceitar"
git push origin main
