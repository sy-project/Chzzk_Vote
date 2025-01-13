# Chzzk_Vote
파이썬 치지직 투표기

파이썬을 이용해 채팅을 크롤링 후 "!투표 1" 과 같은 채팅을 감지하여 투표합니다.

이 코드는 [Buddha7771](https://github.com/Buddha7771/ChzzkChat) 님의 코드를 기반으로 작성되었습니다.

아래는 Anaconda가 정상 설치되었다는 가정하의 튜토리얼입니다.

## 설치 - 명령어 실행
    # 코드 다운로드
    $ git clone https://github.com/sy-project/Chzzk_Vote.git .
    $ cd Chzzk_Vote

    # 가상환경 설치
    $ conda create -n chzzk python=3.9
    $ conda activate chzzk

    # 패키지 설치
    $ pip install -r requirements.txt

## 설치 - bat 파일 실행
    # 코드 다운로드 - zip 압축파일
    `< > Code` 클릭 > `Download ZIP` 클릭

    # 가상환경 & 패키지 설치 - bat 파일
    `install.bat` 실행

## 준비하기

1. 웹 브라우저에서 네이버를 키고 개발자 도구(F12)를 킵니다.
	@@ -35,15 +30,11 @@
## 사용하기


    # 예시 - 명령어 실행
    python main.py 

    # 예시 - bat 파일
    `start.bat` 실행

    # 특정 채널에 적용하려면 아이디를 찾아 옵션으로 넣습니다.
    채널의 링크가 `https://chzzk.naver.com/a3f9b654ff36bb29ab53eb38c25faab9` 일 경우 아래와 같이 작성을 해줍니다.
    python main.py --streamer_id a3f9b654ff36bb29ab53eb38c25faab9

> 출력 내용은 자동으로 chat.log에 저장됩니다.   
> 작동을 중지하려면 `ctrl + c'을 눌러주세요
