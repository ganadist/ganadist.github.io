Title: 안드로이드 앱의 서명키 교체하기  
Slug: 2022_05_12_key_rotation  
Date: 2022-05-12 20:54  
Category: tech  
Tags: GooglePlay, Android, Security  
Summary: 안드로이드 앱의 서명키 교체하기  

어제 Google I/O의 세션중 Google Play Console에 새로 추가될 기능 중 [서명키를 교체(Key Rotation)하는 것](https://youtu.be/d8mn0pmgvGw?t=328)이 곧 들어갈 것이라고 합니다.
해당 기능은 예전에 Google이 [별도의 블로깅 포스트](https://android-developers.googleblog.com/2021/06/the-future-of-android-app-bundles-is.html)에서 곧(?) 추가할 것이라고 한지 거의 1년만에 들어가게 됩니다.

Google이 Google Play Store(예전의 Android Market)을 운영한지 13년이 넘어가고 있는데요, 그 사이에 서명키를 안전하게 보관하고 있다면 다행이겠지만, 여러가지 이유로 서명키가 외부에 유출이 되었을 수 있습니다.

또한 서명키를 생성할 때, 현대 컴퓨팅환경에 알맞지 않은 취약한 알고리즘을 이용해 서명키를 작성할 수 있습니다.

서명키가 유출되거나 취약한 알고리즘을 이용한 서명키를 사용하는 경우, 악의적인 의도로 서명된 앱을 변조해서, 앱 사용자의 정보를 취득할 수 있는 위험이 있게 됩니다.
이러한 경우에는 꼭 서명키를 교체해서, 앱의 보안을 강화해야 합니다.

기존에는 이러한 경우 (눈물을 머금고) 서명키를 직접 교체해야 했지만, 앱의 업그레이드가 불가능 하기 때문에, 사용자들에게 수동으로 앱을 제거후 다시 설치해 달라고 부탁해야 했습니다. 혹은 Application ID를 새로 구성해서, 사용자를 처음부터 모으는 고행의 길을 선택해야 했습니다.
하지만 이번에 추가되는 서명키 교체(Key Rotation)은 그러한 불편한 없이, 자연스럽게 서명키를 교체하는 것이 가능합니다.

이 포스트에서는 Google Play Console 대신, 직접 서명키를 바꾸는 방법과 그 영향에 대해서 이야기 해보겠습니다.

원래 Android앱의 서명키는 Java에서 사용하던 서명 방식을 그대로 이용한 app signing scheme v1 에서 시작해서, 현재 app signing scheme v4 까지 발표되었는데요, [서명키를 교체하는 기능](https://developer.android.com/about/versions/pie/android-9.0#apk-key-rotation)은 app signing scheme v3 에서 지원됩니다.
즉 app signing scheme v3가 지원되는 API Level 28 (Android 9) 이상의 OS가 설치된 기기에서 지원됩니다.

서명 키 교체는 실질적으로 앱안에 예전의 서명키와 교체할 서명키가 같이 포함되고, 해당키 모두를 이용해 각각 서명됩니다.
그리고 app signing scheme v3 가 지원되지 않는 예전 OS에서는 이전 서명키로 인식하고, Android 9 이상의 OS가 설치된 기기에서는 새로 추가한 서명키가 인식됩니다.

따라서 서명키의 fingerprint를 이용해 동작하는 API가 있다면, 기존의 서명키 fingerprint와 함께, 새로운 서명키의 fingerprint도 같이 등록해야 합니다.

일반적으로 서명키는 [Android Gradle Plugin에서 제공하는 DSL](https://developer.android.com/studio/publish/app-signing#secure-shared-keystore)을 이용해, 특정한 시스템에서만 실제 서명키를 이용하고, 개발환경에서는 별도의 개발용 서명키를 사용하는 것이 안전합니다.

하지만, 서명키 교체 기능은 현재 (Android Gradle Plugin 7.4 alpha01) version에서 지원이 되지 않고 있으며, 따라서 명령행에서 수동으로 수행해야 합니다.

혹시 Android Gradle Plugin을 통해 키교체 기능을  자동화 하고 싶은 분이 있다면, [Google의 이슈트래커에 등록된 이슈](https://issuetracker.google.com/issues/160230884)를 **참고하(고 별표를 열심히 눌러주)시기 바랍니다**.  
(이 포스팅을 작성하는 이유입니다.)


## 준비물  

* Android SDK 와 build tools 30.0.0 또는 상위 버젼 설치
* 기존에 사용하던 인증서 파일(ex: old_release.keystore) 및 인증정보 
* 새로 사용할 인증서 파일(ex: new_release.keystore) 및 인증정보
* 앱 바이너리(apk) 파일

## 서명 과정 및 확인 방법

### lineage 정보 생성
먼저 android build tools 에 포함된 `apksigner` 명령을 이용해 lineage (게임이 아닙니다) 정보를 생성합니다. 

```bash
apksigner rotate \
  --out lineage.dat \
  --old-signer --ks old_release.keystore --ks-key-alias "XXX" --ks-pass "pass:XXXX" \
  --set-installed-data true \
  --set-permission true \
  --set-rollback false \
  --new-signer --ks new_release.keystore --ks-key-alias "XXX" --ks-pass "pass:XXXX"    
```

해당 명령을 실행할 때,  새로 서명된 앱으로 업그레이드 되면서 기존에 설치되었던 앱의 일부 특성에 대해 지정할 수 있습니다.  

   * --set-install-data : 기존에 사용하고 있던 앱 데이터를 그대로 유지할지 결정
   * --set-permission : 기존에 사용하고 있던 서명키 기반의 퍼미션을 유지할 지 결정
   * --set-rollback : 새로 서명한 키에서 원래서명키만 남긴 앱을 설치할 때, 서명키를 원복할지 결정

이 외에도 buildtool 버젼에 따라 apksigner에서 지정할 수 있는 옵션이 달라질 수 있습니다. 자세한 설명은 아래의 명령을 이용해 확인할 수 있습니다.  

```bash
apksigner rotate --help
  USAGE: apksigner rotate [options]

  This takes the provided keys and creates a SigningCertificateLineage entry linking the old to the
  new, for use in a key rotation scenario using APK Signature Scheme v3.
  ...
```

### lineage 정보를 기반으로 2개의 서명키로 앱 서명

위에서 생성한 lineage 정보와 기존의 서명키, 그리고 신규 서명키를 이용해 앱 서명을 진행합니다.

```bash
apksigner sign \
  --ks old_release.keystore --ks-key-alias "XXX" --ks-pass "pass:XXXX" \
  --next-signer \
  --ks new_release.keystore --ks-key-alias "XXX" --ks-pass "pass:XXXX" \
  --lineage lineage.dat \
  --v3-signing-enabled true \
  app-release.apk
```

간단하다면 간단하지만, 의외로 귀찮은 작업입니다. 따라서, 위에서 언급한 구글 이슈트래커를 참고해서, 별표와 답장을 보내서, 기본 빌드 스크립트만을 이용해 손쉽게 해당 정보가 적용될 수 있도록 Google 개발자분들에게 용기(?)를 주도록 해주세요.

### 서명키 확인 방법

생성된 apk 는 다음과 같이 확인할 수 있습니다.

  * 예전 OS를 위한 signing scheme v1/v2 확인

```bash
jarsigner -verify -certs --verbose app-release.apk
...
- Signed by "CN=OLD Key, OU=My Team, O=My Company, L=My Location, ST=Seoul, C=KR"
 Digest algorithm: SHA-256
 Signature algorithm: SHA256withRSA, 1024-bit key (weak)
```

  *  Android OS 8.1 이하 버젼에 설치시 아래와 같이 서명정보를 확인 가능

```bash
adb shell dumpsys package com.example.myapplication | grep signatures             
    signatures=PackageSignatures{7d9facf [e76b236f]}
```

  * 신규 서명키 signing scheme v3 확인

```bash
apksigner verify -print-certs app-release.apk
   Signer #1 certificate DN: CN=NEW Key, OU=New Team, O=My Company, L=My Location, ST=Pangyo, C=KR
   Signer #1 certificate SHA-256 digest: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   Signer #1 certificate SHA-1 digest: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   Signer #1 certificate MD5 digest: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

  *  Android OS 9 이상 버젼의 기기에 설치시 아래와 같이 서명정보를 확인 가능

```bash
adb shell dumpsys package com.example.myapplication | grep signatures
  signatures=PackageSignatures{2fa497a version:3, signatures:[804a2fa7], past signatures:[e76b236f flags: 17, 804a2fa7 flags: 17]}
```

## 참고자료
* https://developer.android.com/about/versions/pie/android-9.0#apk-key-rotation
* https://source.android.com/security/apksigning/v3?hl=en
* https://android-developers.googleblog.com/2021/06/the-future-of-android-app-bundles-is.html
* https://youtu.be/d8mn0pmgvGw
* https://issuetracker.google.com/issues/160230884