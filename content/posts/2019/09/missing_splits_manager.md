Title: Split Apks의 Sideload 검사
Slug: 2019_09_03_missing_splits_manager
Date: 2019-09-03 22:35
Category: tech
Tags: Google Play, appbundle, Split Apks
Summary: Google Play Core의 Sideload 검사 알아보기

최근 Google Play에서 [App Bundle](https://developer.android.com/guide/app-bundle)을 사용하는 앱이 점점 늘어나고 있습니다. AppBundle을 사용하면 최종 사용자는 단말기기에 최적화 된 어플리케이션(Split Apks 형식)을 작은 용량으로 받을 수 있는 장점이 있습니다.
Split Apks 형식은 Android 5.0(Lollipop)부터 지원되는 형식이며, [bundletool](https://developer.android.com/studio/command-line/bundletool)을 이용해서 Google Play를 통하지 않고 AppBundle 파일을 이용해 만들 수 있습니다. 당연히 osx에서는 [brew 를 이용해 설치](https://formulae.brew.sh/formula/bundletool)가 가능하며, archlinux에서는 [aur 에서 패키지를 제공](https://aur.archlinux.org/packages/bundletool/)합니다.

```
$ brew install bundletool
$ ./gradlew bundleDebug
$ bundletool build-apks --ks=release.keystore --ks-pass=keystore_password --ks-key-alias=alias --key-pass=password --connected-device --bundle=app/build/outputs/bundle/debug/app-debug.aab --output=my_app.apks
$ unzip -t my_app.apks 
Archive:  my_app.apks
    testing: splits/base-xhdpi.apk    OK
    testing: splits/base-x86.apk      OK
    testing: splits/base-master.apk   OK
    testing: toc.pb                   OK
No errors detected in compressed data of my_app.apks.

```

그런데 Google Play Store이외의 앱 유통 채널(일반적으로 3rd party market이라고 부릅니다)에서는 이러한 장점을 취할 수가 없게 되는데요, 예전과 동일한 방식으로 단말기기에 받은 apk파일을 그대로 3rd party market에 배포하게 되면, 내려받은 단말과 다른 구성을 가진 기기에서는 오동작할 수 있게 됩니다.
여기서 다른 구성이란 ABI(Application Binary Interface) 또는 DPI의 경우 기기마다 달라질 수 있으며, 정상적인 구성을 포함하지 않을 경우, 적절한 native method나 drawable/layout resource를 가져올 수 없어서, 앱이 비정상종료가 될 수 있습니다.

이러한 오류를 방지하기 위해, Google에서는 앱이 구동할 때 [Sideload Check](https://developer.android.com/guide/app-bundle/sideload-check)라는 절차를 추가해서, 잘못된 형식의 앱이 설치(이러한 상황을 Sideload라고 부릅니다)가 되면, 사용자에게 앱을 재설치하도록 유도하게 됩니다.

Sideload check의 주요 기능은 [Google Play Core API](https://developer.android.com/reference/com/google/android/play/core/packages)에서 제공되는데, 해당 API에서 제공되는 MissingSplitManager class에는 다음 2가지의 public method가 존재하며, 각각의 method에서는 다음과 같은 동작을 수행한다고 합니다.

* [MissingSplitsManager.isMissingRequiredSplits()](https://developer.android.com/reference/com/google/android/play/core/missingsplits/MissingSplitsManager.html#isMissingRequiredSplits())
    * 설치된 앱이 Split Apks 형식으로 설치되었는지 확인
        * Google Play나 bundletool에서 Split Apks형식으로 앱을 생성하면 AndroidManifest.xml 에 `com.android.vending.splits.required` 라고하는 metadata가 임의로 추가됩니다. 따라서 해당 metadata의 존재 유무로 Split Apks형식인지 알 수 있습니다.
    * Split Apks 형식이 아니면 standalone apk형식이기 때문에 정상설치로 취급
    * Split Apks 형식인데, base apk 이외에 [추가적인 apk](https://developer.android.com/reference/kotlin/android/content/pm/PackageInfo?hl=en#splitNames:kotlin.Array)가 포함되지 않은 경우, 이상설치로 취급

* [MissingSplitsManager.disableAppIfMissingRequiredSplits()](https://developer.android.com/reference/com/google/android/play/core/missingsplits/MissingSplitsManager.html#disableAppIfMissingRequiredSplits())

    * isMissingRequiredSplits()를 수행해 구성에 문제가 발견되었을 때
        * Activity가 아닌 모든 Android Components(Service, Broadcast Receiver, Provider)에 대해 동작하지 않도록 [Component State](https://developer.android.com/reference/kotlin/android/content/pm/PackageManager?hl=en#setComponentEnabledSetting(android.content.ComponentName,%20kotlin.Int,%20kotlin.Int))를 [disable](https://developer.android.com/reference/kotlin/android/content/pm/PackageManager?hl=en#COMPONENT_ENABLED_STATE_DISABLED:kotlin.Int)로 설정
            * 해당 동작은 사용자의 의도와는 무관하게, Push나 다른앱의 연동등에 의해 앱이 구동되지 않게 하기위해 취하는 조치입니다.
        * Play Service에서 사용자가 앱을 재설치 할 수 있도록 유도하는 dialog를 띄우도록 함.
            * 현재 앱은 다음 단계에서 종료할 것이고, drawable/layout resource가 포함되지 않을 수 있으므로, UI를 띄울 수 없는 상태입니다.
        * Activity가 동작하지 않게 [tasks를 모두 종료](https://developer.android.com/reference/android/app/ActivityManager.AppTask.html#finishAndRemoveTask()) 후 [process 종료](https://developer.android.com/reference/kotlin/java/lang/System?hl=en#exit(kotlin.Int))
    * Split Apks 구성에 문제가 없거나, Split Apks형식이 아닐 때
        * Activity가 아닌 모든 Android Components가 disable 되어 있으면, 이전 Sideload check에서 disable한 것이기 때문에, [원래 상태로 원복](https://developer.android.com/reference/kotlin/android/content/pm/PackageManager?hl=en#COMPONENT_ENABLED_STATE_DEFAULT:kotlin.Int)시킴
        * Application 수행을 계속 진행할 수 있도록 함.


하지만 Sideload check를 추가한 이후에 임의로 몇가지 오류상태를 만들어봤는데, `isMissingRequiredSplits()`가 의도한대로 동작하지 않는 것을 발견했습니다.
API및 DPI에 대해 Split Apks를 생성한 후, base module및 DPI module만 설치 한 경우에도 `isMissingRequiredSplits()`에서 누락된 ABI module을 감지하지 못하고, 정상 설치된 경우로 판단하고 있었습니다. 위에서 설명한 것과 같이 PackageInfo.splitNames에서 항목이 1개라도 있으면 정상설치로 취급하게 됩니다.

따라서 Google Play Core 에서 제공하는 MissingSplitsManager API는 일부 상황에 대해서 오동작할 수 있게됩니다. 개인적으로 이러한 상황이 닥쳤을 때는 Google Play Core API 대신 다음과 같이 동작을 수행하면, 사용자에게 조금이라도 나은 사용자 경험을 줄 수 있을 것 같습니다.

* AndroidManifest.xml에서 `com.android.vending.splits.required` 메타데이터 확인 및 [앱의 설치 경로](https://developer.android.com/reference/kotlin/android/content/pm/PackageManager?hl=en#getInstallerPackageName(kotlin.String))가 [Google Play Store](https://developers.google.com/android/reference/com/google/android/gms/common/GooglePlayServicesUtil.html#GOOGLE_PLAY_STORE_PACKAGE)인지 확인 
    * 되도록이면 Google Play Store의 signature가 google에서 배포한 것이지 확인
* 앱 구성이 잘못되면, notification을 이용해 앱설치가 잘못되었다는 것을 알려주고, click 시 앱을 재설치할 수 있도록 [Google Play의 intent를 등록](https://developer.android.com/distribute/marketing-tools/linking-to-google-play#android-app)

함께보기 : [MissingSplitsManager class를 Android Studio에서 disassemble한 코드 조각](https://gist.github.com/ganadist/af8541d36aaf36c5e94f6a7596ea02eb)