Title: TCP access control in Android Frameworks
Slug: 2017_08_16_tcp_on_android
Date: 2017-08-16 19:00
Category: tech
Tags: android, network
Author: YOUNG HO CHA
Summary: Android Framework에서 소켓권한 제어 방법


2년 전에 완전정복 했었다고 믿었건만, 지나가면 새까맣게 잊어먹는 습성때문에 기록으로 남깁니다.

# Android 1.0 ~ Android 4.4

TCP 소켓을 생성할 때는 리눅스 커널의 [socket 이라는 시스템콜](http://man7.org/linux/man-pages/man2/socket.2.html)을 이용해 생성하게 되어 있는데,  android의 리눅스 커널에는 특정 그룹(AID_INET, AID_NET_RAW)이나 특정 capability(CAP_NET_RAW)를 가지고 있는 process에 대해서만 socket 시스템 콜을 호출할 수 있는 [변경사항을 포함](https://android.googlesource.com/kernel/common/+/fd64bbf28e28526f608df0061175829338ee94cc%5E%21/)하고 있습니다.

그리고 앱에 [INTERNET 이라는 퍼미션](https://developer.android.com/reference/android/Manifest.permission.html#INTERNET)을 포함하고 있으면, 해당 [앱의 group에 inet 을 포함](https://android.googlesource.com/platform/frameworks/base/+/lollipop-mr1-release/data/etc/platform.xml#53)시켜줍니다.

따라서 해당 퍼미션을 가지고 있지 않은 daemon이나 앱에서는 socket을 생성할 때 EACCESS(퍼미션 없음) 오류를 발생하게 됩니다.

# Android 5.0 ~

새로운 [connectivity api](https://developer.android.com/about/versions/android-5.0.html#Multinetwork) 로 인해 socket 퍼미션을 동적으로 관리하기 위해서 [netd 라는 daemon이 완전히 개비](https://android.googlesource.com/platform/system/netd/+/android-7.1.1_r50)되었습니다. ([킷캣 이전에도 netd는 존재](https://android.googlesource.com/platform/system/netd/+/kitkat-dev)했지만 테터링이나 vpn등의 제한된 기능만 제공했습니다.)

c 라이브러리(bionic)의 socket 관련 시스템 콜([socket](https://android.googlesource.com/platform/bionic/+/android-7.1.1_r50/libc/bionic/socket.cpp), [accept4](https://android.googlesource.com/platform/bionic/+/android-7.1.1_r50/libc/bionic/accept4.cpp), [connect](https://android.googlesource.com/platform/bionic/+/android-7.1.1_r50/libc/bionic/connect.cpp)) 래퍼는 직접 커널에서 제공되는 시스템콜을 호출하지 않고, [netd 에서 제공되는 래퍼 함수를 호출](https://android.googlesource.com/platform/bionic/+/android-7.1.1_r50/libc/bionic/NetdClient.cpp)합니다.

그리고 각 socket관련 시스템 콜을 호출할 때는 [각 socket에 대해 fwmark(Firewall Mark)라는 것을 설정](https://android.googlesource.com/platform/system/netd/+/android-7.1.1_r50/server/FwmarkServer.cpp#207)하고, 라우팅 테이블에서 fwmark를 이용해 해당 패킷을 실제로 교환할 지 결정합니다.

    mako:/ # ip rule
    0:      from all lookup local
    10000:  from all fwmark 0xc0000/0xd0000 lookup legacy_system
    10500:  from all oif dummy0 uidrange 0-0 lookup dummy0
    10500:  from all oif wlan0 uidrange 0-0 lookup wlan0
    13000:  from all fwmark 0x10063/0x1ffff lookup local_network
    13000:  from all fwmark 0x10064/0x1ffff lookup wlan0
    14000:  from all oif dummy0 lookup dummy0
    14000:  from all oif wlan0 lookup wlan0
    15000:  from all fwmark 0x0/0x10000 lookup legacy_system
    16000:  from all fwmark 0x0/0x10000 lookup legacy_network
    17000:  from all fwmark 0x0/0x10000 lookup local_network
    19000:  from all fwmark 0x64/0x1ffff lookup wlan0
    22000:  from all fwmark 0x0/0xffff lookup wlan0
    23000:  from all fwmark 0x0/0xffff uidrange 0-0 lookup main
    32000:  from all unreachable

따라서 퍼미션을 가지지 않는 데몬이나 앱이 tcp연결을 시도하면, 킷캣 미만처럼 EACCESS오류가 발생하는 것이 아니라,  송신용 소켓일 경우에는  ENETUNREACH(Network is unreachable)이 발생하며, 수신용 소켓일 경우에는 라우팅이 되지 않아 아예 패킷 수신이 되지 않습니다.

또한 네트워크 인터페이스가 netd 및 connectivity service에 등록되지 않은 상태이면, 마찬가지로 라우팅 테이블에서 해당 패킷을 처리하지 않게 되므로, 패킷 송수신이 불가능한 상태가 됩니다.

임의로 네트워크 인터페이스를 netd에 등록하려면 다음 명령을 미리 실행해 놓습니다.

    mako:/ # ndc network create 100
    mako:/ # ndc network default set 100
    mako:/ # ndc network interface add 100 eth0
    mako:/ # dumpsys netd

      NetworkController
        Default network: 100

        Networks:
          51 DUMMY dummy0
            No DNS servers defined
            No search domains defined

          99 LOCAL
            No DNS servers defined
            No search domains defined

          100 PHYSICAL eth0,wlan0
            Required permission: NONE
            DNS servers: # IP (total, successes, errors, timeouts, internal errors, RTT avg, last sample)
              168.126.63.1 (38, 38, 0, 0, 0, 47ms, 562s)
              168.126.63.2 <no data>
            No search domains defined
            DNS parameters: sample validity = 1800s, success threshold = 25%, samples (min, max) = (8, 64)
