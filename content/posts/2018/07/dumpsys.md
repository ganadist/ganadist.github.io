Title: android 의 dumpsys를 이용한 분석 방법
Slug: 2018_07_10_dumpsys
Date: 2018-07-10 21:16
Category: tech
Tags: android
Summary: android dumpsys 사용하기

얼마 전에 [과일님](http://pluu.github.io/)이 [쌩고생하며 디버깅했던 경험을 공유](https://yanolja.github.io/2018/07/Android-Why)해주었는데, 약간 더 곁들여서 끄적여봅니다.

# dumpsys

[dumpsys 명령어](https://developer.android.com/studio/command-line/dumpsys)는 IBinder의 [dump 메소드](http://bit.ly/2u8AZIY)의 결과를 표준 출력으로 출력해주는 유용한 개발도구입니다. adb만 사용 가능한 상태면 손쉽게 기기의 상태를 확인해볼 수 있고, PC가 없더라도 [개발자 옵션에 포함되어 있는 버그 신고](https://developer.android.com/studio/debug/bug-report#bugreportdevice) 기능을 이용해서 출력을 뽑아낼 수 있습니다. 그런데 아무 IBinder 객체에게 사용할 수 있는 것은 아니고, [system service manager](https://android.googlesource.com/platform/frameworks/native/+/master/cmds/servicemanager/)에 등록된 항목에 한해서 가능합니다. system service manager에 등록된 IBinder객체는 다음의 명령을 이용해 확인가능합니다.


    ## android 4.3 이전
    $ adb shell service list

    ## android 4.4 이후
    $ adb shell dumpsys -l


출력물은 각 시스템 서비스의 dump 메소드의 구현을 확인하면 정확하게 어떤 값을 출력하는 지 알 수 있습니다. 예를 들면 다음과 같습니다.

 * [ActivityManagerService](https://android.googlesource.com/platform/frameworks/base/+/079f03f/services/core/java/com/android/server/am/ActivityManagerService.java#15068)
 * [MediaPlayserService](https://android.googlesource.com/platform/frameworks/av/+/1ec73be/media/libmediaplayerservice/MediaPlayerService.cpp#433)


# dumpsys activity service

그리고 [앱에서 작성하는 Service 클래스](https://developer.android.com/reference/android/app/Service)에도 시스템 서비스와 유사하게 [dump 메소드 인터페이스가 제공](http://bit.ly/2L3Ty7D)됩니다. 위에 이야기했듯이 dumpsys는 system service manager에 등록된 IBinder 객체에만 접근할 수 있기 때문에, 앱에서 작성한 서비스에서 정보를 얻기 위해서는 ActivityManagerService를 경유해야 합니다.

Android에서 ActivityManagerService는 앱에 포함된 activity, service, broadcast receiver, provider등을 관리해주며, 각 컴포넌트의 상태를 확인할 수 있는데요. dumpsys 명령을 이용하면 정말 상세하게 알 수 있습니다.


    $ adb shell dumpsys activity -h

    Activity manager dump options:
      [-a] [-c] [-p PACKAGE] [-h] [WHAT] ...
      WHAT may be one of:
        a[ctivities]: activity stack state
        r[recents]: recent activities state
        b[roadcasts] [PACKAGE_NAME] [history [-s]]: broadcast state
        broadcast-stats [PACKAGE_NAME]: aggregated broadcast statistics
        i[ntents] [PACKAGE_NAME]: pending intent state
        p[rocesses] [PACKAGE_NAME]: process state
        o[om]: out of memory management
        perm[issions]: URI permission grant state
        prov[iders] [COMP_SPEC ...]: content provider state
        provider [COMP_SPEC]: provider client-side state
        s[ervices] [COMP_SPEC ...]: service state
        as[sociations]: tracked app associations
        settings: currently applied config settings
        service [COMP_SPEC]: service client-side state
        package [PACKAGE_NAME]: all state related to given package
        all: dump all activities
        top: dump the top activity
      WHAT may also be a COMP_SPEC to dump activities.
      COMP_SPEC may be a component name (com.foo/.myApp),
        a partial substring in a component name, a
        hex object identifier.
      -a: include all available server state.
      -c: include client state.
      -p: limit output to given package.
      --checkin: output checkin format, resetting data.
      --C: output checkin format, not resetting data.
      --proto: output dump in protocol buffer format.

여기서 특정 앱의 service에 포함된 dump 메소드([SystemUI](https://android.googlesource.com/platform/frameworks/base/+/079f03f/packages/SystemUI/src/com/android/systemui/SystemUIService.java#47) 또는 [TelephonyService](https://android.googlesource.com/platform/packages/services/Telephony/+/67a453d/src/com/android/phone/TelephonyDebugService.java#51))의 출력 결과를 알고 싶다면 다음과 같이 명령을 실행하면 됩니다.

    $ adb shell dumpsys activity service com.android.systemui/.SystemUIService

    $ adb shell dumpsys activity service com.android.phone/.TelephonyDebugService


만약에 여러분이 작성한 앱의 서비스에서 다양한 디버깅 정보를 출력하고 싶다면, dump메소드를 채우면 됩니다.


# dumpsys activity broadcasts

 intent broadcast 타이밍 때문에 고통받는 개발자들도 dumpsys를 이용하면 큰 도움이 됩니다.

다음의 명령을 이용하면 intent broadcast가 발생했던 시간, intent 내용 및 처리 시간과 receiver 등을 쉽게 확인해볼 수 있습니다.


    $ adb shell dumpsys activity broadcasts history
