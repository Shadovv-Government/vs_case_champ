# Скрипты

```powershell
python technical/scripts/build_research_data.py
python technical/scripts/build_nb01_eda.py technical/notebooks/01_dataset_eda.ipynb
python technical/scripts/build_nb02_benchmarks.py .
Set-Location technical/notebooks
python ../scripts/run_notebook.py 01_dataset_eda.ipynb
python ../scripts/run_notebook.py 02_social_commerce_benchmarks.ipynb
```

Для ноутбуков нужны Python, pandas, openpyxl, matplotlib, numpy, nbformat, nbclient, ipykernel и jinja2. `transcribe.py` использует faster-whisper и принимает локальную запись и папку вывода. Запись и сырая расшифровка относятся к `.local/`. [Сборка слайдов](../deck/README.md)
