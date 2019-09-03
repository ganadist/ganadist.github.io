Title: 사제 Android Platform SDK 배포시 주의할 점
Slug: 2013_01_07_platform_sdk_publish
Date: 2013-01-07 21:26
Category: tech
Tags:  android, platform, sdk
Summary: android addon sdk 배포시 주의해야 할 사항들

요새 android sdk 및 addon과 관련해서 약간 작업을 하면서 느낀 애로사항을 정리해봤습니다.

1. sdk용 addon을 배포하기 위해서는 [xsd 파일](http://goo.gl/UUh8a)에 정의된 대로 xml을 만들어야 합니다.

1. ics(sdk tools v20)까지 쓰이던 skin이 v21부터 쓰이지 않습니다. 그 대신에 Device Profile이라는 것으로 대체된 것 같습니다. Device Profile은 sdk addon 대신 extra 로 추가될 수 있습니다. (설치 위치가 $SDKROOT/extras/$VENDOR_ID/DeviceProfiles/devices.xml 이면 avd manager에서 인식됩니다.)

1. addon 에 추가되는 문서는 add-ons/addon-blahblah/docs/$DOC_MODULE 로 설치되는데, 실제로 eclipse에서는 add-ons/addon-blahblah/reference 에 설치되어야 IDE와 연동됩니다.

1. 이건 [java vm의 버그](http://bugs.sun.com/view_bug.do?bug_id=4787931)인데, java vm에서 사용자 홈 디렉토리를 찾는 부분이 Windows에서는 조금 이상하게 되어 있습니다.
사용자의 바탕화면 폴더를 찾은 다음, 그 윗 폴더를 사용자의 홈 디렉토리(user.home property)로 설정하는데요. 일반적으로는 %USERPROFILE%이라는 환경변수를 사용자 홈 디렉토리로 인지해야 합니다.
그런데 registry등으로 바탕화면 폴더의 위치를 변경 해버리면, Sdk Manager(java app)와 Android Emulator(windows native program)가 찾아보는 HOME디렉토리가 달라지기 때문에 제대로 동작하지 않을 수 있습니다. 간단한 workaround로는 ANDROID_SDK_HOME 이라는 환경변수를 추가적으로 설정해 놓으면, Sdk Manager와 Android Emulator가 엉뚱한 파일을 참조하는 것을 해결할 수 있습니다.
