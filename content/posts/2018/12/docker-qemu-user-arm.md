Title: Docker로 ndk 바이너리 실행해보기
Slug: 2018_12_29_docker_qemu_user_arm
Date: 2018-12-29 12:32
Category: tech
Tags: Android, Docker, NDK
Summary: headless android runtime with docker

옛날 옛적(..)에 [Scratchbox](http://www.scratchbox.org/)라고 하는 물건이 있었습니다. 크로스 컴파일을 편하게 하기위한 도구인데, 파일시스템을 격리시키는 [chroot](https://en.wikipedia.org/wiki/Chroot)와 가상화 소프트웨어인 [qemu](https://www.qemu.org)를 이용해서, PC에서 arm, mips, ppc등과 같은 이기종용 바이너리를 생성할 수 있습니다.

여기서 qemu를 이용하는 방법이 독특한데요, [하드웨어 가상화](https://qemu.weilnetz.de/doc/qemu-doc.html#QEMU-PC-System-emulator)가 아닌, [리눅스 커널 가상화(소프트웨어 가상화)](https://qemu.weilnetz.de/doc/qemu-doc.html#QEMU-User-space-emulator)을 이용합니다. 이렇게 되면 실행파일을 qemu가 해석해서, 일부 시스템콜을 에물레이션하게 됩니다. ([Wine](https://www.winehq.org), 또는 [WSL(Windows Subsystem for Linux)](https://docs.microsoft.com/en-us/windows/wsl/about) 등도 이와 유사하게 동작합니다.)

그리고 실행하는 방법을 단순화 하기 위해 Linux의 [binfmt_misc](https://en.wikipedia.org/wiki/Binfmt_misc)를 이용해서, 실행하려는 파일의 헤더를 확인해 적절한 에물레이터에게 실행파일을 해석하게 하도록 하면, 거의 native환경과 유사하게 실행환경을 구성할 수 있습니다.

그런데 scratchbox와 유사하지만 최근 트렌드에 알맞게 chroot 대신 [docker를 이용해 이기종용 바이너리를 실행하는 환경을 구성하려는 시도](https://ownyourbits.com/2018/06/27/running-and-building-arm-docker-containers-in-x86/)가 눈에 띄더군요. 해당 포스팅을 따라하면 쉽게 PC에서 arm용 데비안 환경을 구성할 수 있습니다.

이와 유사하게 android환경도 에물레이터 대신 docker를 이용해 구성할 수 없을까 싶어서 시도를 해보았습니다. docker 이미지는 Android SDK 에서 설치할 수 있는 에뮬레이터의 OS이미지를 이용하면 손쉽게 만들 수 있습니다.

    $ mkdir system
    $ sudo mount $ANDROID_HOME/system-images/android-19/default/armeabi-v7a/system.img system
    $ sudo tar cf - system | docker import - android-19-armeabi-v7a
    sha256:f7427ad5b84efaf1c862c69b66df55c3ad8b8bbb05660fece31bc29c8cbc4abe


그리고 qemu-user-static 바이너리와 binfmt_misc 설정을 완료하고 docker를 수행합니다. 데비안/우분투 사용자면, [qemu-user-static 패키지](https://packages.debian.org/sid/qemu-user-static)만 설치하면 됩니다. 하지만 저는 archlinux를 사용하고 있어서, docker에서 debian 환경을 수행한 후, 해당 패키지를 설치하고 바이너리를 /opt/qemu-user 로 복사한 후, binfmt_misc 설정만 [binfmt-qemu-static aur](https://aur.archlinux.org/packages/binfmt-qemu-static/)로 설치했습니다. 아직 docker이미지가 제대로 동작하는지 확인을 할 수가 없으니 busybox의 도움도 받아보겠습니다.

    $ docker run -it -v /bin/busybox:/bin/sh -v /opt/qemu-user/qemu-arm-static:/usr/bin/qemu-arm-static -v /tmp:/tmp --name kk --rm  android-19-armeabi-v7a /bin/sh
    
    # uname -a
    Linux fb479d7afe07 4.19.12-arch1-1-ARCH #1 SMP PREEMPT Fri Dec 21 13:56:54 UTC 2018 x86_64 GNU/Linux
    # /system/bin/ls
    FATAL: kernel did not supply AT_SECURE


첫번째 uname 실행은 pc용 busybox가 docker 내부에서 정상동작하는지 확인하기 위해서 실행해봤습니다. 그리고 android에 포함된 toolbox의 ls를 수행했는데 커널에서 특정기능이 지원하지 않는다는 오류메세지가 발생했습니다. 여기서 커널은 실제 리눅스 커널이 아니라 qemu-user가 에물레이션 하는 커널일껍니다. 일단 [해당 메세지를 어디서 출력하는지 알아보기 위해 검색](http://androidxref.com/4.4.4_r1/search?q=kernel+did+not+supply+AT_SECURE&project=bionic)을 해보니, 런타임 링커에서 특정한 커널기능을 확인하는 부분이 있습니다. 일단 해당 부분을 검사하지 않도록 수정한 후 android를 빌드해서 새로 docker 이미지를 만들었습니다.

    $ repo init -u https://android.googlesource.com/platform/manifest -b kitkat-dev 
    $ repo sync --no-tags -c -j8
    $ source ./build/envsetup.sh
    $ lunch aosp_arm-userdebug
    $ make -j8 systemtarball


수정한 OS이미지로 docker 이미지를 생성한 후 실행해보았습니다.

    $ docker import $OUT/system.tar.bz2 android-19-armeabi-v7a
    # /system/bin/ls
    Segmentation fault (core dumped)


세그폴트 메세지를 보고 잠시 당황했었습니다만, gdb를 이용해 어디서 발생했는지 확인해보았습니다.

    $ prebuilts/gcc/linux-x86/arm/arm-linux-androideabi-4.7/bin/arm-linux-androideabi-gdb $OUT/system/bin/ls /tmp/qemu_ls_20181229-022527_7.core 
    GNU gdb (GDB) 7.6

    (gdb) set sysroot out/target/product/generic/symbols
    (gdb) set solib-search-path out/target/product/generic/symbols/system/lib
    (gdb) bt
    #0  0xf676889e in find_property()
    at bionic/libc/bionic/system_properties.c:403


일반적인 안드로이드 환경과 다르게 system property 값을 관리하는 init 프로세스가 동작하고 있지 않아서 property관련 동작이 잘못수행되고 있었습니다. 일단은 해당 동작이 segfault만 발생하지 않도록 대충 수습한 후,  docker이미지를 다시 만들어서 /system/bin/ls 를 수행하니 파일 목록이 정상적으로 출력됩니다.

좀 더 제대로 확인해보기 위해 다음과 같이 ndk용 코드를 간단하게 작성해봤습니다.

  * jni/Application.mk

[gist:id=80acee57558d9c9503612078a3f656b2,file=Application.mk]

  * jni/Android.mk

[gist:id=80acee57558d9c9503612078a3f656b2,file=Android.mk]

  * jni/main.c

[gist:id=80acee57558d9c9503612078a3f656b2,file=main.c]

그리고 실행파일을 생성한 후 docker 내에서 실행해보았습니다.

    $ $ANDROID_HOME/ndk-bundle/ndk-build 
    [armeabi-v7a] Compile thumb  : uname <= main.c
    [armeabi-v7a] Executable     : uname
    [armeabi-v7a] Install        : uname => libs/armeabi-v7a/uname

    $ cp libs/armeabi-v7a/uname /tmp/

    $ file /tmp/uname
    /tmp/uname: ELF 32-bit LSB shared object, ARM, EABI5 version 1 (SYSV), dynamically linked, interpreter /system/bin/linker, BuildID[sha1]=6d04cf954964d58ce83ee7f5996a70dab7cca880, stripped

    $ docker run -it -v /bin/busybox:/bin/sh -v /opt/qemu-user/qemu-arm-static:/usr/bin/qemu-arm-static -v /tmp:/tmp --name kk --rm  android-19-armeabi-v7a /bin/sh

    # /tmp/uname
    sys:	 Linux
    rel:	 4.19.12-arch1-1-ARCH
    ver:	 #1 SMP PREEMPT Fri Dec 21 13:56:54 UTC 2018
    h/w:	 armv7l

이와 같이 arm용 android 실행파일에서 호출하는 [uname 시스템 콜](http://man7.org/linux/man-pages/man2/uname.2.html)이 docker에서 정상적으로 동작하는 것을 확인했습니다.

이 환경에서는 일반적인 android app을 수행할 수는 없지만, cpu 연산만 필요로 하는 일부 동작(openssl, ffmpeg)등의 검증은 실제 하드웨어나 에물레이터 필요없이, jenkins와 같은 headless 환경에서 가능할 수 있을 것 같습니다.

이제 회사사람들을 꼬시는 일만 남았...

덤:
[docker 이미지](https://gist.github.com/ganadist/72213f7c4cdf0f5efd99ec3d52287394)를 [docker hub 에 업로드](https://cloud.docker.com/repository/docker/ganadist/android-docker/general)해두었습니다. 사용해 보려면 다음과 같이 docker 명령을 실행하면 됩니다.

    $  docker run --privileged -it ganadist/android-docker:android-19-armeabi-v7a 

