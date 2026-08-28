# Project Paeon

사업자등록번호를 통해 정확한 상호명을 추려내는 사이트. https://paeon.코드.kr 에서
oh-my-homelab(Kubernetes GitOps)으로 배포됩니다.

## Dev

Python 3.14 이상이 필요합니다.

```bash
> python -m venv venv
> source venv/bin/activate
> pip install -r requirements.txt
> SECRET_KEY=dev DEBUG=True python manage.py migrate
> SECRET_KEY=dev DEBUG=True python manage.py runserver
```

`DATABASE_URL`을 안 주면 로컬 SQLite(`db.sqlite3`)로 자동 폴백합니다. 배포 환경(k8s)에서는
Postgres `DATABASE_URL`을 Secret으로 주입합니다.

## How to use

1. 사업자등록번호를 입력합니다.
2. 상호명으로 유추되는 회사명 입력 (여러개를 동시에 집어넣어도 됩니다.)
3. 검색 후 목록 보기

<img width="800" alt="image" src="https://user-images.githubusercontent.com/47373998/164879467-d8bbff3e-470c-44f2-b219-725ef397bfc4.png">

## 데이터

검색은 국민연금공단이 공개하는 사업장가입내역([data.go.kr 카탈로그 #15083277](https://www.data.go.kr/catalog/15083277/fileData.json))을
로컬 DB(`PensionCompany`)에 적재해두고 그 안에서 조회합니다 — 요청마다 외부 API를 부르지
않습니다.

데이터는 매월 갱신되므로(`자료생성년월` 필드), 배포 환경에서는 `deploy/charts/paeon`의
CronJob이 매달 1일 자동으로 `python manage.py reload_pension_company`를 실행해 전체
테이블을 최신 CSV로 교체합니다. 로컬에서 수동으로 갱신하려면:

```bash
python manage.py reload_pension_company
```

## 배포

Dockerfile + `deploy/charts/paeon`(Helm) — CI가 `main` 푸시마다 `ghcr.io/shinkeonkim/paeon`에
이미지를 올리고, oh-my-homelab의 ArgoCD Application이 이 차트를 GitOps로 동기화합니다.
`SECRET_KEY`/`DATABASE_URL`은 이 레포에 없고, oh-my-homelab 쪽 SOPS 암호화 Secret으로만
주입됩니다.
