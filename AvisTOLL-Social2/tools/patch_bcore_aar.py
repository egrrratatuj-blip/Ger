#!/usr/bin/env python3
"""Apply the audited Android 21 / Social2 JNI-renaming patch to an extracted source tree."""
from pathlib import Path
import sys
root=Path(sys.argv[1])
BRIDGE='kxv72q4n'
PINE='mnr85zt1'

def replace(rel,old,new,count=1):
    p=root/rel
    text=p.read_text()
    actual=text.count(old)
    if actual!=count: raise ValueError(f'{rel}: expected {count} occurrences of {old!r}, found {actual}')
    p.write_text(text.replace(old,new))

replace('Bcore/src/main/cpp/CMakeLists.txt','project(ABridge CXX C ASM)',f'project({BRIDGE} CXX C ASM)')
replace('Bcore/src/main/cpp/CMakeLists.txt','        ABridge\n',f'        {BRIDGE}\n',2)
replace('Bcore/pine-core/src/main/cpp/CMakeLists.txt','add_library(pine SHARED',f'add_library({PINE} SHARED')
replace('Bcore/pine-core/src/main/cpp/CMakeLists.txt','target_link_libraries(pine ',f'target_link_libraries({PINE} ')
replace('Bcore/pine-core/build.gradle',"targets 'pine'",f"targets '{PINE}'")
replace('Bcore/pine-core/src/main/java/top/canyie/pine/PineConfig.java','System.loadLibrary("pine")',f'System.loadLibrary("{PINE}")')
replace('Bcore/src/main/java/top/niunaijun/blackbox/core/NativeCore.java','"libABridge.so"',f'"lib{BRIDGE}.so"')
replace('Bcore/src/main/java/top/niunaijun/blackbox/core/NativeCore.java','System.loadLibrary("ABridge")',f'System.loadLibrary("{BRIDGE}")')
replace('Bcore/src/main/java/top/niunaijun/blackbox/utils/RuntimeNativeLibrary.java','"libABridge.so"',f'"lib{BRIDGE}.so"')
replace('Bcore/src/main/cpp/Hook/FileSystemHook.cpp','"libABridge.so"',f'"lib{BRIDGE}.so"')
replace('Bcore/src/main/cpp/Stealth/SyscallSpoof.cpp','"ABridge"',f'"{BRIDGE}"')
for rel in ('Bcore/pine-core/src/main/java/top/canyie/pine/PineConfig.java','Bcore/pine-core/src/main/java/top/canyie/pine/Pine.java'):
    p=root/rel
    p.write_text(p.read_text().replace('libpine.so',f'lib{PINE}.so'))

replace('Bcore/build.gradle',"""        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
""","""        release {
            buildConfigField "boolean", "STORAGE_ALIAS", project.hasProperty("avisStorageAlias") ? "true" : "false"
            buildConfigField "boolean", "PRIVATE_BRIDGE", project.hasProperty("avisPrivateBridge") ? "true" : "false"
            buildConfigField "boolean", "PATH_COMPAT", project.hasProperty("avisPathCompat") ? "true" : "false"
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
""")
with (root/'Bcore/proguard-rules.pro').open('a') as f:
    f.write("""
# R8 from AGP 4.0.1; keep JNI, IPC, reflection and dynamically invoked runtime hooks.
-keep class top.canyie.pine.** { *; }
-keep class de.robv.android.xposed.** { *; }
-keep class top.niunaijun.blackbox.** { *; }
-keep class top.niunaijun.jnihook.** { *; }
-keepattributes *Annotation*,EnclosingMethod,InnerClasses,Signature
""")
with (root/'Bcore/consumer-rules.pro').open('a') as f:
    f.write("""
# Keep binary contracts when a consuming APK enables R8.
-keep class top.canyie.pine.** { *; }
-keep class de.robv.android.xposed.** { *; }
-keep class top.niunaijun.blackbox.** { *; }
-keep class top.niunaijun.jnihook.** { *; }
-keep class mirror.** { *; }
-keepattributes *Annotation*,EnclosingMethod,InnerClasses,Signature
""")
assert not list(root.rglob('*.so')),'Prebuilt SO prohibited'
assert not list(root.rglob('*.keystore')),'Private signing key must not be in source'
print('PATCH_OK',BRIDGE,PINE)
