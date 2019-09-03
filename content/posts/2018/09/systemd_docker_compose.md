Title: Systemd 로 docker-compose 간단하게 관리하기
Slug: 2018_09_11_systemd_docker_compose
Date: 2018-09-11 23:17
Category: tech
Tags: systemd, docker, docker-compose, gitlab
Summary: systemd와 docker-compose를 이용해 gitlab 인스턴스 관리하기


회사에서 가지고 노는(?) 일부 서비스는 [docker-compose](https://docs.docker.com/compose/overview/)를 이용해 관리를 하는데, 가끔씩 docker 이미지를 업그레이드 할 필요가 있습니다.
docker-compose 명령을 이용하면 간단하게 업그레이드 할 수 있긴 하지만, systemd 서비스 형식을 이용하면 왠지 더 뽀대나고, 편하게 관리할 수 있을 것 같다는 생각이 들어서 시도해보았습니다. (덤으로 ubuntu 18.04부터는 systemd로 서비스 관리가 됩니다.)

다음은 docker-compose 를 수행할 systemd service unit 파일 (`/etc/systemd/system/docker-compose@.service`)입니다.


    [Unit]
    Description=Start docker instance with composer.yml
    After=network.target
    RequiresMountsFor=/srv

    [Service]
    Type=oneshot
    ExecStartPre=-/usr/bin/docker-compose down
    ExecStartPre=-/usr/bin/docker-compose pull
    ExecStart=/usr/bin/docker-compose up -d
    WorkingDirectory=/etc/docker-compose/%i


`ExecStartPre` 에서 업데이트할 도커 이미지가 있는지 확인한 후 업그레이드를 하고, (실패하더라도 fallback 으로 무시) docker-compose를 이용해 인스턴스를 시작합니다.
docker-compose에 필요한 `compose.yml`은 `/etc/docker-compose/ 의 하위 디렉토리`에 찾을 수 있게 `WorkingDirectory`를 설정하였습니다.


아래는 gitlab 을 띄우기 위한 `/etc/docker-compose/gitlab/compose.yml` 파일입니다.


    # vim: ts=2 sw=2 sts=2 et ai
    gitlab:
      image: gitlab/gitlab-ce:latest
      restart: always
      hostname: gitlab.private
      container_name: gitlab
      environment:
        GITLAB_OMNIBUS_CONFIG: |
          external_url 'http://gitlab.example.com/'
          # Add any other gitlab.rb configuration here, each on its own line
          gitlab_rails['ldap_enabled'] = true
          gitlab_rails['ldap_servers'] = YAML.load <<-'EOS'
          main: # 'main' is the GitLab 'provider ID' of this LDAP server
            label: 'LDAP'
            host: 'ldap.example.com'
            port: 389
            uid: 'uid'
            bind_dn: 'cn=admin,dc=example,dc=com'
            password: 'ldapadminpassword'
            encryption: 'plain' # "start_tls" or "simple_tls" or "plain"
            verify_certificates: false
            active_directory: false
            allow_username_or_email_login: true
            lowercase_usernames: true
            block_auto_created_users: false
            base: 'ou=members,dc=example,dc=com'
            user_filter: ''
            attributes:
                username: ['uid']
                email: ['mail']
                name: 'cn'
            ## EE only
            group_base: ''
            admin_group: ''
            sync_ssh_keys: false
          EOS
      ports:
        - "127.0.0.1:8080:80"
      volumes:
        - /etc/gitlab:/etc/gitlab
        - /var/log/gitlab:/var/log/gitlab
        - /srv/gitlab/data:/var/opt/gitlab

docker 인스턴스의 lifecycle은 docker service에서 해주며, compose.yml에서 docker 서비스가 시작하면 인스턴스가 자동으로 시작하도록 `restart: always`로 설정했기 때문에, systemd의 Service Type은 oneshot으로 설정했습니다. 앞에서도 언급했지만 systemd unit의 역할은 `docker 이미지의 업데이트` 스크립트 입니다.


이제 gitlab 인스턴스를 구동시키다가, 업데이트가 필요하면, 다음과 같이 systemd service를 실행해서 docker 이미지를 업데이트하면 됩니다.

    $ sudo systemctl restart docker-compose@gitlab

참쉽죠?
