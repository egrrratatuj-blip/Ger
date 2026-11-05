# AvisTOLL Social2 — public Android release

Публичная ветка с исправленным исходником, готовым APK и правилами воспроизводимой сборки.

## Скачать
- **[Готовый APK — NDK21, ARM64](AvisTOLL-Social2/releases/AvisTOLL-Social2-FRESH-NDK21-debug.apk)** — SHA-256 `159c090309098de481235e57ff47a0c885618bb80188ec4900620abf712591d4`.
- **[Исправленный исходник ZIP](AvisTOLL-Social2/source/AvisTOLL-Social2-FRESH-PUBLIC-SOURCE.zip)** — без предсобранных `.so` и приватного ключа.
- **[Правила сборки на русском](AvisTOLL-Social2/BUILD_RULES_RU.txt)**.
- **[GitHub Actions](../../actions)** — автоматическая пересборка Java/C++ и проверка ELF.

Прямая ссылка на APK:
https://raw.githubusercontent.com/egrrratatuj-blip/Ger/avis-social2/AvisTOLL-Social2/releases/AvisTOLL-Social2-FRESH-NDK21-debug.apk

Важное: этот APK успешно собран и проверен структурно, но не подтверждён запуск на Android 16. Публичный исходник не включает прежний ключ подписи. Новые CI-сборки без сохранённого секрета подписи могут требовать переустановки приложения.

Ветка `avis-social2` выделена отдельно, чтобы не затрагивать другие проекты репозитория.
