# MRI Snapshot Analyzer

Демонстрационное приложение для анализа снимков МРТ (MVP). Поддерживает загрузку DICOM (.dcm)
и NIfTI (.nii/.nii.gz) файлов, возвращает базовый отчёт.

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Откройте `http://localhost:8000`.

## Эндпоинты

- `GET /health` — проверка состояния.
- `POST /analyze` — загрузка файла для анализа.

## Примечания

Это прототип: логика анализа замокана. Для реальных моделей замените функцию
`_mock_analysis` в `app/main.py`.
