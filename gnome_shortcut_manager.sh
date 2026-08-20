#!/usr/bin/env bash

# ==============================================================================
# GNOME Shortcut Manager
# ==============================================================================
# Registers, edits, and removes .desktop shortcuts for executables and scripts
# in the GNOME application menu and on the desktop.
# ==============================================================================

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Localized text is stored by language and text ID.
APP_LANGUAGE="en"
declare -A TEXT=()

define_text() {
    local text_id="$1"
    local english="$2"
    local korean="$3"
    TEXT["en.${text_id}"]="$english"
    TEXT["ko.${text_id}"]="$korean"
}

t() {
    local text_id="$1"
    shift
    local template="${TEXT["${APP_LANGUAGE}.${text_id}"]:-${TEXT["en.${text_id}"]}}"
    printf "$template" "$@"
}

# Translation entry format:
#   define_text \
#       "text_id" \
#       "English text" \
#       "Korean text"

# Common interface text

define_text \
    "app_title" \
    "GNOME Shortcut Manager" \
    "그놈 단축 아이콘 관리자"

define_text \
    "language_title" \
    "Select Language" \
    "언어 선택"

define_text \
    "language_prompt" \
    "Select (1-2, default: 1): " \
    "선택 (1-2, 기본값 1): "

define_text \
    "language_english" \
    "English" \
    "영어"

define_text \
    "language_korean" \
    "Korean" \
    "한국어"

define_text \
    "pause_prompt" \
    "Press Enter to continue..." \
    "Enter 키를 누르면 진행합니다..."

define_text \
    "invalid_number" \
    "Please enter a valid number." \
    "올바른 번호를 입력하세요."

define_text \
    "range_error" \
    "Please enter a number from %s to %s." \
    "%s부터 %s 사이의 숫자를 입력해주세요."

# Icon selection text

define_text \
    "icon_setting" \
    "Icon Settings" \
    "아이콘 설정"

define_text \
    "searching_nearby" \
    "Searching for icon images near the executable..." \
    "실행파일 경로 주변에서 아이콘 이미지를 탐색 중..."

define_text \
    "detected_icons" \
    "Detected icon images near the executable (%s):" \
    "기존 경로에서 감지된 아이콘 이미지 (%s개):"

define_text \
    "icons_omitted" \
    "... (%s more omitted)" \
    "... (외 %s개 생략)"

define_text \
    "choose_other_icon" \
    "[0] Choose a system icon or enter a custom path" \
    "[0] 감지된 아이콘 대신 시스템 아이콘 / 직접 입력 선택"

define_text \
    "detected_icon_prompt" \
    "Select an icon number (0-%s): " \
    "선택할 아이콘 번호를 입력하세요 (0-%s): "

define_text \
    "selected_icon" \
    "Selected icon: %s" \
    "선택된 아이콘: %s"

define_text \
    "no_nearby_icons" \
    "No icon images (.png, .svg, etc.) were found near the executable." \
    "기존 경로 근처에서 아이콘 이미지(.png, .svg 등)를 찾지 못했습니다."

define_text \
    "icon_method" \
    "Choose an icon selection method:" \
    "아이콘 선택 방식을 선택하세요:"

define_text \
    "choose_system_icon" \
    "Choose from %s recommended system icons" \
    "추천 시스템 아이콘 %s가지 중 선택"

define_text \
    "custom_icon_option" \
    "Enter a custom icon file path" \
    "직접 아이콘 파일 경로 입력"

define_text \
    "method_prompt" \
    "Select (1-2, default: 1): " \
    "선택 (1-2, 기본값 1): "

define_text \
    "custom_icon_prompt" \
    "Enter the full path to an icon image: " \
    "아이콘 이미지 파일의 전체 경로를 입력하세요: "

define_text \
    "invalid_icon_file" \
    "The file does not exist. Please try again." \
    "해당 파일이 존재하지 않습니다. 다시 입력해주세요."

define_text \
    "system_icon_list" \
    "%s standard system icons" \
    "%s가지 시스템 표준 아이콘 목록"

define_text \
    "system_icon_prompt" \
    "Choose a system icon (1-%s): " \
    "사용할 시스템 아이콘 번호를 선택하세요 (1-%s): "

define_text \
    "selected_system_icon" \
    "Selected system icon: %s" \
    "시스템 아이콘 선택: %s"

# Registration text

define_text \
    "register_title" \
    "1. Register a New App Shortcut" \
    "1. 새 앱 단축 아이콘 등록"

define_text \
    "executable_prompt" \
    "Enter the full path to the executable (cancel: q): " \
    "실행파일의 전체 경로를 입력하세요 (취소: q): "

define_text \
    "registration_cancelled" \
    "Registration cancelled." \
    "등록을 취소했습니다."

define_text \
    "path_required" \
    "A path is required." \
    "경로를 입력해야 합니다."

define_text \
    "path_not_found" \
    "The file or path does not exist: %s" \
    "파일 또는 경로가 존재하지 않습니다: %s"

define_text \
    "path_is_directory" \
    "The path is a directory. Enter an executable file path." \
    "입력한 경로는 디렉토리입니다. 실행파일 경로를 입력해주세요."

define_text \
    "no_execute_permission" \
    "The file does not have execute permission (+x)." \
    "해당 파일에 실행 권한(+x)이 없습니다."

define_text \
    "grant_execute_permission" \
    "Grant execute permission? (Y/n): " \
    "실행 권한을 부여하시겠습니까? (Y/n): "

define_text \
    "execute_permission_added" \
    "Execute permission added." \
    "실행 권한을 추가했습니다."

define_text \
    "execute_permission_warning" \
    "The app may not run correctly without execute permission." \
    "실행 권한이 없으면 앱이 정상 실행되지 않을 수 있습니다."

define_text \
    "confirmed_executable" \
    "Confirmed executable: %s" \
    "확인된 실행파일: %s"

define_text \
    "execution_options_prompt" \
    "Additional execution options (optional; %%u is added automatically, e.g. --no-sandbox): " \
    "추가 실행 옵션 (선택사항, %%u 자동 추가, 예: --no-sandbox): "

define_text \
    "app_name_prompt" \
    "App name (default: '%s'): " \
    "앱 이름 (기본값: '%s'): "

define_text \
    "terminal_prompt" \
    "Does this app need to run in a terminal? (y/N): " \
    "터미널(콘솔) 창에서 실행해야 하는 앱입니까? (y/N): "

define_text \
    "comment_prompt" \
    "App description/comment (optional; Enter for default): " \
    "앱 설명/주석 (선택사항, 엔터 시 기본값): "

define_text \
    "category_title" \
    "Choose a category:" \
    "카테고리 선택:"

define_text \
    "category_utility" \
    "Utility (default)" \
    "Utility (유틸리티 - 기본값)"

define_text \
    "category_development" \
    "Development" \
    "Development (개발 도구)"

define_text \
    "category_game" \
    "Game" \
    "Game (게임)"

define_text \
    "category_network" \
    "Network" \
    "Network (인터넷/네트워크)"

define_text \
    "category_multimedia" \
    "AudioVideo" \
    "AudioVideo (멀티미디어)"

define_text \
    "category_office" \
    "Office" \
    "Office (오피스)"

define_text \
    "category_system" \
    "System" \
    "System (시스템)"

define_text \
    "category_prompt" \
    "Choose a category (1-7, default: 1): " \
    "카테고리 번호 선택 (1-7, 기본값 1): "

define_text \
    "desktop_prompt" \
    "Also create the shortcut on the Desktop? (Y/n): " \
    "바탕화면(Desktop)에도 단축아이콘을 생성할까요? (Y/n): "

define_text \
    "shortcut_created" \
    "App shortcut created: %s" \
    "앱 단축아이콘 파일이 생성되었습니다: %s"

define_text \
    "desktop_created" \
    "Shortcut also placed on the Desktop (%s)." \
    "바탕화면(%s)에도 단축아이콘이 배치되었습니다."

define_text \
    "registration_complete" \
    "'%s' was registered successfully!" \
    "'%s' 단축아이콘 등록이 성공적으로 완료되었습니다!"

# App list and editing text

define_text \
    "no_registered_apps" \
    "No user shortcuts are registered. (%s)" \
    "등록된 사용자 단축아이콘이 없습니다. (%s)"

define_text \
    "registered_apps" \
    "Registered Apps (%s)" \
    "등록된 앱 목록 (%s)"

define_text \
    "manager_created" \
    "manager-created" \
    "매니저 생성"

define_text \
    "unknown" \
    "Unknown" \
    "미정"

define_text \
    "executable_label" \
    "Executable" \
    "실행경로"

define_text \
    "icon_label" \
    "Icon" \
    "아이콘"

define_text \
    "edit_title" \
    "2. Edit an App Shortcut" \
    "2. 등록된 앱 단축아이콘 수정"

define_text \
    "no_apps_to_edit" \
    "There are no shortcuts to edit." \
    "수정할 단축아이콘이 존재하지 않습니다."

define_text \
    "edit_app_prompt" \
    "Choose an app to edit (1-%s, cancel: 0): " \
    "수정할 앱의 번호를 선택하세요 (1-%s, 취소: 0): "

define_text \
    "edit_cancelled" \
    "Editing cancelled." \
    "수정을 취소했습니다."

define_text \
    "selected_file" \
    "Selected file: %s" \
    "선택한 파일: %s"

define_text \
    "editing_app" \
    "Editing App: %s" \
    "앱 정보 수정중: %s"

define_text \
    "file_path" \
    "File path: %s" \
    "파일 경로: %s"

define_text \
    "edit_name" \
    "Change app name       (current: %s)" \
    "앱 이름 변경    (현재: %s)"

define_text \
    "edit_executable" \
    "Change executable path (current: %s)" \
    "실행 경로 변경  (현재: %s)"

define_text \
    "edit_exec_options" \
    "Change execution options (current: %s)" \
    "실행 옵션 변경  (현재: %s)"

define_text \
    "edit_icon" \
    "Change icon           (current: %s)" \
    "아이콘 변경     (현재: %s)"

define_text \
    "edit_terminal" \
    "Toggle terminal mode  (current: %s)" \
    "터미널 실행여부 (현재: %s)"

define_text \
    "save_changes" \
    "Save changes" \
    "수정 완료 및 저장"

define_text \
    "cancel_edit" \
    "Cancel editing" \
    "수정 취소"

define_text \
    "edit_item_prompt" \
    "Choose an item to edit (0-6): " \
    "수정할 항목 선택 (0-6): "

define_text \
    "new_name_prompt" \
    "Enter a new app name (current: %s): " \
    "새 앱 이름을 입력하세요 (현재: %s): "

define_text \
    "name_changed" \
    "App name changed." \
    "앱 이름이 변경되었습니다."

define_text \
    "new_executable_prompt" \
    "Enter the new executable path: " \
    "새 실행파일 경로를 입력하세요: "

define_text \
    "executable_changed" \
    "Executable path changed." \
    "실행 경로가 변경되었습니다."

define_text \
    "new_exec_options_prompt" \
    "Enter additional execution options (current: %s; Enter to clear; %%u is automatic): " \
    "추가 실행 옵션을 입력하세요 (현재: %s, Enter 시 제거, %%u 자동 추가): "

define_text \
    "exec_options_changed" \
    "Execution options changed." \
    "실행 옵션이 변경되었습니다."

define_text \
    "no_options" \
    "none" \
    "없음"

define_text \
    "invalid_executable" \
    "Invalid executable path." \
    "유효하지 않은 파일 경로입니다."

define_text \
    "icon_changed" \
    "Icon changed." \
    "아이콘이 변경되었습니다."

define_text \
    "terminal_changed" \
    "Terminal mode changed to '%s'." \
    "터미널 실행 여부가 '%s'(으)로 변경되었습니다."

define_text \
    "changes_saved" \
    "Changes saved!" \
    "수정 사항이 저장되었습니다!"

# Deletion, list, and main menu text

define_text \
    "delete_title" \
    "3. Delete an App Shortcut" \
    "3. 등록된 앱 단축아이콘 삭제"

define_text \
    "no_apps_to_delete" \
    "There are no shortcuts to delete." \
    "삭제할 단축아이콘이 없습니다."

define_text \
    "delete_app_prompt" \
    "Choose an app to delete (1-%s, cancel: 0): " \
    "삭제할 앱의 번호를 입력하세요 (1-%s, 취소: 0): "

define_text \
    "deletion_cancelled" \
    "Deletion cancelled." \
    "삭제를 취소했습니다."

define_text \
    "delete_confirmation" \
    "Delete the '%s' (%s) shortcut?" \
    "정말로 '%s' (%s) 단축아이콘을 삭제하시겠습니까?"

define_text \
    "confirmation_prompt" \
    "Confirm (y/N): " \
    "확인 (y/N): "

define_text \
    "removed_from_menu" \
    "Removed from the application menu (%s)." \
    "애플리케이션 메뉴(%s)에서 삭제되었습니다."

define_text \
    "removed_from_desktop" \
    "Removed from the Desktop (%s)." \
    "바탕화면(%s)에서도 삭제되었습니다."

define_text \
    "deletion_complete" \
    "'%s' deleted!" \
    "'%s' 삭제 완료!"

define_text \
    "view_title" \
    "4. View Registered App Shortcuts" \
    "4. 등록된 앱 단축아이콘 목록 보기"

define_text \
    "main_prompt" \
    "Choose an action:" \
    "원하시는 작업을 선택하세요:"

define_text \
    "menu_register" \
    "Register a new executable shortcut" \
    "새 실행파일 단축아이콘 등록"

define_text \
    "menu_edit" \
    "Edit a registered app shortcut" \
    "등록된 앱 단축아이콘 수정"

define_text \
    "menu_delete" \
    "Delete a registered app shortcut" \
    "등록된 앱 단축아이콘 삭제"

define_text \
    "menu_list" \
    "View all registered apps" \
    "등록된 앱 목록 전체 보기"

define_text \
    "menu_exit" \
    "Exit" \
    "종료"

define_text \
    "main_choice_prompt" \
    "Select (0-4): " \
    "선택 (0-4): "

define_text \
    "goodbye" \
    "Exiting GNOME Shortcut Manager. Have a great day!" \
    "그놈 단축 아이콘 관리자를 종료합니다. 좋은 하루 되세요!"

# Path configuration
APPS_DIR="$HOME/.local/share/applications"
DESKTOP_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"

# Ensure required directories exist
mkdir -p "$APPS_DIR"

# System icon descriptions

define_text \
    "icon.application-x-executable" \
    "Default executable icon" \
    "실행 파일 기본 아이콘"

define_text \
    "icon.utilities-terminal" \
    "Terminal / console application" \
    "터미널 / 콘솔 응용프로그램"

define_text \
    "icon.preferences-system" \
    "System settings / control panel" \
    "시스템 설정 / 제어판"

define_text \
    "icon.system-run" \
    "Run command / utility" \
    "실행 / 유틸리티 도구"

define_text \
    "icon.emblem-favorite" \
    "Favorite / star" \
    "즐겨찾기 / 별 모양"

define_text \
    "icon.applications-other" \
    "Other applications" \
    "기타 프로그램"

define_text \
    "icon.applications-accessories" \
    "Accessories" \
    "보조 프로그램"

define_text \
    "icon.applications-games" \
    "Games" \
    "게임 애플리케이션"

define_text \
    "icon.applications-internet" \
    "Internet / web browser" \
    "인터넷 / 웹 브라우저"

define_text \
    "icon.applications-multimedia" \
    "Multimedia / media player" \
    "멀티미디어 / 미디어 플레이어"

define_text \
    "icon.applications-office" \
    "Office / document tools" \
    "오피스 / 문서 도구"

define_text \
    "icon.applications-system" \
    "System tools" \
    "시스템 도구"

define_text \
    "icon.applications-development" \
    "Development / programming tools" \
    "개발 / 프로그래밍 도구"

define_text \
    "icon.applications-engineering" \
    "Engineering / design tools" \
    "엔지니어링 / 설계 도구"

define_text \
    "icon.applications-mathematics" \
    "Education / mathematics" \
    "교육 / 수학 학습 프로그램"

define_text \
    "icon.applications-utilities" \
    "General utilities" \
    "일반 유틸리티 모음"

define_text \
    "icon.tweaks-app" \
    "Tweaks / customization" \
    "트윅 / 맞춤 설정"

define_text \
    "icon.system-search" \
    "Search / navigation" \
    "검색 / 탐색 도구"

define_text \
    "icon.accessories-calculator" \
    "Calculator / mathematics" \
    "계산기 / 수학 유틸리티"

define_text \
    "icon.accessories-text-editor" \
    "Text editor / notes" \
    "텍스트 편집기 / 메모장"

define_text \
    "icon.accessories-character-map" \
    "Character map / symbols" \
    "문자표 / 특수문자 도구"

define_text \
    "icon.accessories-dictionary" \
    "Dictionary / language tools" \
    "사전 / 언어 도구"

define_text \
    "icon.application-x-compressed-tar" \
    "Compression / archive manager" \
    "압축 / 아카이브 관리"

define_text \
    "icon.utilities-system-monitor" \
    "System monitor / performance" \
    "시스템 모니터 / 성능 확인"

define_text \
    "icon.log-viewer-app" \
    "Logs / history viewer" \
    "로그 / 기록 확인"

define_text \
    "icon.disk-utility-app" \
    "Disk / storage utility" \
    "디스크 관리 / 저장장치 도구"

define_text \
    "icon.document-new" \
    "New document / writing" \
    "새 문서 / 문서 작성"

define_text \
    "icon.x-office-document" \
    "Word processor / document" \
    "워드프로세서 / 일반 문서"

define_text \
    "icon.x-office-spreadsheet" \
    "Spreadsheet / calculations" \
    "스프레드시트 / 표 계산"

define_text \
    "icon.x-office-presentation" \
    "Presentation / slides" \
    "프레젠테이션 / 슬라이드"

define_text \
    "icon.application-pdf" \
    "PDF document / viewer" \
    "PDF 문서 / 뷰어"

define_text \
    "icon.network-server" \
    "Network / server tools" \
    "네트워크 / 서버 도구"

define_text \
    "icon.network-wireless" \
    "Wireless network / Wi-Fi" \
    "무선 네트워크 / Wi-Fi"

define_text \
    "icon.network-wired" \
    "Wired network / Ethernet" \
    "유선 네트워크 / 이더넷"

define_text \
    "icon.network-vpn" \
    "VPN / secure network" \
    "VPN / 보안 네트워크"

define_text \
    "icon.network-workgroup" \
    "Network group / sharing" \
    "네트워크 그룹 / 공유"

define_text \
    "icon.web-browser" \
    "Web browser / web app" \
    "웹 브라우저 / 웹 애플리케이션"

define_text \
    "icon.internet-mail" \
    "Email / mail client" \
    "이메일 / 메일 클라이언트"

define_text \
    "icon.applications-chat" \
    "Messenger / chat app" \
    "메신저 / 채팅 응용프로그램"

define_text \
    "icon.bluetooth-active" \
    "Bluetooth / wireless device" \
    "블루투스 / 무선 장치"

define_text \
    "icon.mark-location" \
    "Map / location tool" \
    "지도 / 위치 기반 도구"

define_text \
    "icon.drive-harddisk" \
    "Disk / hard drive" \
    "디스크 / 하드 드라이브"

define_text \
    "icon.drive-removable-media" \
    "External disk / removable storage" \
    "외장 디스크 / 이동식 저장장치"

define_text \
    "icon.media-flash" \
    "USB flash storage" \
    "USB 메모리 / 플래시 저장장치"

define_text \
    "icon.folder-remote" \
    "Remote / cloud folder" \
    "원격 / 클라우드 폴더"

define_text \
    "icon.folder-documents" \
    "Documents folder / management" \
    "문서 폴더 / 문서 관리"

define_text \
    "icon.folder-download" \
    "Downloads / receiving files" \
    "다운로드 / 파일 받기"

define_text \
    "icon.folder-music" \
    "Music folder / audio collection" \
    "음악 폴더 / 오디오 모음"

define_text \
    "icon.folder-pictures" \
    "Pictures folder / image collection" \
    "사진 폴더 / 이미지 모음"

define_text \
    "icon.folder-videos" \
    "Videos folder / video collection" \
    "비디오 폴더 / 영상 모음"

define_text \
    "icon.system-file-manager" \
    "File manager / browser" \
    "파일 관리자 / 탐색기"

define_text \
    "icon.applications-graphics" \
    "Graphics / image editor" \
    "그래픽 / 이미지 편집기"

define_text \
    "icon.camera-photo" \
    "Camera / photography" \
    "카메라 / 사진 촬영"

define_text \
    "icon.camera-video" \
    "Video camera / recording" \
    "비디오 카메라 / 영상 촬영"

define_text \
    "icon.video-display" \
    "Video / screen playback" \
    "영상 / 화면 재생"

define_text \
    "icon.audio-player" \
    "Music / audio player" \
    "음악 / 오디오 플레이어"

define_text \
    "icon.audio-headphones" \
    "Headphones / personal audio" \
    "헤드폰 / 개인 오디오"

define_text \
    "icon.audio-speakers" \
    "Speakers / audio output" \
    "스피커 / 오디오 출력"

define_text \
    "icon.audio-input-microphone" \
    "Microphone / audio input" \
    "마이크 / 오디오 입력"

define_text \
    "icon.help-browser" \
    "Help / documentation browser" \
    "도움말 / 문서 브라우저"

define_text \
    "icon.user-desktop" \
    "Desktop utility" \
    "데스크톱 유틸리티"

define_text \
    "icon.emblem-system" \
    "System emblem" \
    "시스템 엠블럼"

define_text \
    "icon.applications-science" \
    "Science / education tools" \
    "과학 / 교육 도구"

define_text \
    "icon.preferences-desktop-wallpaper" \
    "Wallpaper / theme settings" \
    "배경화면 / 테마 설정"

define_text \
    "icon.security-high" \
    "Security / encryption tools" \
    "보안 / 암호화 도구"

define_text \
    "icon.system-lock-screen" \
    "Screen lock / security" \
    "화면 잠금 / 보안"

define_text \
    "icon.dialog-password" \
    "Password / authentication" \
    "비밀번호 / 인증 도구"

define_text \
    "icon.system-users" \
    "Users / account management" \
    "사용자 / 계정 관리"

define_text \
    "icon.computer" \
    "Computer / workstation" \
    "컴퓨터 / 워크스테이션"

define_text \
    "icon.preferences-desktop-display" \
    "Monitor / display settings" \
    "모니터 / 디스플레이 설정"

define_text \
    "icon.input-keyboard" \
    "Keyboard / input tools" \
    "키보드 / 입력 도구"

define_text \
    "icon.input-mouse" \
    "Mouse / pointing device" \
    "마우스 / 포인팅 장치"

define_text \
    "icon.input-gaming" \
    "Game controller / input device" \
    "게임 컨트롤러 / 입력 장치"

define_text \
    "icon.printer" \
    "Printer / printing tools" \
    "프린터 / 인쇄 도구"

define_text \
    "icon.scanner" \
    "Scanner / document scanning" \
    "스캐너 / 문서 스캔"

define_text \
    "icon.battery-good" \
    "Battery / power management" \
    "배터리 / 전원 관리"

define_text \
    "icon.preferences-system-time" \
    "Clock / date and time" \
    "시계 / 날짜 및 시간"

define_text \
    "icon.x-office-calendar" \
    "Calendar / scheduling" \
    "달력 / 일정 관리"

define_text \
    "icon.weather-clear" \
    "Weather / forecast" \
    "날씨 / 기상 정보"

define_text \
    "icon.system-software-install" \
    "Software installation / packages" \
    "소프트웨어 설치 / 패키지"

define_text \
    "icon.system-software-update" \
    "Software updates" \
    "소프트웨어 업데이트"

define_text \
    "icon.package-x-generic" \
    "Package / distribution file" \
    "패키지 / 배포 파일"

# 82 system icons. Descriptions are resolved from icon.<name> text IDs.
# Names follow the Freedesktop convention and are commonly provided by Ubuntu
# and GNOME themes. Their appearance can vary with the installed icon theme.
SYSTEM_ICONS=(
    # General application categories
    "application-x-executable" "utilities-terminal" "preferences-system"
    "system-run" "emblem-favorite" "applications-other"
    "applications-accessories" "applications-games" "applications-internet"
    "applications-multimedia" "applications-office" "applications-system"
    "applications-development" "applications-engineering"
    "applications-mathematics" "applications-utilities"

    # Tools, editing, and documents
    "tweaks-app" "system-search" "accessories-calculator"
    "accessories-text-editor" "accessories-character-map"
    "accessories-dictionary" "application-x-compressed-tar"
    "utilities-system-monitor" "log-viewer-app" "disk-utility-app"
    "document-new" "x-office-document" "x-office-spreadsheet"
    "x-office-presentation" "application-pdf"

    # Internet, communications, and location
    "network-server" "network-wireless" "network-wired" "network-vpn"
    "network-workgroup" "web-browser" "internet-mail" "applications-chat"
    "bluetooth-active" "mark-location"

    # Files, folders, and storage
    "drive-harddisk" "drive-removable-media" "media-flash" "folder-remote"
    "folder-documents" "folder-download" "folder-music" "folder-pictures"
    "folder-videos" "system-file-manager"

    # Multimedia and graphics
    "applications-graphics" "camera-photo" "camera-video" "video-display"
    "audio-player" "audio-headphones" "audio-speakers"
    "audio-input-microphone"

    # System, hardware, and security
    "help-browser" "user-desktop" "emblem-system" "applications-science"
    "preferences-desktop-wallpaper" "security-high" "system-lock-screen"
    "dialog-password" "system-users" "computer"
    "preferences-desktop-display" "input-keyboard" "input-mouse"
    "input-gaming" "printer" "scanner" "battery-good"
    "preferences-system-time" "x-office-calendar" "weather-clear"
    "system-software-install" "system-software-update" "package-x-generic"
)

# ------------------------------------------------------------------------------
# Display helpers
# ------------------------------------------------------------------------------
print_header() {
    local title
    title="$(t app_title)"
    clear
    echo -e "${CYAN}${BOLD}======================================================${NC}"
    printf "${CYAN}${BOLD}%*s${NC}\n" $((27 + ${#title} / 2)) "$title"
    echo -e "${CYAN}${BOLD}======================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✔ $1${NC}" >&2
}

print_error() {
    echo -e "${RED}✘ $1${NC}" >&2
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}" >&2
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}" >&2
}

pause_prompt() {
    echo "" >&2
    read -rp "$(t pause_prompt)" key >&2
}

# Return only the executable portion of an Exec value. Shortcuts created by
# this manager quote the executable path, including paths that contain spaces.
extract_executable_path() {
    local exec_value="$1"
    if [[ "$exec_value" == \"* ]]; then
        exec_value="${exec_value#\"}"
        printf '%s\n' "${exec_value%%\"*}"
    else
        printf '%s\n' "${exec_value%% *}"
    fi
}

# Return the arguments after the executable and hide the automatically managed
# trailing %u field code from the options editor.
extract_execution_options() {
    local exec_value="$1"
    if [[ "$exec_value" == \"* ]]; then
        exec_value="${exec_value#\"}"
        if [[ "$exec_value" == *\"* ]]; then
            exec_value="${exec_value#*\"}"
        else
            exec_value=""
        fi
    elif [[ "$exec_value" == *" "* ]]; then
        exec_value="${exec_value#* }"
    else
        exec_value=""
    fi

    exec_value="${exec_value#${exec_value%%[![:space:]]*}}"
    exec_value="${exec_value%${exec_value##*[![:space:]]}}"
    if [ "$exec_value" = "%u" ]; then
        exec_value=""
    elif [[ "$exec_value" == *" %u" ]]; then
        exec_value="${exec_value% %u}"
    fi

    printf '%s\n' "$exec_value"
}

# Retain GNOME's single-URI field code by default. Do not add %u when another
# file/URI field code was supplied explicitly.
ensure_exec_field_code() {
    local exec_value="$1"
    if ! [[ " $exec_value " =~ [[:space:]]%[fFuU][[:space:]] ]]; then
        exec_value+=" %u"
    fi

    printf '%s\n' "$exec_value"
}

build_exec_command() {
    local exec_path="$1"
    local exec_options="$2"
    local exec_value="\"$exec_path\""

    if [ -n "$exec_options" ]; then
        exec_value+=" $exec_options"
    fi

    ensure_exec_field_code "$exec_value"
}

# ------------------------------------------------------------------------------
# Shortcut trust settings and desktop cache refresh
# ------------------------------------------------------------------------------
apply_file_trust() {
    local target_file="$1"
    [ -z "$target_file" ] || [ ! -f "$target_file" ] && return 0
    
    chmod +x "$target_file" 2>/dev/null
    if command -v gio &>/dev/null; then
        gio trust "$target_file" &>/dev/null
        gio set "$target_file" metadata::trusted true &>/dev/null
        gio set "$target_file" metadata::trusted yes &>/dev/null
    fi
    touch "$target_file" 2>/dev/null
}

refresh_desktop_system() {
    # Refresh the GNOME application database.
    if command -v update-desktop-database &>/dev/null; then
        update-desktop-database "$APPS_DIR" &>/dev/null
    fi

    # Refresh the GTK icon cache.
    if command -v gtk-update-icon-cache &>/dev/null; then
        [ -d "$HOME/.local/share/icons" ] && gtk-update-icon-cache -f -t "$HOME/.local/share/icons" &>/dev/null
    fi

    # Trigger inotify events so GNOME Shell and DING notice changes promptly.
    touch "$APPS_DIR" 2>/dev/null
    [ -d "$DESKTOP_DIR" ] && touch "$DESKTOP_DIR" 2>/dev/null
}

# ------------------------------------------------------------------------------
# Icon discovery and selection (only the selected icon is written to stdout)
# ------------------------------------------------------------------------------
select_icon() {
    local exec_path="$1"
    local selected_icon=""
    local exec_dir=""

    if [ -n "$exec_path" ] && [ -e "$exec_path" ]; then
        if [ -d "$exec_path" ]; then
            exec_dir="$exec_path"
        else
            exec_dir="$(dirname "$exec_path")"
        fi
    fi

    echo -e "\n${BOLD}[$(t icon_setting)]${NC}" >&2

    # Search for image files near the executable.
    local nearby_icons=()
    if [ -n "$exec_dir" ] && [ -d "$exec_dir" ]; then
        print_info "$(t searching_nearby)"
        while IFS= read -r -d '' file; do
            nearby_icons+=("$file")
        done < <(find "$exec_dir" -maxdepth 3 \( -name "*.png" -o -name "*.svg" -o -name "*.ico" -o -name "*.xpm" -o -name "*.jpg" -o -name "*.jpeg" \) -print0 2>/dev/null)
    fi

    # Offer images detected near the executable first.
    if [ ${#nearby_icons[@]} -gt 0 ]; then
        echo -e "${GREEN}★ $(t detected_icons "${#nearby_icons[@]}")${NC}" >&2
        local i=1
        for icon_file in "${nearby_icons[@]}"; do
            echo "  [$i] $icon_file" >&2
            ((i++))
            if [ $i -gt 10 ]; then
                printf "  %s\n" "$(t icons_omitted "$(( ${#nearby_icons[@]} - 10 ))")" >&2
                break
            fi
        done
        echo "  $(t choose_other_icon)" >&2
        echo "" >&2

        read -rp "$(t detected_icon_prompt "${#nearby_icons[@]}")" icon_choice >&2
        if [[ "$icon_choice" =~ ^[0-9]+$ ]] && [ "$icon_choice" -ge 1 ] && [ "$icon_choice" -le "${#nearby_icons[@]}" ]; then
            selected_icon="${nearby_icons[$((icon_choice-1))]}"
            selected_icon="$(realpath "$selected_icon" 2>/dev/null || echo "$selected_icon")"
            chmod a+r "$selected_icon" 2>/dev/null
            print_success "$(t selected_icon "$selected_icon")"
            echo "$selected_icon"
            return 0
        fi
    else
        print_warning "$(t no_nearby_icons)"
    fi

    # Fall back to a system icon or a custom path.
    echo -e "\n${BOLD}$(t icon_method)${NC}" >&2
    local total_icons="${#SYSTEM_ICONS[@]}"
    echo "  1) $(t choose_system_icon "$total_icons")" >&2
    echo "  2) $(t custom_icon_option)" >&2
    read -rp "$(t method_prompt)" mode_choice >&2
    mode_choice="${mode_choice:-1}"

    if [ "$mode_choice" = "2" ]; then
        while true; do
            read -rp "$(t custom_icon_prompt)" custom_icon >&2
            # Remove pasted quote characters from the path.
            custom_icon="${custom_icon//\'/}"
            custom_icon="${custom_icon//\"/}"
            if [ -f "$custom_icon" ]; then
                selected_icon="$(realpath "$custom_icon" 2>/dev/null || echo "$custom_icon")"
                chmod a+r "$selected_icon" 2>/dev/null
                break
            else
                print_error "$(t invalid_icon_file)"
            fi
        done
    else
        echo -e "\n${BOLD}--- $(t system_icon_list "$total_icons") ---${NC}" >&2
        local idx=1
        for item in "${SYSTEM_ICONS[@]}"; do
            local name="$item"
            local desc
            desc="$(t "icon.${name}")"
            printf "  %2d) %-28s - %s\n" "$idx" "$name" "$desc" >&2
            ((idx++))
        done
        echo "" >&2
        while true; do
            read -rp "$(t system_icon_prompt "$total_icons")" sys_idx >&2
            if [[ "$sys_idx" =~ ^[0-9]+$ ]] && [ "$sys_idx" -ge 1 ] && [ "$sys_idx" -le "$total_icons" ]; then
                local chosen_item="${SYSTEM_ICONS[$((sys_idx-1))]}"
                selected_icon="$chosen_item"
                print_success "$(t selected_system_icon "$selected_icon")"
                break
            else
                print_error "$(t range_error 1 "$total_icons")"
            fi
        done
    fi

    echo "$selected_icon"
}

# ------------------------------------------------------------------------------
# Register an app shortcut
# ------------------------------------------------------------------------------
register_app() {
    print_header
    echo -e "${BOLD}[$(t register_title)]${NC}\n"

    # Read and validate the executable path.
    local exec_path=""
    while true; do
        read -rp "$(t executable_prompt)" raw_input
        if [ "$raw_input" = "q" ] || [ "$raw_input" = "Q" ]; then
            print_info "$(t registration_cancelled)"
            pause_prompt
            return 0
        fi

        # Remove pasted quote characters from the path.
        exec_path="${raw_input//\'/}"
        exec_path="${exec_path//\"/}"

        if [ -z "$exec_path" ]; then
            print_error "$(t path_required)"
            continue
        fi

        if [ ! -e "$exec_path" ]; then
            print_error "$(t path_not_found "$exec_path")"
            continue
        fi

        if [ -d "$exec_path" ]; then
            print_error "$(t path_is_directory)"
            continue
        fi

        # Offer to add execute permission when needed.
        if [ ! -x "$exec_path" ]; then
            print_warning "$(t no_execute_permission)"
            read -rp "$(t grant_execute_permission)" chmod_ans
            chmod_ans="${chmod_ans:-Y}"
            if [[ "$chmod_ans" =~ ^[Yy]$ ]]; then
                chmod +x "$exec_path"
                print_success "$(t execute_permission_added)"
            else
                print_error "$(t execute_permission_warning)"
            fi
        fi

        break
    done

    # Normalize to an absolute path.
    exec_path="$(realpath "$exec_path")"
    print_success "$(t confirmed_executable "$exec_path")"

    # Read optional command-line arguments separately from the executable path.
    # %u is appended later unless another file/URI field code is supplied.
    local exec_options=""
    read -rp "$(t execution_options_prompt)" exec_options
    local exec_command
    exec_command="$(build_exec_command "$exec_path" "$exec_options")"

    # Suggest a default app name based on the file name.
    local default_name
    default_name="$(basename "$exec_path")"
    default_name="${default_name%.*}"
    default_name="${default_name//[-_]/ }"
    default_name="$(echo "$default_name" | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2); print}')"

    echo ""
    read -rp "$(t app_name_prompt "$default_name")" app_name
    app_name="${app_name:-$default_name}"

    # Select an icon.
    local icon_path
    icon_path="$(select_icon "$exec_path")"

    # Configure terminal mode.
    echo ""
    read -rp "$(t terminal_prompt)" term_ans
    local terminal_val="false"
    if [[ "$term_ans" =~ ^[Yy]$ ]]; then
        terminal_val="true"
    fi

    # Read an optional description.
    read -rp "$(t comment_prompt)" comment_input
    comment_input="${comment_input:-$app_name Application}"

    # Select a desktop-entry category.
    echo -e "\n${BOLD}$(t category_title)${NC}"
    echo "  1) $(t category_utility)"
    echo "  2) $(t category_development)"
    echo "  3) $(t category_game)"
    echo "  4) $(t category_network)"
    echo "  5) $(t category_multimedia)"
    echo "  6) $(t category_office)"
    echo "  7) $(t category_system)"
    read -rp "$(t category_prompt)" cat_choice
    local category_val="Utility;"
    case "$cat_choice" in
        2) category_val="Development;" ;;
        3) category_val="Game;" ;;
        4) category_val="Network;" ;;
        5) category_val="AudioVideo;" ;;
        6) category_val="Office;" ;;
        7) category_val="System;" ;;
        *) category_val="Utility;" ;;
    esac

    # Optionally copy the shortcut to the desktop.
    read -rp "$(t desktop_prompt)" desktop_ans
    desktop_ans="${desktop_ans:-Y}"

    # Create the .desktop file.
    local file_id
    file_id="$(echo "$app_name" | tr '[:upper:]' '[:lower:]' | sed -e 's/[^a-z0-9]/-/g' -e 's/-\{2,\}/-/g' -e 's/^-//' -e 's/-$//')"
    [ -z "$file_id" ] && file_id="app-$RANDOM"
    
    local desktop_filename="${file_id}.desktop"
    local target_desktop_file="$APPS_DIR/$desktop_filename"

    cat <<EOF > "$target_desktop_file"
[Desktop Entry]
Version=1.0
Type=Application
Name=$app_name
Comment=$comment_input
Exec=$exec_command
Icon=$icon_path
Terminal=$terminal_val
Categories=$category_val
StartupNotify=true
X-Created-By=shortcut-manager
EOF

    apply_file_trust "$target_desktop_file"

    print_success "$(t shortcut_created "$target_desktop_file")"

    # Copy the shortcut to the desktop when requested.
    if [[ "$desktop_ans" =~ ^[Yy]$ ]]; then
        if [ -d "$DESKTOP_DIR" ]; then
            cp "$target_desktop_file" "$DESKTOP_DIR/$desktop_filename"
            apply_file_trust "$DESKTOP_DIR/$desktop_filename"
            print_success "$(t desktop_created "$DESKTOP_DIR")"
        fi
    fi

    # Refresh GNOME databases, caches, and filesystem events.
    refresh_desktop_system

    echo -e "\n${GREEN}${BOLD}✔ $(t registration_complete "$app_name")${NC}"
    pause_prompt
}

# ------------------------------------------------------------------------------
# Registered app list helper
# ------------------------------------------------------------------------------
display_registered_apps() {
    local desktop_files=()
    while IFS= read -r -d '' f; do
        desktop_files+=("$f")
    done < <(find "$APPS_DIR" -maxdepth 1 -name "*.desktop" -print0 2>/dev/null)

    if [ ${#desktop_files[@]} -eq 0 ]; then
        print_warning "$(t no_registered_apps "$APPS_DIR")"
        return 1
    fi

    echo -e "${BOLD}--- $(t registered_apps "$APPS_DIR") ---${NC}\n"
    local idx=1
    for dfile in "${desktop_files[@]}"; do
        local name
        local exec_cmd
        local icon_info
        local manager_tag=""

        name="$(grep -m 1 "^Name=" "$dfile" | cut -d'=' -f2-)"
        exec_cmd="$(grep -m 1 "^Exec=" "$dfile" | cut -d'=' -f2-)"
        icon_info="$(grep -m 1 "^Icon=" "$dfile" | cut -d'=' -f2-)"
        
        if grep -q "^X-Created-By=shortcut-manager" "$dfile" 2>/dev/null; then
            manager_tag="${CYAN}[$(t manager_created)]${NC}"
        fi

        printf "  %2d) %-25s %b\n" "$idx" "${name:-$(t unknown)}" "$manager_tag"
        printf "      ├─ %s: %s\n" "$(t executable_label)" "$exec_cmd"
        printf "      └─ %s: %s\n\n" "$(t icon_label)" "$icon_info"
        ((idx++))
    done

    return 0
}

# ------------------------------------------------------------------------------
# Edit an app shortcut
# ------------------------------------------------------------------------------
edit_app() {
    print_header
    echo -e "${BOLD}[$(t edit_title)]${NC}\n"

    local desktop_files=()
    while IFS= read -r -d '' f; do
        desktop_files+=("$f")
    done < <(find "$APPS_DIR" -maxdepth 1 -name "*.desktop" -print0 2>/dev/null)

    if [ ${#desktop_files[@]} -eq 0 ]; then
        print_warning "$(t no_apps_to_edit)"
        pause_prompt
        return 0
    fi

    display_registered_apps
    local total=${#desktop_files[@]}

    read -rp "$(t edit_app_prompt "$total")" select_num
    if ! [[ "$select_num" =~ ^[0-9]+$ ]] || [ "$select_num" -lt 1 ] || [ "$select_num" -gt "$total" ]; then
        print_info "$(t edit_cancelled)"
        pause_prompt
        return 0
    fi

    local target_file="${desktop_files[$((select_num-1))]}"
    print_info "$(t selected_file "$(basename "$target_file")")"

    # Parse the existing desktop entry.
    local current_name
    local current_exec
    local current_exec_path
    local current_exec_options
    local current_icon
    local current_term

    current_name="$(grep -m 1 "^Name=" "$target_file" | cut -d'=' -f2-)"
    current_exec="$(grep -m 1 "^Exec=" "$target_file" | cut -d'=' -f2-)"
    current_icon="$(grep -m 1 "^Icon=" "$target_file" | cut -d'=' -f2-)"
    current_term="$(grep -m 1 "^Terminal=" "$target_file" | cut -d'=' -f2-)"
    current_term="${current_term:-false}"

    # Normalize older manager-created shortcuts when they are edited. The
    # corrected value is written only when the user chooses Save changes.
    if grep -q "^X-Created-By=shortcut-manager" "$target_file" 2>/dev/null; then
        current_exec="$(ensure_exec_field_code "$current_exec")"
    fi
    current_exec_path="$(extract_executable_path "$current_exec")"
    current_exec_options="$(extract_execution_options "$current_exec")"

    while true; do
        print_header
        echo -e "${BOLD}[$(t editing_app "$current_name")]${NC}"
        echo -e " $(t file_path "$target_file")\n"
        echo "  1) $(t edit_name "$current_name")"
        echo "  2) $(t edit_executable "$current_exec_path")"
        echo "  3) $(t edit_exec_options "${current_exec_options:-$(t no_options)}")"
        echo "  4) $(t edit_icon "$current_icon")"
        echo "  5) $(t edit_terminal "$current_term")"
        echo "  6) $(t save_changes)"
        echo "  0) $(t cancel_edit)"
        echo ""
        read -rp "$(t edit_item_prompt)" edit_choice

        case "$edit_choice" in
            1)
                read -rp "$(t new_name_prompt "$current_name")" new_name
                if [ -n "$new_name" ]; then
                    current_name="$new_name"
                    print_success "$(t name_changed)"
                fi
                sleep 1
                ;;
            2)
                read -rp "$(t new_executable_prompt)" raw_einput
                raw_einput="${raw_einput//\'/}"
                raw_einput="${raw_einput//\"/}"
                if [ -e "$raw_einput" ] && [ ! -d "$raw_einput" ]; then
                    current_exec_path="$(realpath "$raw_einput")"
                    current_exec="$(build_exec_command "$current_exec_path" "$current_exec_options")"
                    print_success "$(t executable_changed)"
                else
                    print_error "$(t invalid_executable)"
                fi
                sleep 1
                ;;
            3)
                read -rp "$(t new_exec_options_prompt "${current_exec_options:-$(t no_options)}")" current_exec_options
                current_exec="$(build_exec_command "$current_exec_path" "$current_exec_options")"
                print_success "$(t exec_options_changed)"
                sleep 1
                ;;
            4)
                local new_icon
                new_icon="$(select_icon "$current_exec_path")"
                if [ -n "$new_icon" ]; then
                    current_icon="$new_icon"
                    print_success "$(t icon_changed)"
                fi
                sleep 1
                ;;
            5)
                if [ "$current_term" = "true" ]; then
                    current_term="false"
                else
                    current_term="true"
                fi
                print_success "$(t terminal_changed "$current_term")"
                sleep 1
                ;;
            6)
                # Update the desktop entry.
                sed -i "s|^Name=.*|Name=$current_name|" "$target_file"
                sed -i "s|^Exec=.*|Exec=$current_exec|" "$target_file"
                sed -i "s|^Icon=.*|Icon=$current_icon|" "$target_file"
                sed -i "s|^Terminal=.*|Terminal=$current_term|" "$target_file"

                apply_file_trust "$target_file"

                # Synchronize an existing desktop copy.
                local base_filename
                base_filename="$(basename "$target_file")"
                if [ -f "$DESKTOP_DIR/$base_filename" ]; then
                    cp "$target_file" "$DESKTOP_DIR/$base_filename"
                    apply_file_trust "$DESKTOP_DIR/$base_filename"
                fi

                # Refresh desktop caches and events.
                refresh_desktop_system

                print_success "$(t changes_saved)"
                pause_prompt
                return 0
                ;;
            0)
                print_info "$(t edit_cancelled)"
                pause_prompt
                return 0
                ;;
            *)
                print_error "$(t invalid_number)"
                sleep 1
                ;;
        esac
    done
}

# ------------------------------------------------------------------------------
# Delete an app shortcut
# ------------------------------------------------------------------------------
delete_app() {
    print_header
    echo -e "${BOLD}[$(t delete_title)]${NC}\n"

    local desktop_files=()
    while IFS= read -r -d '' f; do
        desktop_files+=("$f")
    done < <(find "$APPS_DIR" -maxdepth 1 -name "*.desktop" -print0 2>/dev/null)

    if [ ${#desktop_files[@]} -eq 0 ]; then
        print_warning "$(t no_apps_to_delete)"
        pause_prompt
        return 0
    fi

    display_registered_apps
    local total=${#desktop_files[@]}

    read -rp "$(t delete_app_prompt "$total")" del_num
    if ! [[ "$del_num" =~ ^[0-9]+$ ]] || [ "$del_num" -lt 1 ] || [ "$del_num" -gt "$total" ]; then
        print_info "$(t deletion_cancelled)"
        pause_prompt
        return 0
    fi

    local target_file="${desktop_files[$((del_num-1))]}"
    local app_name
    app_name="$(grep -m 1 "^Name=" "$target_file" | cut -d'=' -f2-)"
    local base_filename
    base_filename="$(basename "$target_file")"

    echo ""
    print_warning "$(t delete_confirmation "$app_name" "$base_filename")"
    read -rp "$(t confirmation_prompt)" confirm_del

    if [[ "$confirm_del" =~ ^[Yy]$ ]]; then
        rm -f "$target_file"
        print_success "$(t removed_from_menu "$APPS_DIR")"

        if [ -f "$DESKTOP_DIR/$base_filename" ]; then
            rm -f "$DESKTOP_DIR/$base_filename"
            print_success "$(t removed_from_desktop "$DESKTOP_DIR")"
        fi

        refresh_desktop_system

        print_success "$(t deletion_complete "$app_name")"
    else
        print_info "$(t deletion_cancelled)"
    fi

    pause_prompt
}

# ------------------------------------------------------------------------------
# View registered app shortcuts
# ------------------------------------------------------------------------------
view_apps() {
    print_header
    echo -e "${BOLD}[$(t view_title)]${NC}\n"
    display_registered_apps
    pause_prompt
}

# ------------------------------------------------------------------------------
# Language selection
# ------------------------------------------------------------------------------
select_language() {
    clear
    echo "======================================================"
    echo "          ${TEXT["en.language_title"]} / ${TEXT["ko.language_title"]}"
    echo "======================================================"
    echo ""
    echo "  1) ${TEXT["en.language_english"]}"
    echo "  2) ${TEXT["ko.language_korean"]} (${TEXT["en.language_korean"]})"
    echo ""
    read -rp "${TEXT["en.language_prompt"]}" language_choice

    case "$language_choice" in
        2) APP_LANGUAGE="ko" ;;
        *) APP_LANGUAGE="en" ;;
    esac
}

# ------------------------------------------------------------------------------
# Main loop
# ------------------------------------------------------------------------------
main() {
    select_language

    while true; do
        print_header
        echo -e "${BOLD}$(t main_prompt)${NC}\n"
        echo "  1) $(t menu_register)"
        echo "  2) $(t menu_edit)"
        echo "  3) $(t menu_delete)"
        echo "  4) $(t menu_list)"
        echo "  0) $(t menu_exit)"
        echo ""
        read -rp "$(t main_choice_prompt)" main_choice

        case "$main_choice" in
            1) register_app ;;
            2) edit_app ;;
            3) delete_app ;;
            4) view_apps ;;
            0)
                echo -e "\n${GREEN}$(t goodbye)${NC}"
                exit 0
                ;;
            *)
                print_error "$(t invalid_number)"
                sleep 1
                ;;
        esac
    done
}

# Run the script.
main "$@"
