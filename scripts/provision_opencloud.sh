#!/usr/bin/env bash
# Provisioning script for OpenCloud on the PoC VM (R007-R014 vertical slice).
#
# This script performs the one-time, infrastructure-level setup that
# OpenCloudService intentionally does NOT do from within the Python
# application (principle of least privilege: the app never calls
# sudo/apt). Run it once, manually, as the target user (e.g. the PoC
# "training" account) on the target VM.
#
# What it does:
#   1. Installs the podman package (requires sudo).
#   2. Enables systemd lingering for the current user, so rootless
#      Podman containers survive the end of an SSH session.
#   3. Creates the persistent config/data directories used by
#      OpenCloudConfig.
#
# What it deliberately does NOT do:
#   - It does not run "opencloud init" (see docs/opencloud-service.md
#     for the documented, manual one-time bootstrap step).
#   - It does not pull the OpenCloud image or start any container —
#     that is OpenCloudService.install()'s job.
#
# Usage:
#   bash scripts/provision_opencloud.sh
#
# Idempotent: safe to re-run; already-satisfied steps are skipped.

set -euo pipefail

CONFIG_DIR="${HOME}/opencloud/opencloud-config"
DATA_DIR="${HOME}/opencloud/opencloud-data"

echo "==> Checking for podman..."
if command -v podman >/dev/null 2>&1; then
    echo "    podman is already installed: $(podman --version)"
else
    echo "    installing podman via apt (requires sudo)..."
    sudo apt-get update -qq
    sudo apt-get install -y -qq podman
    echo "    installed: $(podman --version)"
fi

echo "==> Checking systemd lingering for user $(whoami)..."
if [ "$(loginctl show-user "$(whoami)" -p Linger --value 2>/dev/null || echo no)" = "yes" ]; then
    echo "    lingering is already enabled."
else
    echo "    enabling lingering (requires sudo) so rootless containers"
    echo "    survive the end of an SSH session..."
    sudo loginctl enable-linger "$(whoami)"
fi

echo "==> Ensuring persistent directories exist..."
mkdir -p "${CONFIG_DIR}" "${DATA_DIR}"
echo "    config: ${CONFIG_DIR}"
echo "    data:   ${DATA_DIR}"

echo "==> Provisioning complete."
echo "Next steps (see docs/opencloud-service.md):"
echo "  1. Run 'opencloud init' once against these directories to"
echo "     generate the admin password and configuration."
echo "  2. Use OpenCloudService.install() to pull the image and start"
echo "     the container."
