#!/usr/bin/env python3
"""Apply conservative Android 16 runtime fixes to Social2, without changing native hooks."""
from pathlib import Path
import sys
r=Path(sys.argv[1])

def rep(path,old,new):
 p=r/path
 s=p.read_text()
 assert s.count(old)==1,(path,old)
 p.write_text(s.replace(old,new,1))

helper='''package top.niunaijun.blackbox.utils;
import android.content.pm.ApplicationInfo;
import android.os.Build;
import java.io.File;
import top.niunaijun.blackbox.BlackBoxCore;

public final class GuestApkCompat {
    private static final String TAG = "AvisDexCompat";
    private GuestApkCompat() {}
    public static void beforeGuestLoad(ApplicationInfo guest) {
        if (Build.VERSION.SDK_INT < 34 || guest == null) return;
        try {
            File host = new File(BlackBoxCore.getContext().getApplicationInfo().dataDir).getCanonicalFile();
            File managed = new File(host, "data/app").getCanonicalFile();
            prepare(guest.sourceDir,managed);
            if (guest.splitSourceDirs != null)
                for (String split : guest.splitSourceDirs) prepare(split,managed);
        } catch (Throwable e) { Slog.w(TAG,"Preparation failed",e); }
    }
    private static void prepare(String path,File managed) {
        if(path==null || path.isEmpty())return;
        try {
            File f=new File(path).getCanonicalFile();
            if(!f.getPath().startsWith(managed.getAbsolutePath()+File.separator)||!f.isFile())return;
            if(f.canWrite()&&!f.setReadOnly()) Slog.w(TAG,"Cannot protect "+f.getName());
            else Slog.i(TAG,"Read-only guest APK: "+f.getName());
        }catch(Throwable e){Slog.w(TAG,"Read-only failure",e);}
    }
}
'''
h=r/'Bcore/src/main/java/top/niunaijun/blackbox/utils/GuestApkCompat.java'
assert not h.exists()
h.write_text(helper)
rep('Bcore/src/main/java/top/niunaijun/blackbox/app/BActivityThread.java',
'        ApplicationInfo applicationInfo = packageInfo.applicationInfo;\n',
'        ApplicationInfo applicationInfo = packageInfo.applicationInfo;\n        top.niunaijun.blackbox.utils.GuestApkCompat.beforeGuestLoad(applicationInfo);\n')
rep('Bcore/src/main/java/top/niunaijun/blackbox/core/system/pm/installer/CopyExecutor.java',
'            try {\n                if (option.isFlag(InstallOption.FLAG_URI_FILE)) {',
'            try {\n                if(newFile.exists())newFile.setWritable(true,true);\n                if (option.isFlag(InstallOption.FLAG_URI_FILE)) {')
rep('Bcore/src/main/java/top/niunaijun/blackbox/core/system/pm/installer/CopyExecutor.java',
'                        FileUtils.copyFile(src, dst);\n                        ps.pkg.splitCodePaths[i] = dst.getAbsolutePath();',
'                        if(dst.exists())dst.setWritable(true,true);\n                        FileUtils.copyFile(src, dst);\n                        ps.pkg.splitCodePaths[i] = dst.getAbsolutePath();')
rep('Bcore/src/main/java/top/niunaijun/blackbox/app/dispatcher/AppServiceDispatcher.java',
'            IBinder iBinder = service.onBind(intent);\n            record.addBinder(intent, iBinder);',
'            IBinder iBinder = service.onBind(intent);\n            if (isUnavailableGmsBinder(serviceInfo,intent,iBinder)) return null;\n            record.addBinder(intent, iBinder);')
rep('Bcore/src/main/java/top/niunaijun/blackbox/app/dispatcher/AppServiceDispatcher.java',
'    public int onStartCommand(Intent proxyIntent, int flags, int startId) {',
'''    private boolean isUnavailableGmsBinder(ServiceInfo info,Intent intent,IBinder binder) {
        if(info==null || !"com.google.android.gms".equals(info.packageName)||binder==null)return false;
        try {
            String name=binder.getClass().getName();
            String descriptor=binder.getInterfaceDescriptor();
            if(name.contains("NullBinder") || descriptor==null || descriptor.isEmpty()){
                android.util.Log.w(TAG,"AvisGmsBind: unavailable broker, no proxy: "
                     +info.name+" action="+(intent==null?"":intent.getAction())+" binder="+name);
                return true;
            }
        }catch(Throwable e){android.util.Log.w(TAG,"AvisGmsBind descriptor check unavailable",e);}
        return false;
    }

    public int onStartCommand(Intent proxyIntent, int flags, int startId) {''')
print("CRASH_FIX_PATCH_OK")
