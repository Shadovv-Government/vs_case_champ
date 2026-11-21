# Сборка презентации

- [calculate.py](calculate.py) пересчитывает [evidence.json](evidence.json) по исходному XLSX. Здесь же заданы допущения финансовой модели и пороги пилота.
- [slides.mjs](slides.mjs), [layout.mjs](layout.mjs) и [notes.mjs](notes.mjs) задают слайды и заметки. Графики и текст остаются редактируемыми.
- [assets/](assets/) содержит изображения, иконки и Golos Text Regular и Bold. Логотип — из [официального пакета VK](https://vk.company.ru/ru/press/identity/). Изображения сгенерированы для проекта.
- [package_pdf.py](package_pdf.py) собирает PDF из восьми слайдов с поиском по тексту и закладками, а [report.py](report.py) — аналитический отчёт и отдельное раскрытие ИИ. В аналитическом отчёте используется тот же набор расчётов, что на слайдах.

Из корня репозитория:

1. Задайте `ARTIFACT_RUNTIME` (путь к каталогу `dependencies` OpenAI Primary Runtime) и `PRESENTATIONS_SKILL` (путь к навыку Presentations).
2. Запустите `python technical/deck/calculate.py` с `pandas` и `openpyxl`.
3. С Node из указанного runtime запустите `technical/deck/build.mjs` и затем `technical/deck/finalize.mjs`. Переменная `CASE_PYTHON` позволяет задать свой Python для финализатора.
4. Запустите `python technical/deck/package_pdf.py` с `Pillow` и `reportlab`.

Финализатор проверяет пакет PowerPoint, размеры слайдов и нативные диаграммы, затем записывает проверенный PPTX. Результаты сборки — в [presentation/](../../presentation/README.md), промежуточные файлы — в `.local/redesign/output/`.
