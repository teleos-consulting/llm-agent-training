wsl --install
winget install -e --id Git.Git
winget install -e --id OpenJS.NodeJS
winget install -e --id Microsoft.VisualStudio.2022.Community
winget install -e --id Microsoft.VisualStudioCode
winget install -e --id Python.Python.3.13
winget install -e --id Rustlang.Rust.MSVC
winget install -e --id Docker.DockerDesktop
rustup toolchain install 1.81-x86_64-pc-windows-msvc
echo "Congratulations, comrade!"
