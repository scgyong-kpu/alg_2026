# 개발 환경 설정

이 문서는 알고리즘 수업 예제 코드를 실행하기 위한 Python 개발 환경 설정 방법을 설명합니다.

## 1. 저장소 복제

공유받은 GitHub 주소에서 저장소를 복제합니다.

```bash
git clone https://github.com/scgyong-kpu/alg_2026.git
cd alg_2026
```

## 2. Visual Studio Code에서 폴더 열기

Visual Studio Code를 실행한 뒤 다음 메뉴를 선택합니다.

```text
File > Open Folder...
```

`alg_2026` 폴더를 선택합니다. 파일 열기로 열지 않고 폴더 열기로 엽니다.
반드시 프로젝트 루트 폴더인 `alg_2026`을 열어야 합니다.

## 3. VSCode Python 확장 설치

VSCode 왼쪽의 Extensions 아이콘을 누른 뒤 `Python`을 검색합니다.

Microsoft에서 제공하는 다음 확장을 설치합니다.

- Python
- Python Debugger

이미 설치되어 있다면 다시 설치할 필요는 없습니다.

## 4. Python 버전 확인

이 수업에서는 Python 3.13 사용을 권장합니다.

Windows PowerShell:

```powershell
py --version
```
macOS / Linux:

```bash
python3 --version
```


Python 3.14처럼 너무 최신 버전은 일부 패키지가 아직 지원하지 않을 수 있습니다.

## 5. 가상 환경 만들기

VSCode에서 터미널을 엽니다.

```text
Terminal > New Terminal
```

프로젝트 폴더 안에 가상 환경을 만듭니다.

Windows PowerShell:

```powershell
py -m venv .venv
```

macOS / Linux:

```bash
python3 -m venv .venv
```

## 6. 가상 환경 활성화

macOS / Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

활성화가 끝나면 터미널 프롬프트 앞에 `(.venv)`가 표시됩니다.

VSCode가 Python 인터프리터를 선택하라고 묻는다면 `.venv` 안에 있는 Python을 선택하세요.

## 7. 공통 모듈 설치

수업 예제 실행에 필요한 패키지를 설치합니다.

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`requirements.txt`에는 수업 예제에서 공통으로 사용하는 `pyvisalgo` 모듈이 editable 모드로
포함되어 있습니다. editable 모드로 설치하면 저장소 안의 소스 파일을 수정했을 때 다시
설치하지 않아도 바로 반영됩니다.

## 8. 예제 실행

예제는 프로젝트 루트 폴더에서 실행합니다.

```bash
python week01_ch1/ch1_1_find_max.py
```

VSCode에서 파일을 바로 실행할 수도 있습니다.

- macOS: `Cmd+Shift+Option+Enter`
- Windows: `Ctrl+Shift+Alt+Enter`

디버깅하면서 실행하려면 `F5`를 누릅니다.

파일이 있는 폴더를 기준으로 실행되도록 VSCode 설정에서 `Execute File in Dir` 옵션을 켜세요.
이 옵션을 켜면 예제 파일이 자기 폴더를 현재 작업 폴더로 사용해서 실행됩니다.

import 오류가 발생하면 다음을 확인하세요.

- VSCode에서 `alg_2026` 루트 폴더를 열었는지 확인합니다.
- 가상 환경이 활성화되어 있는지 확인합니다.
- `python -m pip install -r requirements.txt` 명령이 정상적으로 끝났는지 확인합니다.
