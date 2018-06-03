Title: 간단하게 뜯어보는 nbd(network block device)
Slug: 2011_08_15_nbd
Date: 2011-08-15 12:00
Category: tech
Tags: linux
Author: YOUNG HO CHA
Summary: nbd 사용방법


nbd는 소켓을 이용해서 저멀리 떨어져있는 기계의 block장치를 현재 컴퓨터의 block장치처럼 쓰게 하는 리눅스의 기능이다.

물론 꼭 저 멀리 떨어져있을 필요는 없으며, 꼭 block장치여야 한다는 법은 없다.

특정한 위치에서 특정한 길이의 데이터를 read하거나 write할 수만 있으면 상관없다.
 

nbd를 구성하려면 3개의 컴퍼넌트가 필요하다.

 * nbd 커널드라이버
 * nbd 서버
 * nbd 클라이언트
 

## nbd 커널드라이버
커널의 block devices 설정에 포함되어으며, 이 설정을 켜놓으면 /dev/nbd[0-7] 또는 /dev/block/nbd[0-7] 장치로 유저스페이스에 노출된다.


## nbd 클라이언트
nbd서버와 연결한 소켓을 nbd device 장치와 연결해주는 역할을 한다.

그외에 블럭장치의 특성(block 장치의 크기, block size, timeout, 등)을 설정해야 한다.

해당 설정은 [ioctl 명령](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/include/uapi/linux/nbd.h?h=v4.16#n21) 을 참조.

## nbd 서버
nbd 드라이버에서 보낸 요청을 처리하는 서버

nbd의 요청은 [다음과 같은 형태](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/include/uapi/linux/nbd.h?h=v4.16#n66)로 전달된다.


각각의 의미는 다음과 같다.

 * magic: nbd request의 시작. NBD_REQUEST_MAGIC값과 동일해야 한다. 이 값이 틀리면 깨지거나 잘못된 패킷이다.

 * type: 읽기/쓰기 요청의 구분

 * handle: 각 요청을 구분하기 위한 값. nbd_reply에 이 값을 복사해서 응답해야 한다.

 * from: 읽기/쓰기를 시작할 offset

 * len: 읽기/쓰기를 할 길이

쓰기 request일 경우, 위 요청 패킷 바로 뒤에 len에 해당하는 길이의 데이터가 덧붙여 따라온다.

nbd의 요청에 대한 응답은 다음과 같다.

 * magic: nbd reply의 시작. NBD_REPLY_MAGIC값을 채워야 한다.

 * error: 오류 발생시 적절한 errno를 채운다. (보통은 EIO). 에러가 없을 때는 0을 채운다.

 * handle: nbd_request의 handle값을 복사한다.

읽기 request일 경우, 위 응답 패킷을 보낸 후 요청 길이만큼 데이터를 덧붙여 보내면 된다.

위의 모든 값은 모두 Network byte order로 변환해서 처리해야 한다.

자세한건 [nbd 홈페이지](http://nbd.sourceforge.net)의 client/server 코드를 참조.

그리고 위의 server/client는 TCP/IP 소켓으로 구현되어 있지만, 리눅스에서 지원하는 SOCK_STREAM 타입의 소켓이라면 어느것이라도 지원된다. (유닉스 도메인 소켓이나 블루투스, IRDA 등등) 
