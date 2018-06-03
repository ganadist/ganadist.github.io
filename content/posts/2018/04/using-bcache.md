Title: bcache 사용하기
Slug: 2018_04_18_using_bcache
Date: 2018-04-18 15:04
Category: tech
Tags: linux, performance, ssd, hdd
Author: YOUNG HO CHA
Summary: linux bcache를 이용해 sshd 만들기

bcache 는 ssd와 hdd를 조합해서 [sshd(hybrid drive)](https://en.wikipedia.org/wiki/Hybrid_drive)를 소프트웨어 적으로 구현하는 리눅스 커널의 기능입니다.

일반적으로 ssd는 hdd보다 전송 속도 및 반응 속도가 빨라서 입출력이 많은 작업에 사용하기 좋지만, 가격이 비싸기 때문에 대용량의 데이터를 보관하는데 적합하지 않습니다. 하지만 빠른 반응속도를 가진 용량 작은 ssd(Intel Optane Memory등)와 적당한 가격의 큰 hdd를 bcache로 엮어주면 가성비가 괜찮은 sshd를 임의로 만들 수 있습니다.

먼저 bcache를 구성하려면 데이터가 비어있는 ssd 파티션과 마찬가지로 데이터가 비어있는 hdd 파티션이 필요합니다.

먼저 ssd 파티션을 bcache의 cache 장치로 등록합니다.

    $ sudo make-bcache -C --block 512 --bucket 2M --wipe-bcache /dev/nvme0n1p3
    UUID:            29373e97-cb10-4474-8ab2-2d99917da727
    Set UUID:        7701c988-810e-4603-be15-a122c670975e
    version:         0
    nbuckets:        141280
    block_size:      1
    bucket_size:     4096
    nr_in_set:       1
    nr_this_dev:     0
    first_bucket:    1

--block 옵션은 연동할 hdd의 블럭단위크기로 설정하고, --bucket 옵션은 ssd의 작업단위크기로 설정하면 됩니다.

단 --bucket 옵션의 크기를 너무 크게 주면 등록이 되지 않기 때문에 오류가 발생하면 dmesg 명령으로 커널 메세지를 확인하시기 바랍니다.

위와 같이 cache 장치로 등록하면 "Set UUID"를 주의깊게 기억하고 있다가 hdd를 등록할 때 사용하면 됩니다.

이미 등록된 ssd의 set uuid는 다음과 같이 확인해볼 수 있습니다.

    $ ls -l /sys/fs/bcache
    drwxr-xr-x 7 root root    0  4월 18 15:34 7701c988-810e-4603-be15-a122c670975e
    --w------- 1 root root 4096  4월 18 14:36 register
    --w------- 1 root root 4096  4월 18 14:36 register_quiet

또는 다음 명령의 출력 결과 중 cset.uuid 를 확인해도 됩니다.

    $ sudo bcache-super-show /dev/nvme0n1p3
    sb.magic           ok
    sb.first_sector    8 [match]
    sb.csum            268D099BA966DCC6 [match]
    sb.version         3 [cache device]

    dev.label          (empty)
    dev.uuid           29373e97-cb10-4474-8ab2-2d99917da727
    dev.sectors_per_block     8
    dev.sectors_per_bucket    8192
    dev.cache.first_sector    8192
    dev.cache.cache_sectors   578674688
    dev.cache.total_sectors   578682880
    dev.cache.ordered    yes
    dev.cache.discard    no
    dev.cache.pos        0
    dev.cache.replacement 0 [lru]

    cset.uuid          7701c988-810e-4603-be15-a122c670975e

ssd가 구성되면, backing partition으로 사용될 hdd 를 초기화 합니다. 다음 옵션중 --cset-uuid 의 인자는 위에서 확인했던 set uuid를 입력하면 됩니다.

    $ export CSET_UUID=7701c988-810e-4603-be15-a122c670975e
    $ sudo make-bcache -B  --writeback --cset-uuid $CSET_UUID /dev/sdb2

이렇게 명령을 수행하면 bcache0 장치가 등록되는데, 커널 메세지로 확인이 가능합니다.

    bcache: register_cache() registered cache device nvme0n1p3
    bcache: register_bdev() registered backing device sdb2
    bcache: bch_cached_dev_attach() Caching sdb2 as bcache0 on set 7701c988-810e-4603-be15-a122c670975e

이렇게 생성된 bcache 장치에 파일시스템을 구성 후 mount 하고 사용하면 됩니다.

    $ sudo mkfs.ext4 -L BUILD_OUT /dev/bcache0
    $ sudo mount /dev/bcache0 /srv/build/out

그리고 용도에 따라서 cache mode를 변경할 수 있습니다.

 * writeback : write 에 대해 cache 가 됩니다. 시스템이 비정상적으로 종료되거나, 갑작스런 전원공급 중단이 발생할 경우 데이터가 유실될 가능성이 있습니다만, 빠른 write속도가 제공됩니다.

 * writethrough: ssd와 hdd에 동시에 write를 합니다.
 * writearound: write cache가 동작하지 않습니다.

 아래 2가지 모드에서는 writeback보다 write속도가 떨어지지만, 그만큼 안정성은 올라갑니다. 저장장치의 용도에 따라 적합한 cache mode를 선택해서 사용하면 됩니다.


    $ cat /sys/block/bcache0/bcache/cache_mode
    writethrough writeback [writearound] none
    $ echo writeback | sudo tee /sys/block/bcache0/bcache/cache_mode
    writeback
    $ cat /sys/block/bcache0/bcache/cache_mode
    writethrough [writeback] writearound none

참고:

  * [공식 홈페이지](https://bcache.evilpiepirate.org/)
  * [커널 문서](https://github.com/torvalds/linux/blob/master/Documentation/bcache.txt)    
  * [Arch Linux 문서](https://wiki.archlinux.org/index.php/Bcache)
  * [Ubuntu 문서](https://wiki.ubuntu.com/ServerTeam/Bcache)
