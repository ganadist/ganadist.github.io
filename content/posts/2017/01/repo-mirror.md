Title: repo mirror 를 이용해 git 저장용량을 절약하기
Slug: 2017_01_24_repo_mirror
Date: 2017-01-24 19:00
Category: tech
Tags: android, gerrit, git, repo
Author: YOUNG HO CHA
Summary: repo init의 --reference 옵션 사용하기


회사에서 하는 작업의 특성상, 대 여섯이상의 안드로이드 버젼 소스를 동시에 다루는 때가 많다. 하지만 그때마다 안드로이드 버젼의 소스를 그때그때 구성하는 것은 무지막지한 자원 낭비다.

현재 안드로이드 소스에 등록(manifest.xml)된 git repo 개수는 529개, 소스 용량은 대략 6G 가량 된다. 이걸 필요할 때마다 [구글 서버](https://android.googlesource.com/)로 부터 소스를 전송받아 구성하는 것은 여러모로 불합리해보여서 로컬네트워크에 [미러서버를 구성](https://android.googlesource.com/mirror/manifest/)해보기도 했으나, 네트워크가 여전히 병목인 것은 변함이 없었다. 그래서 아예 PC에다가 mirror를 마련하고 사용하기도 했다.

하지만 PC에다가 mirror를 마련하니 소스를 구성하는데 필요한 시간은 조금 줄어들었지만, 미러주기 사이에 달라진 변경사항에 대해서는 바로바로 확인이 불가능한 단점이 발생하였다. 게다가 더 큰 문제는 소스와 더불어 git 저장소까지 복제가 되다보니 PC의 저장장소 부족현상에 허덕이게 되었다. 그렇게 고민이 깊어가던 중..(..)

어느날 repo 명령어 도움말을 보다가 repo init 명령에 [--reference 옵션](https://gerrit.googlesource.com/git-repo/+/8844338%5E%21/)이 추가된 것을 발견. 구현은 아주 간단하다.

 * repo init를 수행할 때 [.repo/manifests 의 git config에 repo.reference 값을 지정한 디렉토리로 설정](https://gerrit.googlesource.com/git-repo/+/v1.12.37/subcmds/init.py#209)

 * repo sync를 최초로 수행할 때, [각 repo project에 대한 저장소를 생성하면서 .git/object/info/alternatives 를 .repo/manifests 에 등록했던 repo.reference값으로 채움](https://gerrit.googlesource.com/git-repo/+/v1.12.37/project.py#2287)

git 문서를 확인해보니 .git/object/info/alternatives 파일을 이용하면, [git의 object를 복사하지 않고 지정된 디렉토리에서 찾는다](https://git-scm.com/docs/gitrepository-layout#gitrepository-layout-objects)고 한다.

이 방식으로 repo init 명령을 이용해 안드로이드 소스 작업환경을 구성하면, git object를 복사할 필요가 없어져서 환경구성에 필요한 디스크공간도 절약과 함께, 소요되는 시간도 짧아진다.

뱀발: --reference 옵션을 이용할 때 디렉토리 위치를 절대경로로 지정해야 했지만, [최근 수정에 의해 상대경로도 정상적으로 동작](https://gerrit-review.googlesource.com/#/c/95310/)하도록 변경되었다.
