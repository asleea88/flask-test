### Build & Run Server
```
$ docker-compose up
```
- docker-compose 실행 중 이미지가 없다면 자동 빌드 후 실행합니다.
- 만약 수동 빌드를 원하는 경우  `docker build . -t wanted_api` 를 통해 수행할 수 있습니다.

### Test
```
$ pip3 install -r requirements.txt
$ pip3 install -r requirements-test.txt
$ cd ./wanted
$ pytest -v
```

### Database
- 제공된 csv 파일 기준으로 매 실행 마다 DB를 초기화 합니다.
