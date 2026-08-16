# GNOME Shortcut Manager

[English](README.md) | **한국어**

`gnome_shortcut_manager.sh`는 실행 파일이나 사용자 스크립트를 GNOME 애플리케이션 메뉴와 바탕화면에 `.desktop` 단축 아이콘으로 등록하고 관리하는 대화형 Bash 도구입니다.

영어와 한국어 인터페이스를 제공하며, 실행 파일 검증부터 아이콘 탐색, 실행 권한과 GNOME 신뢰 설정, 애플리케이션 데이터베이스 갱신까지 한 번에 처리합니다.

## 주요 기능

### 영어/한국어 인터페이스

- 실행할 때 `English` 또는 `한국어` 선택
- 입력 없이 Enter를 누르면 기본 언어인 영어 사용
- 선택한 언어를 현재 실행이 끝날 때까지 메뉴, 안내, 경고, 오류 및 아이콘 설명에 적용
- 화면 문구를 `text_id`, 영문, 한글 순서의 번역 배열로 관리

```bash
define_text \
    "app_title" \
    "GNOME Shortcut Manager" \
    "그놈 단축 아이콘 관리자"
```

언어 설정은 파일에 저장되지 않으므로 스크립트를 다시 실행하면 언어 선택 화면이 다시 표시됩니다.

### 단축 아이콘 등록

- 입력한 실행 파일 또는 스크립트의 존재 여부 확인
- 디렉터리를 실행 파일로 입력하지 못하도록 검증
- 실행 권한이 없으면 `chmod +x` 적용 여부 확인
- 파일명을 기반으로 기본 앱 이름 제안
- 터미널 실행 여부, 설명, 카테고리 설정
- `~/.local/share/applications`에 `.desktop` 파일 생성
- 선택에 따라 GNOME 바탕화면에도 동일한 단축 아이콘 생성

지원하는 카테고리는 `Utility`, `Development`, `Game`, `Network`, `AudioVideo`, `Office`, `System`입니다.

### 아이콘 선택

아이콘은 다음 순서로 선택할 수 있습니다.

1. 실행 파일이 있는 디렉터리에서 최대 3단계 깊이까지 이미지 탐색
2. 발견된 이미지 중 하나 선택
3. 82가지 시스템 아이콘 중 하나 선택
4. 사용자 아이콘 파일의 전체 경로 직접 입력

자동 탐색 대상 확장자는 다음과 같습니다.

```text
.png  .svg  .ico  .xpm  .jpg  .jpeg
```

시스템 아이콘은 Freedesktop 명명 규격과 Ubuntu/GNOME 아이콘 테마에서 널리 사용되는 이름으로 구성됩니다. 설치된 아이콘 테마에 따라 실제 모양이 달라질 수 있습니다.

- 기본/분류: 실행 파일, 터미널, 설정, 게임, 인터넷, 오피스, 개발 등
- 도구/문서: 계산기, 편집기, 압축, 시스템 모니터, 로그, PDF 등
- 인터넷/통신: 서버, Wi-Fi, 이더넷, VPN, 메일, 채팅, 블루투스 등
- 파일/저장장치: 디스크, USB, 원격 폴더, 다운로드, 사진, 비디오 등
- 멀티미디어: 그래픽, 카메라, 음악, 헤드폰, 스피커, 마이크 등
- 시스템/보안: 잠금, 인증, 사용자, 입력장치, 프린터, 배터리 등

### 등록된 단축 아이콘 수정

사용자 애플리케이션 디렉터리에 있는 `.desktop` 파일을 번호로 선택하여 앱 이름, 실행 파일 경로, 아이콘, 터미널 실행 여부를 수정할 수 있습니다. 같은 파일명의 단축 아이콘이 바탕화면에도 있으면 수정 내용을 자동으로 동기화합니다.

### 등록 목록 조회 및 삭제

- 앱 이름, 실행 명령, 아이콘 정보 표시
- 이 도구가 생성한 항목에는 `[manager-created]` 또는 `[매니저 생성]` 표시
- 삭제 전 대상 앱 이름과 파일명을 다시 보여주고 확인 요청
- 확인하면 애플리케이션 메뉴와 바탕화면의 동일한 파일을 함께 삭제

> 주의: 목록에는 이 도구가 만든 파일뿐 아니라 `~/.local/share/applications`에 있는 모든 사용자 `.desktop` 파일이 표시될 수 있습니다. 삭제할 때 대상 이름과 경로를 확인하세요.

### GNOME 반영 처리

단축 아이콘을 생성하거나 변경한 후 다음 작업을 가능한 범위에서 자동 수행합니다.

- `.desktop` 파일에 실행 권한 부여
- `gio trust` 및 `metadata::trusted` 설정
- `update-desktop-database` 실행
- 사용자 GTK 아이콘 캐시 갱신
- GNOME Shell과 DING이 변경을 감지하도록 디렉터리 갱신 이벤트 발생

관련 명령이 설치되어 있지 않은 경우 해당 작업만 건너뛰며 기본 등록 작업은 계속 진행합니다.

## 요구 사항

- GNOME 데스크톱 환경
- Bash 4 이상(연관 배열 사용)
- 기본 GNU/Linux 명령: `find`, `sed`, `awk`, `grep`, `cut`, `realpath`
- 선택 기능: `xdg-user-dir`, `gio`, `update-desktop-database`, `gtk-update-icon-cache`

## 설치 및 실행

저장소 또는 파일이 있는 디렉터리로 이동한 후 실행 권한을 부여합니다.

```bash
cd /path/to/shortcut
chmod +x gnome_shortcut_manager.sh
./gnome_shortcut_manager.sh
```

실행 권한을 변경하지 않고 Bash로 직접 실행할 수도 있습니다.

```bash
bash gnome_shortcut_manager.sh
```

## 실행 예제

### 예제 1: 영어 인터페이스로 실행

언어 선택에서 Enter를 누르면 영어가 기본으로 적용됩니다.

```text
$ ./gnome_shortcut_manager.sh
======================================================
          Select Language / 언어 선택
======================================================

  1) English
  2) 한국어 (Korean)

Select (1-2, default: 1):

======================================================
                GNOME Shortcut Manager
======================================================

Choose an action:

  1) Register a new executable shortcut
  2) Edit a registered app shortcut
  3) Delete a registered app shortcut
  4) View all registered apps
  0) Exit
```

### 예제 2: 한국어로 실행 파일 등록

다음은 `/opt/my-tool/run.sh`를 터미널에서 실행하는 유틸리티로 등록하는 예시입니다. 실제 아이콘 번호는 표시된 목록에서 원하는 항목의 번호를 선택하면 됩니다.

```text
$ ./gnome_shortcut_manager.sh
선택 (1-2, 기본값 1): 2

원하시는 작업을 선택하세요:
  1) 새 실행파일 단축아이콘 등록
  2) 등록된 앱 단축아이콘 수정
  3) 등록된 앱 단축아이콘 삭제
  4) 등록된 앱 목록 전체 보기
  0) 종료

선택 (0-4): 1
실행파일의 전체 경로를 입력하세요 (취소: q): /opt/my-tool/run.sh
앱 이름 (기본값: 'Run'): My Tool

아이콘 선택 방식을 선택하세요:
  1) 추천 시스템 아이콘 82가지 중 선택
  2) 직접 아이콘 파일 경로 입력
선택 (1-2, 기본값 1): 1
사용할 시스템 아이콘 번호를 선택하세요 (1-82): 2
✔ 시스템 아이콘 선택: utilities-terminal

터미널(콘솔) 창에서 실행해야 하는 앱입니까? (y/N): y
앱 설명/주석 (선택사항, 엔터 시 기본값): My terminal tool
카테고리 번호 선택 (1-7, 기본값 1): 1
바탕화면(Desktop)에도 단축아이콘을 생성할까요? (Y/n): y

✔ 'My Tool' 단축아이콘 등록이 성공적으로 완료되었습니다!
```

등록이 완료되면 일반적으로 다음 파일이 만들어집니다.

```text
~/.local/share/applications/my-tool.desktop
~/Desktop/my-tool.desktop
```

생성되는 `.desktop` 파일은 다음과 같은 구조입니다.

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=My Tool
Comment=My terminal tool
Exec="/opt/my-tool/run.sh" %u
Icon=utilities-terminal
Terminal=true
Categories=Utility;
StartupNotify=true
X-Created-By=shortcut-manager
```

### 예제 3: 사용자 아이콘 파일 지정

아이콘 선택 방식에서 `2`를 입력하고 이미지 파일의 전체 경로를 지정합니다.

```text
아이콘 선택 방식을 선택하세요:
  1) 추천 시스템 아이콘 82가지 중 선택
  2) 직접 아이콘 파일 경로 입력
선택 (1-2, 기본값 1): 2
아이콘 이미지 파일의 전체 경로를 입력하세요: /opt/my-tool/assets/icon.png
```

파일이 존재하면 절대 경로가 `.desktop` 파일의 `Icon` 값으로 저장됩니다.

### 예제 4: 등록 정보 수정

메인 메뉴에서 `2`를 선택한 뒤 수정할 앱과 항목을 차례로 선택합니다.

```text
선택 (0-4): 2

--- 등록된 앱 목록 (~/.local/share/applications) ---
   1) My Tool                   [매니저 생성]
      ├─ 실행경로: "/opt/my-tool/run.sh" %u
      └─ 아이콘: utilities-terminal

수정할 앱의 번호를 선택하세요 (1-1, 취소: 0): 1

  1) 앱 이름 변경
  2) 실행 경로 변경
  3) 아이콘 변경
  4) 터미널 실행여부
  5) 수정 완료 및 저장
  0) 수정 취소

수정할 항목 선택 (0-5): 3
```

원하는 항목을 변경한 후 `5`를 선택해야 수정 사항이 저장됩니다.

### 예제 5: 목록 조회 및 삭제

목록만 확인하려면 메인 메뉴에서 `4`를 선택합니다.

```text
선택 (0-4): 4

--- 등록된 앱 목록 (~/.local/share/applications) ---
   1) My Tool                   [매니저 생성]
      ├─ 실행경로: "/opt/my-tool/run.sh" %u
      └─ 아이콘: utilities-terminal
```

삭제하려면 메인 메뉴에서 `3`을 선택하고 확인 질문에 `y`를 입력합니다.

```text
선택 (0-4): 3
삭제할 앱의 번호를 입력하세요 (1-1, 취소: 0): 1
⚠ 정말로 'My Tool' (my-tool.desktop) 단축아이콘을 삭제하시겠습니까?
확인 (y/N): y
✔ 'My Tool' 삭제 완료!
```

## 생성 경로

| 대상 | 기본 경로 |
|---|---|
| GNOME 애플리케이션 메뉴 | `~/.local/share/applications/*.desktop` |
| 바탕화면 | `xdg-user-dir DESKTOP` 결과 또는 `~/Desktop` |
| 사용자 아이콘 캐시 | `~/.local/share/icons` |

앱 이름은 소문자 파일 ID로 변환됩니다. 영문과 숫자가 없는 이름은 `app-<임의 번호>.desktop` 형식으로 생성될 수 있습니다.

## 참고 사항

- 실행 파일 경로와 사용자 아이콘 경로는 반드시 실제로 존재해야 합니다.
- 주변 아이콘 검색은 실행 파일 디렉터리 아래에서 수행되므로 파일이 많은 경로에서는 시간이 걸릴 수 있습니다.
- 시스템 아이콘 이름을 현재 테마가 제공하지 않으면 GNOME이 대체 아이콘을 표시할 수 있습니다.
- 바탕화면 아이콘 표시는 GNOME 확장 기능 또는 DING 설정에 영향을 받을 수 있습니다.
- 스크립트는 시스템 전체가 아닌 현재 사용자 계정의 애플리케이션 디렉터리를 관리합니다.
