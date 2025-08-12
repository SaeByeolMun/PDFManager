# PDFManager

**버전:** 1.0.0  
**저작권:** SaeByeolMun. All rights reserved.

PDFManager는 PDF 문서 변환 및 처리 기능을 제공하는 Windows용 데스크톱 애플리케이션입니다.  
PySide6 기반으로 제작되었으며, PDF 이미지 변환과 텍스트 처리를 지원합니다.

---

## 📦 설치 및 실행

1. `PDFManager.zip` 파일을 다운로드하여 압축을 해제합니다.
2. 압축 해제된 폴더(`MyApp/`) 안에 있는 `PDFManager.exe`를 실행합니다.
3. 설치가 필요하지 않으며, 폴더 내 파일 구조를 변경하지 않는 것이 좋습니다.

> ⚠️ 주의:  
> 일부 바이러스 백신 프로그램이 서명되지 않은 실행 파일에 경고를 표시할 수 있습니다.  
> 이는 잘못된 탐지(오탐)이며, 코드서명 인증서가 없는 경우 초기 배포 시 발생할 수 있습니다.

---

## 📚 주요 기능

- **PDF → 이미지 변환** (JPG/PNG)  
- **PDF 페이지 병합 및 분할**  
- **PDF 메타데이터 읽기 및 수정**  
- **한글 폰트(Nanum Gothic ExtraBold) 적용 UI**  

---

## 🛠 동봉된 구성 요소

- `MyApp.exe` – 메인 실행 파일
- `licenses/` – 사용된 라이브러리 및 리소스의 라이선스 고지
- `docs/` – 사용자 설명서 (PDF/HTML)
- `data/` – 앱 리소스 (아이콘, 폰트, 설정 등)
- `poppler_bin/` – PDF 처리 엔진 Poppler 바이너리
- `platforms/`, `styles/` 등 – Qt 실행에 필요한 플러그인 및 라이브러리

---

## 🔍 시스템 요구사항

- Windows 10 이상 (64비트)
- 최소 4GB RAM

---

## 📖 라이선스 고지

이 애플리케이션은 다음 오픈소스 소프트웨어를 사용합니다.

1. **PySide6**
   - License: LGPL v3
   - Copyright: © The Qt Company Ltd.
   - Website: https://wiki.qt.io/Qt_for_Python

2. **pdf2image**
   - License: MIT
   - Copyright: © Edouard Belval
   - Website: https://pypi.org/project/pdf2image/

3. **PyPDF2**
   - License: BSD-3-Clause
   - Copyright: © 2006-2025 Mathieu Fenniak and contributors
   - Website: https://pypi.org/project/PyPDF2/

4. **Nanum Gothic ExtraBold**
   - License: SIL Open Font License 1.1
   - Copyright: © 2010 NHN Corporation
   - Designed by: Sandoll Communications Inc.
   - Website: https://fonts.google.com/specimen/Nanum+Gothic

5. **Poppler**
   - License: GPL v2 or later
   - Copyright: © 2005-2025 Poppler Developers
   - Website: https://poppler.freedesktop.org/

---

📌 각 라이브러리의 전문 라이선스는 `licenses/` 폴더에 포함되어 있습니다.

---

## 📬 문의

- 이메일: saebyeolm@gmail.com
- 웹사이트: https://binarylog.tistory.com/
