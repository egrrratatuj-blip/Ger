#!/usr/bin/env python3
"""Assemble one AAR containing all seven project modules; preserve external Maven deps."""
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile,ZIP_DEFLATED
import hashlib,json,shutil,sys

root=Path(sys.argv[1])
out=Path(sys.argv[2])
out.mkdir(parents=True,exist_ok=True)
modules=[
 ('Bcore','Bcore'),('Bcore/black-fake','black-fake'),
 ('Bcore/black-hook','black-hook'),('android-mirror','android-mirror'),
 ('Bcore/pine-core','pine-core'),('Bcore/pine-xposed','pine-xposed'),
 ('Bcore/pine-xposed-res','pine-xposed-res')]
records={}
classes={}
resources={}
native={}
consumer=[]
aar_other={}
for path,name in modules:
    archive=root/path/'build/outputs/aar'/f'{name}-release.aar'
    assert archive.is_file(),f'AAR missing: {archive}'
    records[name]={'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
    with ZipFile(archive) as z:
        files={n:z.read(n) for n in z.namelist() if not n.endswith('/')}
    assert 'classes.jar' in files,name
    with ZipFile(BytesIO(files['classes.jar'])) as jar:
        for n in jar.namelist():
            if n.endswith('/') or n.startswith('META-INF/') or n=='module-info.class':continue
            data=jar.read(n)
            if n in classes and classes[n]!=data:raise ValueError(f'Duplicate conflicting class {n} from {name}')
            classes[n]=data
    for n,data in files.items():
        if n.startswith('jni/') and n.endswith('.so'):
            if n in native and native[n]!=data:raise ValueError(f'Duplicate conflicting native lib {n}')
            native[n]=data
        elif n.startswith('res/') or n.startswith('assets/'):
            if n in resources and resources[n]!=data:raise ValueError(f'Duplicate conflicting resource {n}')
            resources[n]=data
        elif n=='proguard.txt' and data not in consumer:
            consumer.append(data)
        elif name=='Bcore' and n not in ('classes.jar','proguard.txt') and not n.startswith(('jni/','res/','assets/')):
            aar_other[n]=data

expected=('jni/arm64-v8a/libkxv72q4n.so','jni/arm64-v8a/libmnr85zt1.so')
assert sorted(native)==sorted(expected),f'Unexpected JNI libraries: {list(native)}'
for n in ('top/niunaijun/blackbox/core/NativeCore.class',
          'top/canyie/pine/PineConfig.class',
          'top/niunaijun/jnihook/jni/JniHook.class',
          'black/android/app/ActivityThread.class'):
    assert n in classes,n

jarbuf=BytesIO()
with ZipFile(jarbuf,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
    for n in sorted(classes): z.writestr(n,classes[n])
aar=out/'Bcore.aar'
with ZipFile(aar,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
    for n,data in sorted(aar_other.items()):z.writestr(n,data)
    z.writestr('classes.jar',jarbuf.getvalue())
    for n,data in sorted({**resources,**native}.items()):z.writestr(n,data)
    z.writestr('proguard.txt',b'\n'.join(consumer))
variants=out/'module-aars'
variants.mkdir(exist_ok=True)
for path,name in modules:
    shutil.copy2(root/path/'build/outputs/aar'/f'{name}-release.aar',variants/f'{name}.aar')
records['Bcore.aar']={'bytes':aar.stat().st_size,
                      'sha256':hashlib.sha256(aar.read_bytes()).hexdigest(),
                      'class_entries':len(classes),
                      'jni':list(sorted(native)),
                      'internal_modules':len(modules),
                      'external_maven_dependencies_embedded':False}
(out/'aar-manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print('FAT_AAR_OK',json.dumps(records['Bcore.aar']))
