# [GITHUB ISSUE] feat: Enable RAG chatbot on Streamlit Cloud deployment

## 📋 이슈 개요
- **이슈 목적**: Streamlit Cloud 배포 결과에서 RAG 챗봇(풀 버전 대시보드)을 정상적으로 사용할 수 있도록 개선합니다.
- **관련 파일**:
  - [.gitignore](file:///c:/documents/26-1/한신대ABC캠프-2026/ABC-RAG/.gitignore)
  - [requirements.txt](file:///c:/documents/26-1/한신대ABC캠프-2026/ABC-RAG/requirements.txt)
  - [src/dashboard.py](file:///c:/documents/26-1/한신대ABC캠프-2026/ABC-RAG/src/dashboard.py)

---

## 🔍 문제 원인 분석
1. **Chroma DB 부재**: `.gitignore`에서 `data/chroma_yes24/` 폴더를 차단하여, 배포용 깃허브 원격지에 임베딩 벡터 데이터베이스가 올라가지 않았습니다.
2. **의존성 라이브러리 누락**: `requirements.txt`에 `chromadb`, `transformers`, `torch` 등 RAG 구동을 위한 주요 라이브러리 목록이 누락되어 클라우드 빌드 시 패키지가 설치되지 않았습니다.
3. **대시보드 우회 적용**: 1, 2번 원인에 의한 에러 회피를 위해 `src/dashboard.py`에 경량 버전을 덮어씌워 둔 상태입니다. RAG 인프라가 확보되면 원래의 챗봇 버전으로 복원되어야 합니다.

---

## 🛠️ 해결 및 개선 계획
1. **`.gitignore` 수정**: 
   - `data/chroma_yes24/` 폴더를 제외 규칙에서 제거하여 Git이 추적하도록 만듭니다. (전체 파일 용량 합계 약 12MB 내외로, GitHub의 단일 파일 100MB 업로드 제한에 저촉되지 않아 직접 업로드 가능)
2. **`requirements.txt` 업데이트**:
   - RAG 챗봇에 필요한 `chromadb`, `transformers`, `torch` 패키지 버전을 명시하여 추가합니다.
3. **`src/dashboard.py` 복원**:
   - `src/dashboard_local.py`로 백업해 둔 RAG 챗봇 풀버전 대시보드 코드를 다시 `src/dashboard.py`로 롤백(복원)합니다.
4. **Hugging Face 임베딩 모델 자동 다운로드 유도**:
   - 대용량 임베딩 모델 가중치 파일(440MB)이 들어있는 `data/hf_models/`는 `.gitignore` 차단 상태를 유지합니다.
   - 대신 Streamlit Cloud 컨테이너가 부팅될 때 Hugging Face Hub에서 자동으로 `klue/bert-base` 가중치를 다운로드 및 캐싱하여 정상적으로 RAG 모델을 구동하게 유도합니다.
