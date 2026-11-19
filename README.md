# 차곡 Threads 자동 게시

## 흐름
1. 일정표(쓰레드 탭)에서 확인 끝낸 글만 상태를 "검토 완료"로 바꾼다.
2. 일정표를 CSV로 내려받아 이 저장소의 posts.csv 로 덮어쓴다. (열: date,time,format,body,media,status)
   media 열에는 media/ 폴더 안 파일명을 `|` 로 이어서 쓴다. 예: `a.jpg|b.jpg`  (영상은 음소거 처리한 mp4)
3. GitHub Actions가 하루 5번 돌면서 시간이 지난 "검토 완료" 글을 한 개씩 올리고 "게시됨"으로 바꾼다.

## 설정
- Settings > Secrets and variables > Actions 에 THREADS_TOKEN, THREADS_USER_ID 를 등록한다.
- 이 저장소는 공개(public)다. 사진·영상을 raw.githubusercontent.com 주소로 Threads가 가져간다. 민감한 사진은 media/ 에 넣지 않는다.
- 토큰은 60일마다 만료된다. 그 전에 연장하거나 재발급한다.
- Actions 탭에서 threads-post 를 수동 실행(workflow_dispatch)해 첫 글을 시험한다.

## 주의
- GitHub 예약 실행은 몇 분~수십 분 늦을 수 있다.
- 정확한 API 필드와 한도는 Meta 문서에서 한 번 더 확인할 것.
