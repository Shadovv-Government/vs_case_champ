# VK Case Champ 2026 — социальная коммерция для бизнес-сообществ

Решение отборочного этапа. Сдача — PDF из 8 слайдов до 22 ноября, 09:00.

**Начните с отчёта:** [`reports/2026-11-16_progress_report.md`](reports/2026-11-16_progress_report.md) — что изучено, выводы, концепция пути продавца и план работы.

## Материалы

| Папка | Что внутри |
|---|---|
| [`PLAN.md`](PLAN.md), [`docs/`](docs/) | План решения, спецификация анализа и модели, вопросы для Q&A и интервью |
| [`sources/`](sources/) | Бриф кейса (PDF) и датасет организаторов (XLSX) |
| [`notebooks/`](notebooks/) | `01_dataset_eda` — анализ датасета; `02_social_commerce_benchmarks` — мировые бенчмарки |
| [`figures/eda/`](figures/eda/) | 19 графиков по датасету для слайдов |
| [`research/`](research/) | Данные исследования рынка (12 платформ, 55 показателей), 42 источника, 8 графиков для слайдов |
| [`pages/`](pages/) | Локальные копии страниц с объяснениями |
| [`scripts/`](scripts/) | Сборка и запуск ноутбуков |
| [`reports/`](reports/) | Отчёты о проделанной работе |

## Онлайн

- Ноутбуки в Colab: [анализ датасета](https://colab.research.google.com/drive/11g_E_x02hNgS-nOGpGZpBCtKx-pvHsGF), [бенчмарки](https://colab.research.google.com/drive/1Bqm8b2tjVNvrFRQp_HSaYVGOx3jWGRur)
- Папка в Google Drive: [ноутбуки](https://drive.google.com/drive/folders/1dL-aZwn2WfxsymEzz5fZYjfSZtA-OLL_?usp=sharing)
- Страницы с объяснениями: [анализ датасета](https://claude.ai/artifact/H5NzaMgGyBjVvQk41oC9A1), [исследование рынка](https://claude.ai/artifact/YUQ9ribn2rD67jviLETnyQ)

## Как пересобрать

```bash
python research/build_data.py
python scripts/build_nb01_eda.py notebooks/01_dataset_eda.ipynb
python scripts/build_nb02_benchmarks.py .
cd notebooks && python ../scripts/run_notebook.py 01_dataset_eda.ipynb && python ../scripts/run_notebook.py 02_social_commerce_benchmarks.ipynb
```

Нужны `pandas`, `openpyxl`, `matplotlib`, `jinja2`, `nbformat`, `nbclient`, `ipykernel`. Ноутбуки запускаются из папки `notebooks/`, чтобы найти данные по относительным путям.
