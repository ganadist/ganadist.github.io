Title: 안드로이드의 로그 확인 기능들 살펴보기
Slug: 2018_11_24_android_log
Date: 2018-11-24 22:59
Category: tech
Tags: android, log, 
Summary: 안드로이드의 로그설비들

# logcat buffer

 안드로이드 개발을 하고 있다면 아주 친숙하게 볼 수 있는 안드로이드의 기본 로깅 시스템입니다.
 로깅 데이터는 링버퍼에 저장이 되며, 따라서 최근의 로깅 데이터만 보관하며, adb를 이용해 요청할 때 로깅 데이터를 조회할 수 있습니다.
 
 logcat은 용도별로 다음과 같은 로그 버퍼를 가지고 있습니다.

 * main

  LOG_TAG가 [MAIN](https://android.googlesource.com/platform/system/core/+/pie-release/liblog/include/log/log_id.h#29)인 로그 메소드 및 함수 [android.util.Log](https://android.googlesource.com/platform/frameworks/base/+/pie-release/core/java/android/util/Log.java#59) 또는 [ALOGx](https://android.googlesource.com/platform/system/core/+/pie-release/liblog/include/log/log_main.h#173)를 사용할 때 로깅데이터가 저장되는 로그버퍼입니다.
  로그버퍼는 어플리케이션(uid/pid)별로 균등하게 quota가 배분되기 때문에, 특정 어플리케이션이 과다한 로그를 발생시켜도, 다른 어플리케이션의 로그를 씹어먹는 사태가 발생하지 않습니다.(Android 5.0이상에서만 적용됩니다. 그 이전의 플랫폼에서는 애석하게도 특정앱이 로그를 과다하게 발생시키면, 다른 앱의 로그가 밀리게 됩니다.)

 * radio

  LOG_TAG가 [RADIO](https://android.googlesource.com/platform/system/core/+/pie-release/liblog/include/log/log_id.h#30)인 로그 메소드 및 함수 [android.telephony.Rlog](https://android.googlesource.com/platform/frameworks/base/+/pie-release/telephony/java/android/telephony/Rlog.java#34) 또는 [RLOGx](https://android.googlesource.com/platform/system/core/+/pie-release/liblog/include/log/log_radio.h#46) 를 사용할 때 저장되는 로그 버퍼입니다. 주로 전화기능/모뎀관련 동작에 대한 로그가 저장되며, 일반 어플리케이션에서는 사용할 수 없습니다. system buffer와 마찬가지로 어플리케이션과 독립적으로 로그 데이터가 보관됩니다.

 * events

  LOG_TAG가 [EVENTS](https://android.googlesource.com/platform/system/core/+/pie-release/liblog/include/log/log_id.h#31)인 로그 메소드 및 함수 [android.util.EventLog](https://android.googlesource.com/platform/frameworks/base/+/pie-release/core/java/android/util/EventLog.java#35)를 사용할 때 로깅데이터가 저장되는 로그 버퍼입니다. 다른 로그처럼 임의의 문자열이 아니라 [logtags 파일에 정의해 놓은 포맷형식](https://android.googlesource.com/platform/frameworks/base/+/pie-release/services/core/java/com/android/server/EventLogTags.logtags)으로 로그가 저장됩니다. 시스템의 중요한 이벤트가 발생할 때 참조되는 데이터를 저장하게 됩니다.

 * system

  LOG_TAG가 [SYSTEM](https://android.googlesource.com/platform/system/core/+/pie-release/liblog/include/log/log_id.h#32) 인 로그 메소드 및 함수 [android.util.Slog](https://android.googlesource.com/platform/frameworks/base/+/pie-release/core/java/android/util/Slog.java#22) 또는 [SLOGx](https://android.googlesource.com/platform/system/core/+/pie-release/liblog/include/log/log_system.h#44)를 사용할 때 저장되는 로그 버퍼입니다. 주로 ActivityManagerService, WindowManagerService 등과 같은 system server에서 남기는 로그가 저장되며, 일반 어플리케이션에서는 사용할 수 없는 api 이기 때문에, 어플리케이션과 독립적으로 로그 데이터가 보관됩니다.

 * crash

  앱이 segfault 또는 exception으로 인해 비정상적으로 종료되었을 때, 해당 시점의 stack을 보관하는 로그 버퍼입니다. 다른 로그 버퍼에 비해, 사용되는 빈도가 적기 때문에, 기기가 재시작하지 않았다면 꽤 이전의 로그까지 조회가 가능합니다. Android 5.0 이상부터 지원되는 로그버퍼입니다.

 각각의 로그 버퍼의 내용을 확인해보려면, [-b 버퍼이름 옵션](https://developer.android.com/studio/command-line/logcat#alternativeBuffers)을 넣으면 됩니다. 따로 지정하지 않으면, [기본값으로 main, system및 crash 버퍼의 내용이 함께 출력](https://android.googlesource.com/platform/system/core/+/pie-release/logcat/logcat.cpp#1092)됩니다.


# dropbox service

 logcat의 경우, 시스템이 재시작되거나 시간이 오래지나서 링버퍼가 오버랩되면 이전의 로그를 참조할 수 없습니다. 하지만 anr이나 crash등의 중요한 로그 정보들은 logcat이외에도 dropbox 라는 안드로이드의 서비스에 의해 파일로 저장이 되기 때문에, 시스템이 재시작되어도 나중에 확인이 가능합니다.

 dropbox 서비스에 저장된 정보의 목록을 확인해보려면 다음과 같은 명령을 이용합니다.

    $ adb shell dumpsys dropbox
    Drop box contents: 466 entries
    Max entries: 1000

    2018-11-22 02:43:47 keymaster (data, 52 bytes)
    2018-11-22 06:51:37 system_app_anr (compressed text, 14799 bytes)
        Process: com.google.android.gms.persistent/PID: 24113/Flags: 0xa8c83ec ...
    2018-11-23 09:00:20 system_app_wtf (text, 947 bytes)
        Process: com.android.vending/PID: 10025/Flags: 0x38cabec5/Package: com ...
    2018-11-23 09:02:23 system_app_anr (compressed text, 7443 bytes)
        Process: com.google.android.gms/PID: 27251/Flags: 0xa8c83ec5/Package: ...
    2018-11-23 13:20:42 system_server_wtf (text, 1155 bytes)
        Process: system_server/Subject: ActivityManager/Build: google/crosshat ...
    2018-11-23 13:21:41 data_app_wtf (text, 2955 bytes)
        Process: com.nhnent.payapp/PID: 9605/Flags: 0x38d83e44/Package: com.nh ...
    2018-11-23 13:21:43 SYSTEM_TOMBSTONE (compressed text, 6298 bytes)
        isPrevious: true/Build: google/crosshatch/crosshatch:9/PQ1A.181105.017 ...
    2018-11-23 13:21:43 SYSTEM_TOMBSTONE (compressed text, 6249 bytes)
        isPrevious: true/Build: google/crosshatch/crosshatch:9/PQ1A.181105.017 ...
    2018-11-23 13:21:44 SYSTEM_TOMBSTONE (compressed text, 6278 bytes)
        isPrevious: true/Build: google/crosshatch/crosshatch:9/PQ1A.181105.017 ...
    2018-11-23 18:34:10 data_app_crash (text, 2616 bytes)
        Process: com.linecorp.apngsample.debug/PID: 11374/Flags: 0x30e8be46/Pa ...
    2018-11-23 21:22:33 system_app_wtf (compressed text, 1038 bytes)
        Process: com.android.vending/PID: 1712/Flags: 0x38cabec5/Package: com. ...

    Usage: dumpsys dropbox [--print|--file] [YYYY-mm-dd] [HH:MM:SS] [tag]

 이 중 관심있는 특정 항목을 조회해 보려면 아래와 같이 저장된 시간 정보및 tag 정보를 주어서 특정한 로그를 확인해 볼 수 있습니다.

    $ adb shell dumpsys dropbox --print 2018-11-24 08:04:44 data_app_crash
    Drop box contents: 468 entries
    Max entries: 1000
    Searching for: 2018-11-24 08:04:44 data_app_crash

    ========================================
    2018-11-24 08:04:44 data_app_crash (text, 2616 bytes)
    Process: com.linecorp.apngsample.debug
    PID: 15276
    Flags: 0x30c8be46
    Package: com.linecorp.apngsample.debug v1 (1.0)
    Foreground: Yes
    Build: google/crosshatch/crosshatch:9/PQ1A.181105.017.A1/5081125:user/release-keys

    java.lang.RuntimeException: Unable to instantiate activity ComponentInfo{com.linecorp.apngsample.debug/com.linecorp.android.apngsample.MainActivity}: java.lang.ClassNotFoundException: Didn't find class "com.linecorp.android.apngsample.MainActivity" on path: DexPathList[[zip file "/data/app/com.linecorp.apngsample.debug-q0Ui7ZjsmlwkupvRTNNjUg==/base.apk"],nativeLibraryDirectories=[/data/app/com.linecorp.apngsample.debug-q0Ui7ZjsmlwkupvRTNNjUg==/lib/arm64, /data/app/com.linecorp.apngsample.debug-q0Ui7ZjsmlwkupvRTNNjUg==/base.apk!/lib/arm64-v8a, /system/lib64]]
        at android.app.ActivityThread.performLaunchActivity(ActivityThread.java:2844)
        at android.app.ActivityThread.handleLaunchActivity(ActivityThread.java:3049)
        at android.app.servertransaction.LaunchActivityItem.execute(LaunchActivityItem.java:78)
        at android.app.servertransaction.TransactionExecutor.executeCallbacks(TransactionExecutor.java:108)
        at android.app.servertransaction.TransactionExecutor.execute(TransactionExecutor.java:68)
        at android.app.ActivityThread$H.handleMessage(ActivityThread.java:1809)
        at android.os.Handler.dispatchMessage(Handler.java:106)
        at android.os.Looper.loop(Looper.java:193)
        at android.app.ActivityThread.main(ActivityThread.java:6680)
        at java.lang.reflect.Method.invoke(Native Method)
        at com.android.internal.os.RuntimeInit$MethodAndArgsCaller.run(RuntimeInit.java:493)
        at com.android.internal.os.ZygoteInit.main(ZygoteInit.java:858)
    Caused by: java.lang.ClassNotFoundException: Didn't find class "com.linecorp.android.apngsample.MainActivity" on path: DexPathList[[zip file "/data/app/com.linecorp.apngsample.debug-q0Ui7ZjsmlwkupvRTNNjUg==/base.apk"],nativeLibraryDirectories=[/data/app/com.linecorp.apngsample.debug-q0Ui7ZjsmlwkupvRTNNjUg==/lib/arm64, /data/app/com.linecorp.apngsample.debug-q0Ui7ZjsmlwkupvRTNNjUg==/base.apk!/lib/arm64-v8a, /system/lib64]]
        at dalvik.system.BaseDexClassLoader.findClass(BaseDexClassLoader.java:134)
        at java.lang.ClassLoader.loadClass(ClassLoader.java:379)
        at java.lang.ClassLoader.loadClass(ClassLoader.java:312)
        at android.app.AppComponentFactory.instantiateActivity(AppComponentFactory.java:69)
        at androidx.core.app.CoreComponentFactory.instantiateActivity(CoreComponentFactory.java:43)
        at android.app.Instrumentation.newActivity(Instrumentation.java:1215)
        at android.app.ActivityThread.performLaunchActivity(ActivityThread.java:2832)
        ... 11 more


# bugreport

 [AOSP Issue Tracker에 버그를 보고](https://issuetracker.google.com/issues/111714386#comment2)하면 구글러들이 [bugreport 도구](https://developer.android.com/studio/debug/bug-report)를 사용해서, 버그가 발생한 기기의 정보를 공유해달라고 요청하는 경우를 종종 볼 수 있습니다.

 bugreport는 [안드로이드 OS의 거의 대부분 정보](https://android.googlesource.com/platform/frameworks/native/+/pie-release/cmds/dumpstate/dumpstate.cpp#1289)를 수집하며, [루팅하지 않으면 접근하지 못하는 anr및 tombstone](https://android.googlesource.com/platform/frameworks/native/+/pie-release/cmds/dumpstate/dumpstate.cpp#2159), 심지어 위에 언급한 모든 로깅 정보들을 하나의 파일로 함께 모아둡니다. 
 이와 같이 강력한 로깅도구이지만, 로그를 모두 모으는데 시간이 너무 오래 걸리고, 또한 시스템 내부의 정보를 수집하면서 버그발생상태를 흩트려버릴 수도 있다는 단점이 있습니다.


# debuggerd

 로깅도구는 아니지만 임의의 프로세스에 대해 현재 stack을 확인할 수 있는 도구입니다. 
 
 하지만 루팅된 쉘에서만 사용할 수 있으므로, 루팅된 기기나 에물레이터에서만 확인이 가능합니다.

 또한 루팅된 기기에서 bugreport를 수행하면 모든 프로세스에 대한 debuggerd 수행 결과가 포함됩니다.

 사용 방법은 아래와 같이 -b 옵션 뒤에 원하는 process의 pid를 입력하면 됩니다.

    # debuggerd -b 4321                                                                                   


    ----- pid 4321 at 2018-11-25 00:00:06 -----
    Cmd line: com.google.android.deskclock
    ABI: 'x86_64'

    "droid.deskclock" sysTid=4321
    #00 pc 000000000007e1da  /system/lib64/libc.so (__epoll_pwait+10)
    #01 pc 0000000000013d12  /system/lib64/libutils.so (android::Looper::pollInner(int)+162)
    #02 pc 0000000000013bc9  /system/lib64/libutils.so (android::Looper::pollOnce(int, int*, int*, void**)+41)
    #03 pc 000000000011ceb5  /system/lib64/libandroid_runtime.so (android::android_os_MessageQueue_nativePollOnce(_JNIEnv*, _jobject*, long, int)+37)
    #04 pc 00000000003dce2b  /system/framework/x86_64/boot-framework.oat (offset 0x3c3000) (android.media.MediaExtractor.seekTo [DEDUPED]+187)
    #05 pc 0000000000ac225c  /system/framework/x86_64/boot-framework.oat (offset 0x3c3000) (android.os.MessageQueue.next+220)
    #06 pc 0000000000abfaa6  /system/framework/x86_64/boot-framework.oat (offset 0x3c3000) (android.os.Looper.loop+518)
    #07 pc 00000000008921f7  /system/framework/x86_64/boot-framework.oat (offset 0x3c3000) (android.app.ActivityThread.main+583)
    #08 pc 00000000005c3e16  /system/lib64/libart.so (art_quick_invoke_static_stub+806)
    #09 pc 00000000000cf603  /system/lib64/libart.so (art::ArtMethod::Invoke(art::Thread*, unsigned int*, unsigned int, art::JValue*, char const*)+243)
    #10 pc 00000000004b7569  /system/lib64/libart.so (art::(anonymous namespace)::InvokeWithArgArray(art::ScopedObjectAccessAlreadyRunnable const&, art::ArtMethod*, art::(anonymous namespace)::ArgArray*, art::JValue*, char const*)+89)
    #11 pc 00000000004b9347  /system/lib64/libart.so (art::InvokeMethod(art::ScopedObjectAccessAlreadyRunnable const&, _jobject*, _jobject*, _jobject*, unsigned long)+1447)
    #12 pc 00000000004338e8  /system/lib64/libart.so (art::Method_invoke(_JNIEnv*, _jobject*, _jobject*, _jobjectArray*)+56)
    #13 pc 000000000011c623  /system/framework/x86_64/boot.oat (offset 0x110000) (java.lang.Class.getDeclaredMethodInternal [DEDUPED]+227)
    #14 pc 0000000000bfd84d  /system/framework/x86_64/boot-framework.oat (offset 0x3c3000) (com.android.internal.os.RuntimeInit$MethodAndArgsCaller.run+141)
    #15 pc 0000000000c04ae4  /system/framework/x86_64/boot-framework.oat (offset 0x3c3000) (com.android.internal.os.ZygoteInit.main+2804)
    #16 pc 00000000005c3e16  /system/lib64/libart.so (art_quick_invoke_static_stub+806)
    #17 pc 00000000000cf603  /system/lib64/libart.so (art::ArtMethod::Invoke(art::Thread*, unsigned int*, unsigned int, art::JValue*, char const*)+243)
    #18 pc 00000000004b7569  /system/lib64/libart.so (art::(anonymous namespace)::InvokeWithArgArray(art::ScopedObjectAccessAlreadyRunnable const&, art::ArtMethod*, art::(anonymous namespace)::ArgArray*, art::JValue*, char const*)+89)
    #19 pc 00000000004b7132  /system/lib64/libart.so (art::InvokeWithVarArgs(art::ScopedObjectAccessAlreadyRunnable const&, _jobject*, _jmethodID*, __va_list_tag*)+434)
    #20 pc 00000000003a0c97  /system/lib64/libart.so (art::JNI::CallStaticVoidMethodV(_JNIEnv*, _jclass*, _jmethodID*, __va_list_tag*)+791)
    #21 pc 00000000000ffd44  /system/lib64/libart.so (art::(anonymous namespace)::CheckJNI::CallMethodV(char const*, _JNIEnv*, _jobject*, _jclass*, _jmethodID*, __va_list_tag*, art::Primitive::Type, art::InvokeType)+2772)
    #22 pc 00000000000ef581  /system/lib64/libart.so (art::(anonymous namespace)::CheckJNI::CallStaticVoidMethodV(_JNIEnv*, _jclass*, _jmethodID*, __va_list_tag*)+33)
    #23 pc 00000000000b2089  /system/lib64/libandroid_runtime.so (_JNIEnv::CallStaticVoidMethod(_jclass*, _jmethodID*, ...)+153)
    #24 pc 00000000000b5250  /system/lib64/libandroid_runtime.so (android::AndroidRuntime::start(char const*, android::Vector<android::String8> const&, bool)+736)
    #25 pc 00000000000021fd  /system/bin/app_process64 (main+1357)
    #26 pc 00000000000c278c  /system/lib64/libc.so (__libc_init+92)

    "Jit thread pool" sysTid=4326
    #00 pc 0000000000026b98  /system/lib64/libc.so (syscall+24)
    #01 pc 00000000000d70bc  /system/lib64/libart.so (art::ConditionVariable::WaitHoldingLocks(art::Thread*)+108)
    #02 pc 000000000050b82c  /system/lib64/libart.so (art::ThreadPool::GetTask(art::Thread*)+316)
    #03 pc 000000000050ac11  /system/lib64/libart.so (art::ThreadPoolWorker::Run()+97)
    #04 pc 000000000050a6a3  /system/lib64/libart.so (art::ThreadPoolWorker::Callback(void*)+131)
    #05 pc 0000000000092bab  /system/lib64/libc.so (__pthread_start(void*)+27)
    #06 pc 000000000002af2d  /system/lib64/libc.so (__start_thread+61)

    "Signal Catcher" sysTid=4327
    #00 pc 000000000007e45a  /system/lib64/libc.so (__rt_sigtimedwait+10)
    #01 pc 0000000000035622  /system/lib64/libc.so (sigwait+66)
    #02 pc 00000000004dab1a  /system/lib64/libart.so (art::SignalCatcher::WaitForSignal(art::Thread*, art::SignalSet&)+250)
    #03 pc 00000000004d9377  /system/lib64/libart.so (art::SignalCatcher::Run(void*)+279)
    #04 pc 0000000000092bab  /system/lib64/libc.so (__pthread_start(void*)+27)
    #05 pc 000000000002af2d  /system/lib64/libc.so (__start_thread+61)

    "ADB-JDWP Connec" sysTid=4328
    #00 pc 000000000007e35a  /system/lib64/libc.so (__ppoll+10)
    #01 pc 00000000000332d5  /system/lib64/libc.so (poll+69)
    #02 pc 0000000000006e46  /system/lib64/libadbconnection.so (adbconnection::AdbConnectionState::RunPollLoop(art::Thread*)+966)
    #03 pc 00000000000051db  /system/lib64/libadbconnection.so (adbconnection::CallbackFunction(void*)+1019)
    #04 pc 0000000000092bab  /system/lib64/libc.so (__pthread_start(void*)+27)
    #05 pc 000000000002af2d  /system/lib64/libc.so (__start_thread+61)

    "ReferenceQueueD" sysTid=4329
    #00 pc 0000000000026b98  /system/lib64/libc.so (syscall+24)
    #01 pc 00000000000d70bc  /system/lib64/libart.so (art::ConditionVariable::WaitHoldingLocks(art::Thread*)+108)
    #02 pc 00000000003ff20f  /system/lib64/libart.so (art::Monitor::Wait(art::Thread*, long, int, bool, art::ThreadState)+655)
    #03 pc 0000000000400db1  /system/lib64/libart.so (art::Monitor::Wait(art::Thread*, art::mirror::Object*, long, int, bool, art::ThreadState)+449)
    #04 pc 000000000011039d  /system/framework/x86_64/boot.oat (offset 0x110000) (java.lang.Object.notify [DEDUPED]+157)
    #05 pc 000000000018de2c  /system/framework/x86_64/boot-core-libart.oat (offset 0x77000) (java.lang.Daemons$ReferenceQueueDaemon.runInternal+124)
    #06 pc 00000000001178cf  /system/framework/x86_64/boot-core-libart.oat (offset 0x77000) (java.lang.Daemons$Daemon.run+79)
    #07 pc 0000000000276e01  /system/framework/x86_64/boot.oat (offset 0x110000) (java.lang.Thread.run+81)
    #08 pc 00000000005c3ab4  /system/lib64/libart.so (art_quick_invoke_stub+756)
    #09 pc 00000000000cf5f2  /system/lib64/libart.so (art::ArtMethod::Invoke(art::Thread*, unsigned int*, unsigned int, art::JValue*, char const*)+226)
    #10 pc 00000000004b7569  /system/lib64/libart.so (art::(anonymous namespace)::InvokeWithArgArray(art::ScopedObjectAccessAlreadyRunnable const&, art::ArtMethod*, art::(anonymous namespace)::ArgArray*, art::JValue*, char const*)+89)
    #11 pc 00000000004b883a  /system/lib64/libart.so (art::InvokeVirtualOrInterfaceWithJValues(art::ScopedObjectAccessAlreadyRunnable const&, _jobject*, _jmethodID*, jvalue*)+442)
    #12 pc 00000000004e7af8  /system/lib64/libart.so (art::Thread::CreateCallback(void*)+1352)
    #13 pc 0000000000092bab  /system/lib64/libc.so (__pthread_start(void*)+27)
    #14 pc 000000000002af2d  /system/lib64/libc.so (__start_thread+61)

    "FinalizerDaemon" sysTid=4330
    #00 pc 0000000000026b98  /system/lib64/libc.so (syscall+24)
    #01 pc 00000000000d70bc  /system/lib64/libart.so (art::ConditionVariable::WaitHoldingLocks(art::Thread*)+108)
    #02 pc 00000000003ff20f  /system/lib64/libart.so (art::Monitor::Wait(art::Thread*, long, int, bool, art::ThreadState)+655)
    #03 pc 0000000000400db1  /system/lib64/libart.so (art::Monitor::Wait(art::Thread*, art::mirror::Object*, long, int, bool, art::ThreadState)+449)
    #04 pc 00000000001104db  /system/framework/x86_64/boot.oat (offset 0x110000) (java.lang.Object.wait [DEDUPED]+187)
    #05 pc 000000000019705a  /system/framework/x86_64/boot.oat (offset 0x110000) (java.lang.ref.ReferenceQueue.remove+410)
    #06 pc 0000000000196e91  /system/framework/x86_64/boot.oat (offset 0x110000) (java.lang.ref.ReferenceQueue.remove+49)
    #07 pc 000000000018d232  /system/framework/x86_64/boot-core-libart.oat (offset 0x77000) (java.lang.Daemons$FinalizerDaemon.runInternal+354)
    #08 pc 00000000001178cf  /system/framework/x86_64/boot-core-libart.oat (offset 0x77000) (java.lang.Daemons$Daemon.run+79)
    #09 pc 0000000000276e01  /system/framework/x86_64/boot.oat (offset 0x110000) (java.lang.Thread.run+81)
    #10 pc 00000000005c3ab4  /system/lib64/libart.so (art_quick_invoke_stub+756)
    #11 pc 00000000000cf5f2  /system/lib64/libart.so (art::ArtMethod::Invoke(art::Thread*, unsigned int*, unsigned int, art::JValue*, char const*)+226)
    #12 pc 00000000004b7569  /system/lib64/libart.so (art::(anonymous namespace)::InvokeWithArgArray(art::ScopedObjectAccessAlreadyRunnable const&, art::ArtMethod*, art::(anonymous namespace)::ArgArray*, art::JValue*, char const*)+89)
    #13 pc 00000000004b883a  /system/lib64/libart.so (art::InvokeVirtualOrInterfaceWithJValues(art::ScopedObjectAccessAlreadyRunnable const&, _jobject*, _jmethodID*, jvalue*)+442)
    #14 pc 00000000004e7af8  /system/lib64/libart.so (art::Thread::CreateCallback(void*)+1352)
    #15 pc 0000000000092bab  /system/lib64/libc.so (__pthread_start(void*)+27)
    #16 pc 000000000002af2d  /system/lib64/libc.so (__start_thread+61)

    "FinalizerWatchd" sysTid=4331
    #00 pc 0000000000026b98  /system/lib64/libc.so (syscall+24)
    #01 pc 00000000000d70bc  /system/lib64/libart.so (art::ConditionVariable::WaitHoldingLocks(art::Thread*)+108)
    #02 pc 00000000003ff20f  /system/lib64/libart.so (art::Monitor::Wait(art::Thread*, long, int, bool, art::ThreadState)+655)
    #03 pc 0000000000400db1  /system/lib64/libart.so (art::Monitor::Wait(art::Thread*, art::mirror::Object*, long, int, bool, art::ThreadState)+449)
    #04 pc 000000000011039d  /system/framework/x86_64/boot.oat (offset 0x110000) (java.lang.Object.notify [DEDUPED]+157)
    #05 pc 000000000018d71d  /system/framework/x86_64/boot-core-libart.oat (offset 0x77000) (java.lang.Daemons$FinalizerWatchdogDaemon.sleepUntilNeeded+77)
    #06 pc 000000000018dade  /system/framework/x86_64/boot-core-libart.oat (offset 0x77000) (java.lang.Daemons$FinalizerWatchdogDaemon.runInternal+78)
    #07 pc 00000000001178cf  /system/framework/x86_64/boot-core-libart.oat (offset 0x77000) (java.lang.Daemons$Daemon.run+79)
    #08 pc 0000000000276e01  /system/framework/x86_64/boot.oat (offset 0x110000) (java.lang.Thread.run+81)
    #09 pc 00000000005c3ab4  /system/lib64/libart.so (art_quick_invoke_stub+756)
    #10 pc 00000000000cf5f2  /system/lib64/libart.so (art::ArtMethod::Invoke(art::Thread*, unsigned int*, unsigned int, art::JValue*, char const*)+226)
    #11 pc 00000000004b7569  /system/lib64/libart.so (art::(anonymous namespace)::InvokeWithArgArray(art::ScopedObjectAccessAlreadyRunnable const&, art::ArtMethod*, art::(anonymous namespace)::ArgArray*, art::JValue*, char const*)+89)
    #12 pc 00000000004b883a  /system/lib64/libart.so (art::InvokeVirtualOrInterfaceWithJValues(art::ScopedObjectAccessAlreadyRunnable const&, _jobject*, _jmethodID*, jvalue*)+442)
    #13 pc 00000000004e7af8  /system/lib64/libart.so (art::Thread::CreateCallback(void*)+1352)
    #14 pc 0000000000092bab  /system/lib64/libc.so (__pthread_start(void*)+27)
    #15 pc 000000000002af2d  /system/lib64/libc.so (__start_thread+61)

    "HeapTaskDaemon" sysTid=4332
    #00 pc 0000000000026b98  /system/lib64/libc.so (syscall+24)
    #01 pc 00000000000d70bc  /system/lib64/libart.so (art::ConditionVariable::WaitHoldingLocks(art::Thread*)+108)
    #02 pc 0000000000247800  /system/lib64/libart.so (art::gc::TaskProcessor::GetTask(art::Thread*)+368)
    #03 pc 000000000024807f  /system/lib64/libart.so (art::gc::TaskProcessor::RunAllTasks(art::Thread*)+63)
    #04 pc 0000000000079ced  /system/framework/x86_64/boot-core-libart.oat (offset 0x77000) (dalvik.system.VMRuntime.clampGrowthLimit [DEDUPED]+157)
    #05 pc 000000000018dd60  /system/framework/x86_64/boot-core-libart.oat (offset 0x77000) (java.lang.Daemons$HeapTaskDaemon.runInternal+208)
    #06 pc 00000000001178cf  /system/framework/x86_64/boot-core-libart.oat (offset 0x77000) (java.lang.Daemons$Daemon.run+79)
    #07 pc 0000000000276e01  /system/framework/x86_64/boot.oat (offset 0x110000) (java.lang.Thread.run+81)
    #08 pc 00000000005c3ab4  /system/lib64/libart.so (art_quick_invoke_stub+756)
    #09 pc 00000000000cf5f2  /system/lib64/libart.so (art::ArtMethod::Invoke(art::Thread*, unsigned int*, unsigned int, art::JValue*, char const*)+226)
    #10 pc 00000000004b7569  /system/lib64/libart.so (art::(anonymous namespace)::InvokeWithArgArray(art::ScopedObjectAccessAlreadyRunnable const&, art::ArtMethod*, art::(anonymous namespace)::ArgArray*, art::JValue*, char const*)+89)
    #11 pc 00000000004b883a  /system/lib64/libart.so (art::InvokeVirtualOrInterfaceWithJValues(art::ScopedObjectAccessAlreadyRunnable const&, _jobject*, _jmethodID*, jvalue*)+442)
    #12 pc 00000000004e7af8  /system/lib64/libart.so (art::Thread::CreateCallback(void*)+1352)
    #13 pc 0000000000092bab  /system/lib64/libc.so (__pthread_start(void*)+27)
    #14 pc 000000000002af2d  /system/lib64/libc.so (__start_thread+61)

    "Binder:4321_1" sysTid=4333
    #00 pc 000000000007e317  /system/lib64/libc.so (__ioctl+7)
    #01 pc 0000000000030cde  /system/lib64/libc.so (ioctl+206)
    #02 pc 000000000005b40e  /system/lib64/libbinder.so (android::IPCThreadState::talkWithDriver(bool)+270)
    #03 pc 000000000005b5f0  /system/lib64/libbinder.so (android::IPCThreadState::getAndExecuteCommand()+16)
    #04 pc 000000000005bdd1  /system/lib64/libbinder.so (android::IPCThreadState::joinThreadPool(bool)+49)
    #05 pc 0000000000082277  /system/lib64/libbinder.so (android::PoolThread::threadLoop()+23)
    #06 pc 000000000000f79a  /system/lib64/libutils.so (android::Thread::_threadLoop(void*)+314)
    #07 pc 00000000000b5573  /system/lib64/libandroid_runtime.so (android::AndroidRuntime::javaThreadShell(void*)+131)
    #08 pc 0000000000092bab  /system/lib64/libc.so (__pthread_start(void*)+27)
    #09 pc 000000000002af2d  /system/lib64/libc.so (__start_thread+61)

    "Binder:4321_2" sysTid=4334
    #00 pc 000000000007e317  /system/lib64/libc.so (__ioctl+7)
    #01 pc 0000000000030cde  /system/lib64/libc.so (ioctl+206)
    #02 pc 000000000005b40e  /system/lib64/libbinder.so (android::IPCThreadState::talkWithDriver(bool)+270)
    #03 pc 000000000005b5f0  /system/lib64/libbinder.so (android::IPCThreadState::getAndExecuteCommand()+16)
    #04 pc 000000000005bdd1  /system/lib64/libbinder.so (android::IPCThreadState::joinThreadPool(bool)+49)
    #05 pc 0000000000082277  /system/lib64/libbinder.so (android::PoolThread::threadLoop()+23)
    #06 pc 000000000000f79a  /system/lib64/libutils.so (android::Thread::_threadLoop(void*)+314)
    #07 pc 00000000000b5573  /system/lib64/libandroid_runtime.so (android::AndroidRuntime::javaThreadShell(void*)+131)
    #08 pc 0000000000092bab  /system/lib64/libc.so (__pthread_start(void*)+27)
    #09 pc 000000000002af2d  /system/lib64/libc.so (__start_thread+61)

    "Binder:4321_3" sysTid=4335
    #00 pc 000000000007e317  /system/lib64/libc.so (__ioctl+7)
    #01 pc 0000000000030cde  /system/lib64/libc.so (ioctl+206)
    #02 pc 000000000005b40e  /system/lib64/libbinder.so (android::IPCThreadState::talkWithDriver(bool)+270)
    #03 pc 000000000005b5f0  /system/lib64/libbinder.so (android::IPCThreadState::getAndExecuteCommand()+16)
    #04 pc 000000000005bdd1  /system/lib64/libbinder.so (android::IPCThreadState::joinThreadPool(bool)+49)
    #05 pc 0000000000082277  /system/lib64/libbinder.so (android::PoolThread::threadLoop()+23)
    #06 pc 000000000000f79a  /system/lib64/libutils.so (android::Thread::_threadLoop(void*)+314)
    #07 pc 00000000000b5573  /system/lib64/libandroid_runtime.so (android::AndroidRuntime::javaThreadShell(void*)+131)
    #08 pc 0000000000092bab  /system/lib64/libc.so (__pthread_start(void*)+27)
    #09 pc 000000000002af2d  /system/lib64/libc.so (__start_thread+61)

    "Profile Saver" sysTid=4336
    #00 pc 0000000000026b98  /system/lib64/libc.so (syscall+24)
    #01 pc 00000000000d70bc  /system/lib64/libart.so (art::ConditionVariable::WaitHoldingLocks(art::Thread*)+108)
    #02 pc 000000000035ef6d  /system/lib64/libart.so (art::ProfileSaver::Run()+381)
    #03 pc 0000000000362cd7  /system/lib64/libart.so (art::ProfileSaver::RunProfileSaverThread(void*)+87)
    #04 pc 0000000000092bab  /system/lib64/libc.so (__pthread_start(void*)+27)
    #05 pc 000000000002af2d  /system/lib64/libc.so (__start_thread+61)

    "queued-work-loo" sysTid=4340
    #00 pc 000000000007e1da  /system/lib64/libc.so (__epoll_pwait+10)
    #01 pc 0000000000013d12  /system/lib64/libutils.so (android::Looper::pollInner(int)+162)
    #02 pc 0000000000013bc9  /system/lib64/libutils.so (android::Looper::pollOnce(int, int*, int*, void**)+41)
    #03 pc 000000000011ceb5  /system/lib64/libandroid_runtime.so (android::android_os_MessageQueue_nativePollOnce(_JNIEnv*, _jobject*, long, int)+37)
    #04 pc 00000000003dce2b  /system/framework/x86_64/boot-framework.oat (offset 0x3c3000) (android.media.MediaExtractor.seekTo [DEDUPED]+187)
    #05 pc 0000000000ac225c  /system/framework/x86_64/boot-framework.oat (offset 0x3c3000) (android.os.MessageQueue.next+220)
    #06 pc 0000000000abfaa6  /system/framework/x86_64/boot-framework.oat (offset 0x3c3000) (android.os.Looper.loop+518)
    #07 pc 0000000000abec8e  /system/framework/x86_64/boot-framework.oat (offset 0x3c3000) (android.os.HandlerThread.run+510)
    #08 pc 00000000005c3ab4  /system/lib64/libart.so (art_quick_invoke_stub+756)
    #09 pc 00000000000cf5f2  /system/lib64/libart.so (art::ArtMethod::Invoke(art::Thread*, unsigned int*, unsigned int, art::JValue*, char const*)+226)
    #10 pc 00000000004b7569  /system/lib64/libart.so (art::(anonymous namespace)::InvokeWithArgArray(art::ScopedObjectAccessAlreadyRunnable const&, art::ArtMethod*, art::(anonymous namespace)::ArgArray*, art::JValue*, char const*)+89)
    #11 pc 00000000004b883a  /system/lib64/libart.so (art::InvokeVirtualOrInterfaceWithJValues(art::ScopedObjectAccessAlreadyRunnable const&, _jobject*, _jmethodID*, jvalue*)+442)
    #12 pc 00000000004e7af8  /system/lib64/libart.so (art::Thread::CreateCallback(void*)+1352)
    #13 pc 0000000000092bab  /system/lib64/libc.so (__pthread_start(void*)+27)
    #14 pc 000000000002af2d  /system/lib64/libc.so (__start_thread+61)

    "app-indexing" sysTid=4452
    #00 pc 000000000007e1da  /system/lib64/libc.so (__epoll_pwait+10)
    #01 pc 0000000000013d12  /system/lib64/libutils.so (android::Looper::pollInner(int)+162)
    #02 pc 0000000000013bc9  /system/lib64/libutils.so (android::Looper::pollOnce(int, int*, int*, void**)+41)
    #03 pc 000000000011ceb5  /system/lib64/libandroid_runtime.so (android::android_os_MessageQueue_nativePollOnce(_JNIEnv*, _jobject*, long, int)+37)
    #04 pc 00000000003dce2b  /system/framework/x86_64/boot-framework.oat (offset 0x3c3000) (android.media.MediaExtractor.seekTo [DEDUPED]+187)
    #05 pc 0000000000ac225c  /system/framework/x86_64/boot-framework.oat (offset 0x3c3000) (android.os.MessageQueue.next+220)
    #06 pc 0000000000abfaa6  /system/framework/x86_64/boot-framework.oat (offset 0x3c3000) (android.os.Looper.loop+518)
    #07 pc 0000000000abec8e  /system/framework/x86_64/boot-framework.oat (offset 0x3c3000) (android.os.HandlerThread.run+510)
    #08 pc 00000000005c3ab4  /system/lib64/libart.so (art_quick_invoke_stub+756)
    #09 pc 00000000000cf5f2  /system/lib64/libart.so (art::ArtMethod::Invoke(art::Thread*, unsigned int*, unsigned int, art::JValue*, char const*)+226)
    #10 pc 00000000004b7569  /system/lib64/libart.so (art::(anonymous namespace)::InvokeWithArgArray(art::ScopedObjectAccessAlreadyRunnable const&, art::ArtMethod*, art::(anonymous namespace)::ArgArray*, art::JValue*, char const*)+89)
    #11 pc 00000000004b883a  /system/lib64/libart.so (art::InvokeVirtualOrInterfaceWithJValues(art::ScopedObjectAccessAlreadyRunnable const&, _jobject*, _jmethodID*, jvalue*)+442)
    #12 pc 00000000004e7af8  /system/lib64/libart.so (art::Thread::CreateCallback(void*)+1352)
    #13 pc 0000000000092bab  /system/lib64/libc.so (__pthread_start(void*)+27)
    #14 pc 000000000002af2d  /system/lib64/libc.so (__start_thread+61)

    "GAC_Executor[0]" sysTid=4455
    #00 pc 0000000000026b98  /system/lib64/libc.so (syscall+24)
    #01 pc 00000000000d70bc  /system/lib64/libart.so (art::ConditionVariable::WaitHoldingLocks(art::Thread*)+108)
    #02 pc 00000000003ff20f  /system/lib64/libart.so (art::Monitor::Wait(art::Thread*, long, int, bool, art::ThreadState)+655)
    #03 pc 0000000000400db1  /system/lib64/libart.so (art::Monitor::Wait(art::Thread*, art::mirror::Object*, long, int, bool, art::ThreadState)+449)
    #04 pc 00000000001104db  /system/framework/x86_64/boot.oat (offset 0x110000) (java.lang.Object.wait [DEDUPED]+187)
    #05 pc 0000000000276c79  /system/framework/x86_64/boot.oat (offset 0x110000) (java.lang.Thread.parkFor$+457)
    #06 pc 00000000002f51a1  /system/framework/x86_64/boot.oat (offset 0x110000) (java.util.concurrent.locks.AbstractQueuedSynchronizer$ConditionObject.await+945)
    #07 pc 0000000000465308  /system/framework/x86_64/boot.oat (offset 0x110000) (java.util.concurrent.LinkedBlockingQueue.take+152)
    #08 pc 0000000000416079  /system/framework/x86_64/boot.oat (offset 0x110000) (java.util.concurrent.ThreadPoolExecutor.getTask+521)
    #09 pc 0000000000417dbf  /system/framework/x86_64/boot.oat (offset 0x110000) (java.util.concurrent.ThreadPoolExecutor.runWorker+239)
    #10 pc 0000000000414af3  /system/framework/x86_64/boot.oat (offset 0x110000) (java.util.concurrent.ThreadPoolExecutor$Worker.run+67)
    #11 pc 00000000005c3ab4  /system/lib64/libart.so (art_quick_invoke_stub+756)
    #12 pc 00000000000cf5f2  /system/lib64/libart.so (art::ArtMethod::Invoke(art::Thread*, unsigned int*, unsigned int, art::JValue*, char const*)+226)
    #13 pc 00000000002a1b91  /system/lib64/libart.so (art::interpreter::ArtInterpreterToCompiledCodeBridge(art::Thread*, art::ArtMethod*, art::ShadowFrame*, unsigned short, art::JValue*)+321)
    #14 pc 000000000029ac6d  /system/lib64/libart.so (bool art::interpreter::DoCall<false, false>(art::ArtMethod*, art::Thread*, art::ShadowFrame&, art::Instruction const*, unsigned short, art::JValue*)+1261)
    #15 pc 0000000000590b58  /system/lib64/libart.so (MterpInvokeInterface+1480)
    #16 pc 00000000005b5199  /system/lib64/libart.so (ExecuteMterpImpl+14745)
    #17 pc 00000000001264ca  /system/app/PrebuiltDeskClockGoogle/oat/x86_64/PrebuiltDeskClockGoogle.vdex (cff.run+14)
    #18 pc 0000000000271ee1  /system/lib64/libart.so (_ZN3art11interpreterL7ExecuteEPNS_6ThreadERKNS_20CodeItemDataAccessorERNS_11ShadowFrameENS_6JValueEb.llvm.2620325170+561)
    #19 pc 000000000057e547  /system/lib64/libart.so (artQuickToInterpreterBridge+1223)
    #20 pc 00000000005ce1ec  /system/lib64/libart.so (art_quick_to_interpreter_bridge+140)
    #21 pc 0000000000276e01  /system/framework/x86_64/boot.oat (offset 0x110000) (java.lang.Thread.run+81)
    #22 pc 00000000005c3ab4  /system/lib64/libart.so (art_quick_invoke_stub+756)
    #23 pc 00000000000cf5f2  /system/lib64/libart.so (art::ArtMethod::Invoke(art::Thread*, unsigned int*, unsigned int, art::JValue*, char const*)+226)
    #24 pc 00000000004b7569  /system/lib64/libart.so (art::(anonymous namespace)::InvokeWithArgArray(art::ScopedObjectAccessAlreadyRunnable const&, art::ArtMethod*, art::(anonymous namespace)::ArgArray*, art::JValue*, char const*)+89)
    #25 pc 00000000004b883a  /system/lib64/libart.so (art::InvokeVirtualOrInterfaceWithJValues(art::ScopedObjectAccessAlreadyRunnable const&, _jobject*, _jmethodID*, jvalue*)+442)
    #26 pc 00000000004e7af8  /system/lib64/libart.so (art::Thread::CreateCallback(void*)+1352)
    #27 pc 0000000000092bab  /system/lib64/libc.so (__pthread_start(void*)+27)
    #28 pc 000000000002af2d  /system/lib64/libc.so (__start_thread+61)

    "GAC_Executor[1]" sysTid=4457
    #00 pc 0000000000026b98  /system/lib64/libc.so (syscall+24)
    #01 pc 00000000000d70bc  /system/lib64/libart.so (art::ConditionVariable::WaitHoldingLocks(art::Thread*)+108)
    #02 pc 00000000003ff20f  /system/lib64/libart.so (art::Monitor::Wait(art::Thread*, long, int, bool, art::ThreadState)+655)
    #03 pc 0000000000400db1  /system/lib64/libart.so (art::Monitor::Wait(art::Thread*, art::mirror::Object*, long, int, bool, art::ThreadState)+449)
    #04 pc 00000000001104db  /system/framework/x86_64/boot.oat (offset 0x110000) (java.lang.Object.wait [DEDUPED]+187)
    #05 pc 0000000000276c79  /system/framework/x86_64/boot.oat (offset 0x110000) (java.lang.Thread.parkFor$+457)
    #06 pc 00000000002f51a1  /system/framework/x86_64/boot.oat (offset 0x110000) (java.util.concurrent.locks.AbstractQueuedSynchronizer$ConditionObject.await+945)
    #07 pc 0000000000465308  /system/framework/x86_64/boot.oat (offset 0x110000) (java.util.concurrent.LinkedBlockingQueue.take+152)
    #08 pc 0000000000416079  /system/framework/x86_64/boot.oat (offset 0x110000) (java.util.concurrent.ThreadPoolExecutor.getTask+521)
    #09 pc 0000000000417dbf  /system/framework/x86_64/boot.oat (offset 0x110000) (java.util.concurrent.ThreadPoolExecutor.runWorker+239)
    #10 pc 0000000000414af3  /system/framework/x86_64/boot.oat (offset 0x110000) (java.util.concurrent.ThreadPoolExecutor$Worker.run+67)
    #11 pc 00000000005c3ab4  /system/lib64/libart.so (art_quick_invoke_stub+756)
    #12 pc 00000000000cf5f2  /system/lib64/libart.so (art::ArtMethod::Invoke(art::Thread*, unsigned int*, unsigned int, art::JValue*, char const*)+226)
    #13 pc 00000000002a1b91  /system/lib64/libart.so (art::interpreter::ArtInterpreterToCompiledCodeBridge(art::Thread*, art::ArtMethod*, art::ShadowFrame*, unsigned short, art::JValue*)+321)
    #14 pc 000000000029ac6d  /system/lib64/libart.so (bool art::interpreter::DoCall<false, false>(art::ArtMethod*, art::Thread*, art::ShadowFrame&, art::Instruction const*, unsigned short, art::JValue*)+1261)
    #15 pc 0000000000590b58  /system/lib64/libart.so (MterpInvokeInterface+1480)
    #16 pc 00000000005b5199  /system/lib64/libart.so (ExecuteMterpImpl+14745)
    #17 pc 00000000001264ca  /system/app/PrebuiltDeskClockGoogle/oat/x86_64/PrebuiltDeskClockGoogle.vdex (cff.run+14)
    #18 pc 0000000000271ee1  /system/lib64/libart.so (_ZN3art11interpreterL7ExecuteEPNS_6ThreadERKNS_20CodeItemDataAccessorERNS_11ShadowFrameENS_6JValueEb.llvm.2620325170+561)
    #19 pc 000000000057e547  /system/lib64/libart.so (artQuickToInterpreterBridge+1223)
    #20 pc 00000000005ce1ec  /system/lib64/libart.so (art_quick_to_interpreter_bridge+140)
    #21 pc 0000000000276e01  /system/framework/x86_64/boot.oat (offset 0x110000) (java.lang.Thread.run+81)
    #22 pc 00000000005c3ab4  /system/lib64/libart.so (art_quick_invoke_stub+756)
    #23 pc 00000000000cf5f2  /system/lib64/libart.so (art::ArtMethod::Invoke(art::Thread*, unsigned int*, unsigned int, art::JValue*, char const*)+226)
    #24 pc 00000000004b7569  /system/lib64/libart.so (art::(anonymous namespace)::InvokeWithArgArray(art::ScopedObjectAccessAlreadyRunnable const&, art::ArtMethod*, art::(anonymous namespace)::ArgArray*, art::JValue*, char const*)+89)
    #25 pc 00000000004b883a  /system/lib64/libart.so (art::InvokeVirtualOrInterfaceWithJValues(art::ScopedObjectAccessAlreadyRunnable const&, _jobject*, _jmethodID*, jvalue*)+442)
    #26 pc 00000000004e7af8  /system/lib64/libart.so (art::Thread::CreateCallback(void*)+1352)
    #27 pc 0000000000092bab  /system/lib64/libc.so (__pthread_start(void*)+27)
    #28 pc 000000000002af2d  /system/lib64/libc.so (__start_thread+61)

    "Binder:4321_4" sysTid=4819
    #00 pc 000000000007e317  /system/lib64/libc.so (__ioctl+7)
    #01 pc 0000000000030cde  /system/lib64/libc.so (ioctl+206)
    #02 pc 000000000005b40e  /system/lib64/libbinder.so (android::IPCThreadState::talkWithDriver(bool)+270)
    #03 pc 000000000005b5f0  /system/lib64/libbinder.so (android::IPCThreadState::getAndExecuteCommand()+16)
    #04 pc 000000000005bdd1  /system/lib64/libbinder.so (android::IPCThreadState::joinThreadPool(bool)+49)
    #05 pc 0000000000082277  /system/lib64/libbinder.so (android::PoolThread::threadLoop()+23)
    #06 pc 000000000000f79a  /system/lib64/libutils.so (android::Thread::_threadLoop(void*)+314)
    #07 pc 00000000000b5573  /system/lib64/libandroid_runtime.so (android::AndroidRuntime::javaThreadShell(void*)+131)
    #08 pc 0000000000092bab  /system/lib64/libc.so (__pthread_start(void*)+27)
    #09 pc 000000000002af2d  /system/lib64/libc.so (__start_thread+61)

    "Binder:4321_5" sysTid=4941
    #00 pc 000000000007e317  /system/lib64/libc.so (__ioctl+7)
    #01 pc 0000000000030cde  /system/lib64/libc.so (ioctl+206)
    #02 pc 000000000005b40e  /system/lib64/libbinder.so (android::IPCThreadState::talkWithDriver(bool)+270)
    #03 pc 000000000005b5f0  /system/lib64/libbinder.so (android::IPCThreadState::getAndExecuteCommand()+16)
    #04 pc 000000000005bdd1  /system/lib64/libbinder.so (android::IPCThreadState::joinThreadPool(bool)+49)
    #05 pc 0000000000082277  /system/lib64/libbinder.so (android::PoolThread::threadLoop()+23)
    #06 pc 000000000000f79a  /system/lib64/libutils.so (android::Thread::_threadLoop(void*)+314)
    #07 pc 00000000000b5573  /system/lib64/libandroid_runtime.so (android::AndroidRuntime::javaThreadShell(void*)+131)
    #08 pc 0000000000092bab  /system/lib64/libc.so (__pthread_start(void*)+27)
    #09 pc 000000000002af2d  /system/lib64/libc.so (__start_thread+61)

    "Binder:4321_6" sysTid=5370
    #00 pc 000000000007e317  /system/lib64/libc.so (__ioctl+7)
    #01 pc 0000000000030cde  /system/lib64/libc.so (ioctl+206)
    #02 pc 000000000005b40e  /system/lib64/libbinder.so (android::IPCThreadState::talkWithDriver(bool)+270)
    #03 pc 000000000005b5f0  /system/lib64/libbinder.so (android::IPCThreadState::getAndExecuteCommand()+16)
    #04 pc 000000000005bdd1  /system/lib64/libbinder.so (android::IPCThreadState::joinThreadPool(bool)+49)
    #05 pc 0000000000082277  /system/lib64/libbinder.so (android::PoolThread::threadLoop()+23)
    #06 pc 000000000000f79a  /system/lib64/libutils.so (android::Thread::_threadLoop(void*)+314)
    #07 pc 00000000000b5573  /system/lib64/libandroid_runtime.so (android::AndroidRuntime::javaThreadShell(void*)+131)
    #08 pc 0000000000092bab  /system/lib64/libc.so (__pthread_start(void*)+27)
    #09 pc 000000000002af2d  /system/lib64/libc.so (__start_thread+61)

    ----- end 4321 -----

