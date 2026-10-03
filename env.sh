#!/usr/bin/env bash

# Source this file to configure the current shell:
#   source ./env.sh
#
# When executed, it also works as a Python wrapper for VS Code/debugpy:
#   ./env.sh app.py

surpls_project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
surpls_system_python="/usr/bin/python3"
surpls_venv="$surpls_project_root/.venv"
surpls_requirements="$surpls_project_root/requirement.txt"
surpls_requirements_stamp="$surpls_venv/.requirement.sha256"
surpls_tk_lib="$surpls_project_root/.vscode/python3-tk/usr/lib"
surpls_tk_stdlib="$surpls_tk_lib/python3.12"
surpls_tk_dynload="$surpls_tk_stdlib/lib-dynload"

export SURPLS_PROJECT_ROOT="$surpls_project_root"
export PYTHONUNBUFFERED=1

surpls_has_requirements=false
if [[ -f "$surpls_requirements" ]]; then
    while IFS= read -r surpls_line; do
        surpls_line="${surpls_line#"${surpls_line%%[![:space:]]*}"}"
        if [[ -n "$surpls_line" && "$surpls_line" != \#* ]]; then
            surpls_has_requirements=true
            break
        fi
    done < "$surpls_requirements"
fi

if [[ "$surpls_has_requirements" == true && ! -x "$surpls_venv/bin/python" ]]; then
    if ! "$surpls_system_python" -m venv "$surpls_venv" 2>/dev/null; then
        # python3-venv (ensurepip) is missing: create the venv bare and fetch pip.
        rm -rf "$surpls_venv"
        if ! "$surpls_system_python" -m venv --without-pip "$surpls_venv" \
            || ! curl -fsSL https://bootstrap.pypa.io/get-pip.py \
                | "$surpls_venv/bin/python" - --quiet; then
            rm -rf "$surpls_venv"
            echo "Could not create .venv. Install it with: sudo apt install python3-venv" >&2
            if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
                exit 1
            fi
            return 1
        fi
    fi
fi

if [[ -x "$surpls_venv/bin/python" ]]; then
    surpls_python="$surpls_venv/bin/python"
    export VIRTUAL_ENV="$surpls_venv"
    export PATH="$surpls_venv/bin:$PATH"
else
    surpls_python="$surpls_system_python"
fi

if [[ "$surpls_has_requirements" == true ]]; then
    if ! "$surpls_python" -m pip --version >/dev/null 2>&1; then
        echo "pip is unavailable in .venv. Install it with: sudo apt install python3-venv python3-pip" >&2
        if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
            exit 1
        fi
        return 1
    fi

    surpls_requirements_hash="$(sha256sum "$surpls_requirements" | cut -d ' ' -f 1)"
    surpls_installed_hash=""
    if [[ -f "$surpls_requirements_stamp" ]]; then
        surpls_installed_hash="$(<"$surpls_requirements_stamp")"
    fi
    if [[ "$surpls_requirements_hash" != "$surpls_installed_hash" ]]; then
        echo "Installing dependencies from requirement.txt..."
        if ! "$surpls_python" -m pip install -r "$surpls_requirements"; then
            if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
                exit 1
            fi
            return 1
        fi
        printf '%s\n' "$surpls_requirements_hash" > "$surpls_requirements_stamp"
    fi
fi

if "$surpls_python" -c "import tkinter" >/dev/null 2>&1; then
    export PYTHONPATH="$surpls_project_root${PYTHONPATH:+:$PYTHONPATH}"
elif [[ -f "$surpls_tk_stdlib/tkinter/__init__.py" \
    && -f "$surpls_tk_dynload/_tkinter.cpython-312-x86_64-linux-gnu.so" ]]; then
    export PYTHONPATH="$surpls_tk_dynload:$surpls_tk_stdlib:$surpls_project_root${PYTHONPATH:+:$PYTHONPATH}"
    export LD_LIBRARY_PATH="$surpls_tk_lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
else
    echo "Tkinter is unavailable. Install it with: sudo apt install python3-tk" >&2
    if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
        exit 1
    fi
    return 1
fi

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    exec "$surpls_python" "$@"
fi

unset \
    surpls_project_root \
    surpls_system_python \
    surpls_python \
    surpls_venv \
    surpls_requirements \
    surpls_requirements_stamp \
    surpls_has_requirements \
    surpls_line \
    surpls_requirements_hash \
    surpls_installed_hash \
    surpls_tk_lib \
    surpls_tk_stdlib \
    surpls_tk_dynload
