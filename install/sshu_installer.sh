#!/bin/sh

set -e

#set sshu version
SSHU_VER="${SSHU_VER:-1.0.0}"

#Colors
WHITE="\033[0m" #white
RED="\033[1;31m" #red
GREEN="\033[1;32m" #green
YELLOW="\033[1;33m" #yellow

CURRENT_SHELL=${SHELL##*/}
SHELL_RC="$HOME/.${CURRENT_SHELL}rc"

log() {
	case "$1" in
		success)
			echo "$GREEN✔️ $2$WHITE"
			;;
		failure)
			echo "$RED❌ $2$WHITE"
			;;
		progress)
			echo "$YELLOW🚀 $2$WHITE"
			;;
	esac
}

if [ "$(id -u)" -ne 0 ]; then
	INSTALL_PATH="$HOME/.local/bin"
	log progress "Non-root user detected. Selecting ${INSTALL_PATH} as install path"
	UPDATE_RC="true"
else
	INSTALL_PATH="/usr/local/bin"
	log progress "Root user detected. Selecting ${INSTALL_PATH} as install path"
fi

log progress "Detecting os type"

unameOut=$(uname -s)
case "${unameOut}" in
    Linux*)   OS_TYPE="linux";;
    Darwin*)  OS_TYPE="mac";;
    *)        log failure "Unknown OS_TYPE ${unameOut} detected"; exit 1;;
esac

if [ "$OS_TYPE" = "linux" ]; then
	if ldd /bin/ls | grep -q gnu; then
		log progress "glibc detected"
		STD_LIB="-glibc"
	elif ldd /bin/ls | grep -q musl; then
		log progress "musl detected"
		STD_LIB="-musl"
	fi
else
	STD_LIB=""
fi

#Fetch sshu binary

TEMP_DIR=$(mktemp -d)
trap "rm -rf '$TEMP_DIR'" EXIT

curl -L "https://github.com/heinhtetzaw346/sshu/releases/download/${SSHU_VER}/sshu-${OS_TYPE}${STD_LIB}" -o "${TEMP_DIR}/sshu"

mkdir -p "${INSTALL_PATH}"
chmod +x "${TEMP_DIR}/sshu"
mv "${TEMP_DIR}/sshu" "${INSTALL_PATH}"

log success "Moved sshu binary to ${INSTALL_PATH}"

if [ "${UPDATE_RC:-false}" = "true" ]; then
	echo "$PATH" | grep -q "$HOME/.local/bin" || \
		echo "export PATH=\"$PATH:${INSTALL_PATH}\"" >> "${SHELL_RC}"
	log success "Added ${INSTALL_PATH} to ${SHELL_RC}. Try restarting the shell to access sshu"
fi

log success "SSHU Version ${SSHU_VER} installed successfully"
