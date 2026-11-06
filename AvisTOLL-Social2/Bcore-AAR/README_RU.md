# Bcore.aar — Social2 ARM64

Сборка ядра виртуального Android-окружения на базе последней проверенной конфигурации Social2.

## Загрузка

- [Bcore.aar](Bcore.aar) — единая библиотека с 7 внутренними проектными модулями.
- [Bcore-Source.zip](Bcore-Source.zip) — исправленный исходник Java, C++ и ASM.
- [Правила сборки](../BUILD_RULES_BCORE_AAR_RU.txt).
- [Статистика и SHA-256](aar-manifest.json).
- [GitHub Actions](https://github.com/egrrratatuj-blip/Ger/actions/workflows/build-bcore-aar.yml).

SHA-256 первой проверенной сборки Bcore.aar:
`83d09db5a494d51602ab10fa4141a8908b1b98a0174fa74c393c0779cbbfb715`

## Нативные библиотеки

- `jni/arm64-v8a/libkxv72q4n.so` — свежая ARM64-компиляция Bcore, вместо `libABridge.so`.
- `jni/arm64-v8a/libmnr85zt1.so` — свежая ARM64-компиляция Pine, вместо `libpine.so`.

Загружающие классы, CMake targets, внутренние упоминания и ELF SONAME согласованы. 
`JNI_OnLoad` экспортируется обоими ELF-файлами.

## Подключение

```gradle
repositories {
    google()
    mavenCentral()
    maven { url 'https://jitpack.io' }
}
dependencies {
    implementation files('libs/Bcore.aar')
    implementation 'androidx.appcompat:appcompat:1.2.0'
    implementation 'com.google.android.material:material:1.3.0'
    implementation 'com.github.tiann:FreeReflection:3.2.2'
    implementation 'com.github.CodingGay.BlackReflection:core:1.1.2'
}
```

`Bcore.aar` включает **внутренние модули**, но не содержит внешние Maven-зависимости: их должен разрешить Gradle приложения-потребителя. Возможна адаптация манифеста и proxy-компонентов под package name конкретного приложения.

## R8

Для release-модуля Bcore включена минимизация R8 из Android Gradle Plugin. Точные имена Java-классов и методов, используемых JNI, Binder, Xposed и рефлексией, сохраняются специальными keep-правилами. Это ограниченная обфускация с приоритетом совместимости, а не агрессивное переименование всех классов.

## Проверка

- Вызвана `:Bcore:assembleRelease` и ещё шесть `assembleRelease` задач; все выполнены успешно.
- Один собранный AAR с 2 718 class-entries, двумя новыми JNI-библиотеками и AndroidManifest.
- Собран тестовый Android APK с локальным `implementation files('libs/Bcore.aar')`, без зависимости от исходного модуля Bcore; обе JNI-библиотеки внутри APK присутствуют.
- Нативные ELF проверены на ARM64, SONAME, Build ID и `JNI_OnLoad`.

**Проверка сборки и интеграции не равнозначна испытанию функций на Android 16.** Для подтверждения runtime необходим запуск на устройстве и анализ logcat/tombstone. Полный Discord OAuth также требует кода хост-приложения, которого в AAR нет.
