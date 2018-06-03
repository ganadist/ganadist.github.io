Title: python 용 gerrit rest api binding
Slug: 2018_05_20_pygerrit
Date: 2018-05-20 19:26
Category: tech
Tags: gerrit, python, rest, misc, opensource
Author: YOUNG HO CHA
Summary: gerrit rest api binding for python


회사에서 운영하던 고대의 [gerrit 서비스](https://www.gerritcodereview.com/)를 새로운 기계로 이전하기 위해, 2주동안 신나게(?) [ssh 스크립팅](https://gerrit-review.googlesource.com/Documentation/cmd-index.html)과 [importer plugin 을 이용](https://gerrit.googlesource.com/plugins/importer/+/stable-2.15/src/main/resources/Documentation/about.md)해 겨우겨우 완료했습니다.

결국 이전은 완료했건만, ssh 스크립팅은 확장성이 부족해서 재사용이 거의 불가능해 보이길래, 제대로된 gerrit api wrapper 를 찾아봤는데 그나마 멀쩡하게 생긴 넘이 sony 개발자가 만든 [pygerrit2 라는 물건](https://github.com/dpursehouse/pygerrit2)이 보이네요.

대략 코드를 살펴봤는데, 그렇게 길지는 않지만.. 그닥 python 개발자를 만족시키기에는 2% 부족해 보여서 결국 [야크털깍기 시작](https://www.lesstif.com/pages/viewpage.action?pageId=29590364)..(..)

해서 [결과물](https://github.com/ganadist/pygerrit)이 나왔습니다.

나름 대로의 바램을 [Feature에 정리](https://github.com/ganadist/pygerrit/blob/master/gerrit.py#L29)하긴 했는데 계속 유지할 수 있을지는 미지수..(..)
