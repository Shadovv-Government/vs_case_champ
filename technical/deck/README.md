# Сборка презентации

- [evidence.json](evidence.json) — значения графиков и допущения.
- [calculate.py](calculate.py) — пересчёт из синтетического XLSX.
- [slides.mjs](slides.mjs), [layout.mjs](layout.mjs) и [notes.mjs](notes.mjs) — композиции, оформление и заметки. Текст, графики и мокап редактируются.
- [assets/](assets/) — изображения, прозрачные PNG-иконки и Golos Text для отдельного приложения. Логотип из [официального пакета VK](https://vk.company.ru/ru/press/identity/). Фоны и предметные иллюстрации сгенерированы для проекта.
- Gilroy Light и ExtraBold для слайдов извлекаются из личной копии Gilroy FREE в `.local/`. Эта копия не входит в репозиторий.

Из корня репозитория задайте `ARTIFACT_RUNTIME` (каталог `dependencies` установленного OpenAI Primary Runtime) и `PRESENTATIONS_SKILL` (каталог навыка Presentations). Запустите:

```powershell
python technical/deck/calculate.py
python technical/deck/prepare-gilroy.py "C:/путь/к/Gilroy-FREE.zip"
& "$env:ARTIFACT_RUNTIME/node/bin/node.exe" technical/deck/render-icons.mjs
& "$env:ARTIFACT_RUNTIME/node/bin/node.exe" technical/deck/build.mjs
& "$env:ARTIFACT_RUNTIME/node/bin/node.exe" technical/deck/finalize.mjs
python technical/deck/package_pdf.py
```

Python использует pandas, openpyxl, Pillow и PyMuPDF. Финализатор сохраняет новый PPTX и требует свободное имя файла. Перед пересборкой сохраните предыдущие версии вне `presentation/`. PDF для подачи собран из проверенных слайдов 2560×1440.
