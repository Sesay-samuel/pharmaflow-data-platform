
#!/usr/bin/env bash
set -euo pipefail

echo "Starting PharmaFlow EC2 Docker setup..."

# Install Docker on Amazon Linux 2023
sudo dnf install -y docker

# Start Docker and enable it after reboot
sudo systemctl enable --now docker

# Allow ec2-user to run Docker commands
sudo usermod -aG docker ec2-user

# Verify Docker installation
sudo docker --version
sudo systemctl is-active docker

echo "Docker installation completed."
echo "Reconnect your session to activate Docker group membership."
