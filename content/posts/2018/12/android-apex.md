Title: APEX, Android Package for OS
Slug: 2018_12_24_android_apex
Date: 2018-12-24 22:14
Category: tech
Tags: android, aosp
Summary: 모듈화된 안드로이드 OS로 가는 길, APEX

최근 AOSP에 [apex](https://android.googlesource.com/platform/system/apex/+/da6ab6e)하는 기능이 추가되었습니다. 안드로이드에서는 앱을 배포하기 위해 apk라는 패키징 형식을 이용하는데요, apex는 앱 대신 OS의 일부 기능을 업데이트 하기 위해 사용하는 패키지 형식으로 짐작됩니다.

현재 aosp의 master 버젼을 빌드하고 나면 다음과 같은 apex 파일들이 생성됩니다.


    $ ls $OUT/system/apex
    com.android.conscrypt.apex
    com.android.resolv.apex
    com.android.runtime.debug.apex
    com.android.tzdata.apex

    $ unzip -t $OUT/system/apex/com.android.runtime.debug.apex
    Archive:  out/target/product/generic_x86_64/system/apex/com.android.runtime.debug.apex
        testing: apex_manifest.json
        testing: apex_payload.img         OK
        testing: resources.arsc           OK
        testing: AndroidManifest.xml      OK
        testing: META-INF/CERT.SF         OK
        testing: META-INF/CERT.RSA        OK
        testing: META-INF/MANIFEST.MF     OK

언듯 보기에는 apk 파일의 내용물과 유사하지만, classes.dex 대신 apex_payload.img 라는 파일이 포함되어 있습니다. 
해당 파일은 ext2 형식의 파일시스템을 포함하는 이미지이며, 각 역할을 수행하는 실행파일, 공유라이브러리, 또는 OS에서 필요로 하는 리소스가 포함될 수 있습니다.

현재 aosp의 master에서 apex형식으로 분리될 수 있는 항목은 다음과 같습니다.

 * [com.android.runtime](https://android.googlesource.com/platform/art/+/d67db81/build/apex/Android.bp#102) : Android Runtime(ART)
 * [com.android.conscrypt](https://android.googlesource.com/platform/external/conscrypt/+/afe0939/apex/Android.bp#15) : Secure Layer for Java
 * [com.android.resolv](https://android.googlesource.com/platform/system/netd/+/4231c54/apex/Android.bp#16) : DNS Resolver
 * [com.android.tzdata](https://android.googlesource.com/platform/system/timezone/+/8481d19/apex/Android.bp#15) : Timezone resources for bionic/icu
 * [com.android.media](https://android.googlesource.com/platform/frameworks/av/+/69addc70/apex/Android.bp#15) : Media Codecs

따라서 기기 제조사에서 직접 Android OS의 업데이트를 진행하지 않더라도, 위 항목들은 꾸준히 업데이트가 될 수 있을 것으로 보입니다.
