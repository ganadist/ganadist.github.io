Title: gerrit의 database를 h2에서 pgsql로 변환하기
Slug: 2018_06_10_gerrit_h2_pgsql_convert
Date: 2018-06-10 22:56
Category: tech
Tags: gerrit, database
Author: YOUNG HO CHA
Summary: gerrit database를 h2에서 pgsql로 바꾸기

1달 전에 설치했던 회사 [gerrit](https://www.gerritcodereview.com/)서비스의 성능을 튜닝해보던 중, 별도로 database 설치 및 설정이 귀찮아서 gerrit에서 내장으로 제공되는 [h2 database](http://www.h2database.com/)를 선택하던게 문제가 있지 않나 싶은 의심이 들어서, gerrit 관리자들 사이에서 널리 사용되는 [postgresql](https://www.postgresql.org/)로 변환해보기로 했습니다.

database는 전혀 문외한이라 어떻게 해볼까 고민이었는데, 선지자들의 발자취를 검색해보던 중 [google groups](https://groups.google.com/forum/#!msg/repo-discuss/waUyfJ6pbf0/wQnpu9EIAgAJ)에 다행히 성공담이 남아있길래, 그들의 작업 로그를 기반으로 진행해보았습니다. google groups에 논의된 백업 방법은 gerrit 2.7 및 2.12 버젼 기반이고, 제 경우에는 현재 제일 최근 버젼인 2.15를 기반으로 진행하였습니다.

**주의**: 잘못 건드렸다간 데이터를 날려먹을 수 있기 때문에 꼭 이전 데이터를 백업해두시기 바랍니다. 저는 tar로 묶어서 안전하게 보관한 후 진행을 시작했습니다.

## h2 database를 csv로 export

먼저 h2 database에서 내장 함수를 이용해 csv로 export를 하였습니다. google groups의 예제에서는 한땀한땀 h2의 내장 함수를 실행시켜주었지만, python 스크립트를 이용해 일괄적으로 csv 파일로 변환했습니다. (gerrit 버젼에 따라서 table 및 column 이름이 바뀔 수 있습니다.)

[gist:id=0c2780a1f3a624041665e971c5ea632f,file=gerrit_h2_to_csv.py]

스크립트 수행 결과 말미의 sequence는 따로 보관하기가 귀찮아서, 수동으로 import 스크립트에 박아서 처리했습니다.

## All-Projcts 및 All-Users repository 백업

일단 csv로 export가 완료되면, gerrit 에서 자동으로 생성되었던 **All-Projects.git** 및 **All-Users.git** repository 를 별도로 백업해두어야 합니다. 해당 repository에는 전체 프로젝트 및 사용자의 권한 정보가 보관되고, 이후에 db를 생성하기 위해 gerrit을 재초기화 할 때 같이 초기화가 되기 때문에, 꼭 백업을 해두었다가 다시 활용해야 합니다.

## 이전할 database로 gerrit 재 초기화

배포판에서 제공하는 pgsql을 설치한 후, [database의 user 및 table을 구성](https://gerrit-review.googlesource.com/Documentation/install.html#createdb_postgres)하고 [gerrit 설정](https://gerrit-review.googlesource.com/Documentation/config-gerrit.html#database)에서 pgsql을 사용하도록 구성한 다음 재 초기화를 진행합니다.

    $ java -jar bin/gerrit.war init --batch -d .

## All-Projects 및 All-Users repository 복구

앞에서 백업해두었던 두 개의 repository를 다시 원래 위치에 복사해서 복구합니다.

## csv를 pgsql로 import

h2를 export할 때와 유사하게 python 스크립트로 구성해서 pgsql에 csv를 퍼부었습니다.

일부 sequence (change_id, account_id, account_group_id)는 h2스크립트에서 출력했던 결과를 수동으로 기입했습니다.

[gist:id=0c2780a1f3a624041665e971c5ea632f,file=gerrit_csv_to_pgsql.py]

gerrit 2.15에서 새로 추가된 [notedb backend](https://gerrit-review.googlesource.com/Documentation/note-db.html)를 이용하고 있다면 일부 account 관련 database를 import 못한다고 오류가 발생할 수 있는데, 해당 database의 값은 앞에서 복사한 All-Users repository에 포함되어 있기 때문에 무시하면 됩니다.

import가 완료되면 gerrit 내장 sql 커맨드 인터페이스에서 테이블들이 제대로 옮겨졌는지 확인해보면 됩니다.

    $ java -jar bin/gerrit.war gsql -d .
    gerrit> \d
                List of relations
    TABLE_SCHEM | TABLE_NAME                  | TABLE_TYPE
    ------------+-----------------------------+-----------
    PUBLIC      | ACCOUNTS                    | TABLE
    PUBLIC      | ACCOUNT_EXTERNAL_IDS        | TABLE
    PUBLIC      | ACCOUNT_GROUPS              | TABLE
    PUBLIC      | ACCOUNT_GROUP_BY_ID         | TABLE
    PUBLIC      | ACCOUNT_GROUP_BY_ID_AUD     | TABLE
    PUBLIC      | ACCOUNT_GROUP_MEMBERS       | TABLE
    PUBLIC      | ACCOUNT_GROUP_MEMBERS_AUDIT | TABLE
    PUBLIC      | ACCOUNT_GROUP_NAMES         | TABLE
    PUBLIC      | CHANGES                     | TABLE
    PUBLIC      | CHANGE_MESSAGES             | TABLE
    PUBLIC      | PATCH_COMMENTS              | TABLE
    PUBLIC      | PATCH_SETS                  | TABLE
    PUBLIC      | PATCH_SET_APPROVALS         | TABLE
    PUBLIC      | SCHEMA_VERSION              | TABLE
    PUBLIC      | SYSTEM_CONFIG               | TABLE

    gerrit> select * from SCHEMA_VERSION;
    VERSION_NBR | SINGLETON
    ------------+----------
    161         | X
    (1 row; 1 ms)

## gerrit 재시작

database 이전이 완료되면 gerrit을 재시작해서 기능이 정상적으로 동작하는지 점검합니다. 혹시 뭔가 이상한 점이 발견되면 맨 앞에서 백업해두었던 tarball을 이용해 되돌리면 손쉽게 복원이 가능합니다... (무책임)


## 후기

이렇게 열과 성의를 다해 database를 이전하였건만, 성능과 관련해서는 딱히 나아진 점이 보이지 않아서, 다시 h2 database로 되돌렸습니다. 그래도 필요하면 언제든지 database 변환이 가능하다는 것을 위안으로 삼아야죠.

gerrit 성능에 대한 삽질은 나중에 기회가 있을 때 이야기를 풀어보도록 하겠습니다.
