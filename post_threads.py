"""차곡 Threads 자동 게시 (AI 호출 없음, 무료).
posts.csv 에서 status == '검토 완료' 이고 날짜/시간이 지난 첫 글을 올린다.
본문에 '▼ 댓글 이어쓰기' 가 있으면 앞부분은 본글, 뒷부분은 자기 글의 답글로 올린다.
"""
import csv, os, sys, time, datetime as dt, requests

API = "https://graph.threads.net/v1.0"
TOKEN = os.environ["THREADS_TOKEN"]
def get_user_id():
    r = requests.get(f"{API}/me", params={"fields": "id", "access_token": TOKEN}, timeout=60)
    if not r.ok:
        sys.exit(f"token check failed {r.status_code}: {r.text}")
    return r.json()["id"]


USER = os.environ.get("THREADS_USER_ID") or get_user_id()
RAW = os.environ.get("MEDIA_BASE_URL", "")  # 예: https://raw.githubusercontent.com/<id>/<repo>/main/media
MARK = "▼ 댓글 이어쓰기"
KST = dt.timezone(dt.timedelta(hours=9))


def call(path, **data):
    r = requests.post(f"{API}/{path}", data={**data, "access_token": TOKEN}, timeout=60)
    if not r.ok:
        sys.exit(f"API error {r.status_code}: {r.text}")
    return r.json()


def container(text, media=None, reply_to=None):
    d = {"text": text}
    if reply_to:
        d["reply_to_id"] = reply_to
    if not media:
        return call(f"{USER}/threads", media_type="TEXT", **d)["id"]
    items = []
    for m in media:
        url = f"{RAW}/{m}"
        kind = "VIDEO" if m.lower().endswith((".mp4", ".mov")) else "IMAGE"
        key = "video_url" if kind == "VIDEO" else "image_url"
        if len(media) == 1:
            return call(f"{USER}/threads", media_type=kind, **{key: url}, **d)["id"]
        items.append(call(f"{USER}/threads", media_type=kind, is_carousel_item="true", **{key: url})["id"])
    time.sleep(20)
    return call(f"{USER}/threads", media_type="CAROUSEL", children=",".join(items), **d)["id"]


def publish(cid):
    time.sleep(30)  # 미디어 처리 대기
    return call(f"{USER}/threads_publish", creation_id=cid)["id"]


def main():
    now = dt.datetime.now(KST)
    with open("posts.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        if row["status"] != "검토 완료":
            continue
        when = dt.datetime.fromisoformat(f'{row["date"]}T{row["time"]}').replace(tzinfo=KST)
        if when > now:
            continue
        body = row["body"]
        main_text, _, reply_text = body.partition(MARK)
        media = [m.strip() for m in row["media"].split("|") if m.strip()]
        pid = publish(container(main_text.strip(), media))
        if reply_text.strip():
            publish(container(reply_text.strip(), reply_to=pid))
        row["status"] = "게시됨"
        break  # 한 번 실행에 한 글만
    with open("posts.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
