Title: 어플리케이션 Crash 처리하기
Slug: 2016_06_22_handle_crash
Date: 2016-06-22 19:00
Category: tech
Tags: linux, ubuntu, android
Author: YOUNG HO CHA
Summary: 리눅스에서 어플리케이션 crash가 처리되는 방법

최근 리눅스 배포판들은 c 런타임에서 어플리케이션의 버그나 이상동작으로 인해 중단될 때, crash report 설비를 이용해서 어떤 어플리케이션이 무슨 이유로 인해 중단되었는지 확인할 수 있게 해준다.
crash report 처리기들이 어떠한 방식으로 데이터를 구동되는지 대충 살펴보도록 하자.

# [/proc/sys/kernel/core_pattern](https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/tree/Documentation/sysctl/kernel.txt?h=v4.4#n182) 이용하기

core_pattern 은 프로그램이 오류가 발생했을 때 생성할 메모리 덤프파일의 이름 형식을 지정할 때 사용한다. 하지만 [파일이름을 등록할 때 맨 앞에 ‘|’ 로 시작](https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/tree/fs/coredump.c?h=v4.4#n561)하면 저장할 파일이름 대신 ‘|’ 뒤를 실행파일로 취급하고 표준입력으로 메모리 내용을 건네준다.
이를 이용해서 동작하는 프로그램은 다음과 같다.

## systemd: [systemd-coredump](https://www.freedesktop.org/software/systemd/man/systemd-coredump.html)

systemd를 사용하는 시스템에서는 [sysctl을 이용해 systemd-coredump를 core_pattern에 등록](https://github.com/systemd/systemd/blob/master/sysctl.d/50-coredump.conf.in)한다. 그리고 오류가 발생하면, 해당 프로세스의 스택은 물론, systemd 에 의존적인 정보까지 추가해서 기록한다.
이렇게 기록된 정보는 아래의 명령을 이용해서 확인할 수 있다.

    $ coredumpctl info
               PID: 1849 (nautilus)
               UID: 1000 (ganadist)
               GID: 100 (users)
            Signal: 6 (ABRT)
         Timestamp: 일 2016-04-24 16:07:38 KST (1 months 27 days ago)
      Command Line: nautilus -n
        Executable: /usr/bin/nautilus
     Control Group: /user.slice/user-1000.slice/session-c4.scope
              Unit: session-c4.scope
             Slice: user-1000.slice
           Session: c4
         Owner UID: 1000 (ganadist)
           Boot ID: f83aada45fed429299c962af79ea736d
        Machine ID: 3cfa38b6a39d4190be174d821f3d8e30
          Hostname: ganadist
           Message: Process 1849 (nautilus) of user 1000 dumped core.

                    Stack trace of thread 1849:
                    #0  0x00007fe516a212a8 raise (libc.so.6)
                    #1  0x00007fe516a2272a abort (libc.so.6)
                    #2  0x00007fe51789eb25 g_assertion_message (libglib-2.0.so.0)
                    #3  0x00007fe51789ebba g_assertion_message_expr (libglib-2.0.so.0)
                    #4  0x0000000000488a01 n/a (nautilus)
                    #5  0x000000000048bba7 n/a (nautilus)
                    #6  0x0000000000435288 n/a (nautilus)
                    #7  0x0000000000436333 n/a (nautilus)
                    #8  0x00007fe517b51518 g_cclosure_marshal_VOID__ENUMv (libgobject-2.0.so.0)
                    #9  0x00007fe517b4f1d4 n/a (libgobject-2.0.so.0)
                    #10 0x00007fe517b699d6 g_signal_emit_valist (libgobject-2.0.so.0)
                    #11 0x00007fe517b6a0bf g_signal_emit (libgobject-2.0.so.0)
                    #12 0x0000000000444fac n/a (nautilus)
                    #13 0x000000000044526f n/a (nautilus)
                    #14 0x00007fe517879823 n/a (libglib-2.0.so.0)
                    #15 0x00007fe517878dba g_main_context_dispatch (libglib-2.0.so.0)
                    #16 0x00007fe517879160 n/a (libglib-2.0.so.0)
                    #17 0x00007fe51787920c g_main_context_iteration (libglib-2.0.so.0)
                    #18 0x00007fe517e3eafd g_application_run (libgio-2.0.so.0)
                    #19 0x00000000004294e7 n/a (nautilus)
                    #20 0x00007fe516a0e710 __libc_start_main (libc.so.6)
                    #21 0x0000000000429549 n/a (nautilus)

                    Stack trace of thread 1933:
                    #0  0x00007fe516ad17f9 syscall (libc.so.6)
                    #1  0x00007fe5178bdafa g_cond_wait_until (libglib-2.0.so.0)
                    #2  0x00007fe51784d929 n/a (libglib-2.0.so.0)
                    #3  0x00007fe5178a02e6 n/a (libglib-2.0.so.0)
                    #4  0x00007fe51789f975 n/a (libglib-2.0.so.0)
                    #5  0x00007fe516d96424 start_thread (libpthread.so.0)
                    #6  0x00007fe516ad5cbd __clone (libc.so.6)


## [Apport](https://wiki.ubuntu.com/Apport)

우분투 리눅스에서는 apport 라고하는 crash report 도구가 존재하며, [init 스크립트에서 core_pattern에 등록](http://bazaar.launchpad.net/~ubuntu-core-dev/ubuntu/xenial/apport/ubuntu/view/head:/etc/init.d/apport#L52)한다. 또한 apport에는 몇가지 추가동작을 하게 되는데 다음과 같다.

 * 오류 동작시 [실행환경을 분석](http://bazaar.launchpad.net/~ubuntu-core-dev/ubuntu/xenial/apport/ubuntu/view/head:/bin/apport-bug#L57)하여, gnome, kde 또는 cli 에 해당하는 UI를 보여줌

 * c 런타임에서 발생하는 메모리 오류 이외에 여러가지 상황에 대한 오류분석이 추가되어 있다.

   * python 해석기에서 예외가 발생할 때 처리할 수 있는 [예외 처리기가 포함](http://bazaar.launchpad.net/~ubuntu-core-dev/ubuntu/xenial/apport/ubuntu/view/head:/apport_python_hook.py#L200)되어 있다.

   * [intel wifi 드라이버에서 오류가 발생](http://bazaar.launchpad.net/~ubuntu-core-dev/ubuntu/xenial/apport/ubuntu/view/head:/udev/50-apport.rules)할 경우, [오류를 수집 분석](http://bazaar.launchpad.net/~ubuntu-core-dev/ubuntu/xenial/apport/ubuntu/view/head:/data/iwlwifi_error_dump)한다.

   * 뭔가 자바쪽도 bootclasspath에 등록할 것 같은데 귀찮아서 못뒤벼보겠..(..)

   * 그외 오류 패턴별로 우분투의 이슈추적시스템인 launchpad에 등록된 것과 일치하는 것을 뒤벼주는 것도 포함되어 있다.

   * 당연히 오류를 launchpad에 업로드 하는 기능도 있다.

   * 어쨌든 본인은 우분투를 사용하지 않는다... (먼산)


# Android에서 Crash 처리하기

## c 런타임의 오류 처리

Android에서는 리눅스에서 제공하는 core_pattern 대신 [linker에서 어플리케이션을 실행할 때 signal handler를 등록](https://android.googlesource.com/platform/bionic/+/android-6.0.1_r46/linker/debugger.cpp#296)한다.

그리고 오류가 발생할 때 커널에서 보내는 여러가지 [signal(SIGABRT, SIGFPE, SIGSEGV, SIGBUS, SIGTRAP) 등을 받아서](https://android.googlesource.com/platform/bionic/+/android-6.0.1_r46/linker/debugger.cpp#257) [debuggerd에게 처리해달라고 요청](https://android.googlesource.com/platform/bionic/+/android-6.0.1_r46/linker/debugger.cpp#206)하게 되고, debuggerd는 요청한 프로세스에 대해 [tombstone 이라는 형식으로 프로세스의 스택에 대한 정보를 파일로 저장](https://android.googlesource.com/platform/system/core/+/android-6.0.1_r46/debuggerd/tombstone.cpp#783)하게 된다. 그리고 이렇게 저장된 tombstone 형식의 파일은 [안드로이드가 다음 부팅](https://android.googlesource.com/platform/frameworks/base/+/android-6.0.1_r46/core/java/com/android/server/BootReceiver.java#63)될 때 [dropbox 라고 하는 android os의  로그 서비스 저장소](https://android.googlesource.com/platform/frameworks/base/+/android-6.0.1_r46/core/java/com/android/server/BootReceiver.java#153)로 옮겨지게 된다.

## dalvik 런타임의 오류 처리

[Zygote 가 초기화](https://android.googlesource.com/platform/frameworks/base/+/android-6.0.1_r46/core/java/com/android/internal/os/RuntimeInit.java#256) 될 때 [ActivityManagerService 에서 crash를 처리](https://android.googlesource.com/platform/frameworks/base/+/android-6.0.1_r46/core/java/com/android/internal/os/RuntimeInit.java#89)할 수 있는 [기본 예외 처리기](https://android.googlesource.com/platform/frameworks/base/+/android-6.0.1_r46/core/java/com/android/internal/os/RuntimeInit.java#64)를 [등록](https://android.googlesource.com/platform/frameworks/base/+/android-6.0.1_r46/core/java/com/android/internal/os/RuntimeInit.java#109)하게 된다.

ActivityManagerService에서는 [dropbox에 crash 정보를 저장](https://android.googlesource.com/platform/frameworks/base/+/android-6.0.1_r46/services/core/java/com/android/server/am/ActivityManagerService.java#12127)하고,  [os 에 지정된 crash report 어플리케이션](https://android.googlesource.com/platform/frameworks/base/+/android-6.0.1_r46/core/java/android/app/ApplicationErrorReport.java#159)이 있으며, [사용자가 해당 앱을 사용하겠다고 선택](https://android.googlesource.com/platform/frameworks/base/+/android-6.0.1_r46/services/core/java/com/android/server/am/AppErrorDialog.java#66)하면, [해당 앱을 이용해 오류정보를 전송](https://android.googlesource.com/platform/frameworks/base/+/android-6.0.1_r46/services/core/java/com/android/server/am/ActivityManagerService.java#12648)하게 된다.

## dropbox에 저장된 오류 확인하기

아래의 [SYSTEM_TOMBSTONE](https://android.googlesource.com/platform/frameworks/base/+/android-6.0.1_r46/core/java/com/android/server/BootReceiver.java#157) 옵션은 tombstone 에 대한 오류에 대해 조회하는 명령이며, app crash는 앱의 설치 위치에 따라 [system_app](https://android.googlesource.com/platform/frameworks/base/+/android-6.0.1_r46/services/core/java/com/android/server/am/ActivityManagerService.java#12436)_crash, 또는 [data_app](https://android.googlesource.com/platform/frameworks/base/+/android-6.0.1_r46/services/core/java/com/android/server/am/ActivityManagerService.java#12439)_crash 등의 옵션으로 조회가 가능하다.

    $ adb shell dumpsys dropbox --print SYSTEM_TOMBSTONE
    Drop box contents: 634 entries
    Searching for: SYSTEM_TOMBSTONE

    ========================================
    2016-06-21 18:21:15 SYSTEM_TOMBSTONE (compressed text, 6361 bytes)
    Build: google/hammerhead/hammerhead:6.0.1/MOB30M/2862625:user/release-keys
    Hardware: hammerhead
    Revision: 11
    Bootloader: HHZ20f
    Radio: unknown
    Kernel: Linux version 3.4.0-g6a99a02 (android-build@wpdt13.hot.corp.google.com) (gcc version 4.8 (GCC) ) #1 SMP PREEMPT Wed Apr 20 00:08:32 UTC 2016

    *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** ***
    Build fingerprint: 'google/hammerhead/hammerhead:6.0.1/MOB30M/2862625:user/release-keys'
    Revision: '11'
    ABI: 'arm'
    pid: 224, tid: 224, name: mm-qcamera-daem  >>> /system/bin/mm-qcamera-daemon <<<
    signal 11 (SIGSEGV), code 1 (SEGV_MAPERR), fault addr 0x357b9a70
        r0 000000a8  r1 b48c1290  r2 00800000  r3 b48c1299
        r4 b48c1298  r5 357b9a60  r6 b6b55300  r7 b48c1298
        r8 b48c0000  r9 000000a7  sl 000000a3  fp b48c1538
        ip 00000038  sp bedae540  lr b6d78920  pc b6d42128  cpsr 800f0030
        d0  2064656c69616620  d1  735f74696e695f73
        d2  0000000000000073  d3  0000000000000069
        d4  0000000600000001  d5  c01e33f0c300a020
        d6  c11a644000000000  d7  c300bd20c300bd64
        d8  0000000000000000  d9  0000000000000000
        d10 0000000000000000  d11 0000000000000000
        d12 0000000000000000  d13 0000000000000000
        d14 0000000000000000  d15 0000000000000000
        d16 0000000000000000  d17 0000000000000000
        d18 3fe0000000000000  d19 3fe0000000000000
        d20 3fe0000000000000  d21 bfe0000000000000
        d22 4053bd6de0000000  d23 3fe0000000000000
        d24 4053dd6de0000000  d25 3ff30a3d70a3d70a
        d26 3ff6a0902de00d1b  d27 40a65cae7d566cf4
        d28 40b13c51eb851eb9  d29 406d038366516db1
        d30 40ad038366516db1  d31 4072d11eb851eb85
        scr 20000011

    backtrace:
        #00 pc 0004b128  /system/lib/libc.so (arena_dalloc_bin_locked_impl.isra.27+299)
        #01 pc 0005c32f  /system/lib/libc.so (je_tcache_bin_flush_small+206)
        #02 pc 000553cb  /system/lib/libc.so (ifree+290)
        #03 pc 00058257  /system/lib/libc.so (je_free+374)
        #04 pc 000034d7  /system/vendor/lib/libmmcamera2_sensor_modules.so
        #05 pc 00005853  /system/vendor/lib/libmmcamera2_sensor_modules.so
        #06 pc 00007189  /system/vendor/lib/liboemcamera.so (mct_list_traverse+26)
        #07 pc 00004d55  /system/vendor/lib/liboemcamera.so (mct_pipeline_start_session+16)
        #08 pc 00002b3f  /system/vendor/lib/liboemcamera.so (mct_controller_new+50)
        #09 pc 000016b3  /system/bin/mm-qcamera-daemon
        #10 pc 00001205  /system/bin/mm-qcamera-daemon (main+520)
        #11 pc 00017359  /system/lib/libc.so (__libc_init+44)
        #12 pc 0000148c  /system/bin/mm-qcamera-daemon

    stack:
             bedae500  bedae4e4  [stack]
             bedae504  bedae4e4  [stack]
             bedae508  b6680000
             bedae50c  b6d792f0
             bedae510  b6d792e0
             bedae514  00100000
             bedae518  00000000
             bedae51c  00000002
             bedae520  b6b556f8  [anon:libc_malloc]
             bedae524  b6b55300  [anon:libc_malloc]
             bedae528  b48c1394  [anon:libc_malloc]
             bedae52c  b48c0000  [anon:libc_malloc]
             bedae530  b6b556f8  [anon:libc_malloc]
             bedae534  00000000
             bedae538  00000002
             bedae53c  b6d421f7  /system/lib/libc.so (arena_dalloc_bin_locked_impl.isra.27+506)
        #00  bedae540  00000001
             bedae544  b6d7c0e8  /system/lib/libc++.so
             bedae548  b48fa048  [anon:libc_malloc]
             bedae54c  b6b02048  [anon:libc_malloc]
             bedae550  00000004
             bedae554  b6b40140  [anon:libc_malloc]
             bedae558  00000004
             bedae55c  00000001
             bedae560  00000003
             bedae564  b6b55300  [anon:libc_malloc]
             bedae568  b6b556f8  [anon:libc_malloc]
             bedae56c  b6d53333  /system/lib/libc.so (je_tcache_bin_flush_small+210)

    Tombstone written to: /data/tombstones/tombstone_09
