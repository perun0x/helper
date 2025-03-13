#! /bin/bash

echo "$SSH_KEY" | base64 -d > ssh_key
chmod 600 ssh_key
echo "SSH key prepared successfully."