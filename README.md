-----
Author: Matthew DesEnfants (mdesenfants)
-----

# LLM Agent Tutorial

This will cover how to build agents from off-the-shelf large language models. We'll be using OpenAI's LLMs, but these same techniques work with Anthropic's Claude, Meta's Llama, and Deepseek's models as well.

## Installation Instructions

> This will take 15-20 minutes.

The project is intended to be used with Visual Studio Code, which offers versions for most operating systems. We'll also be using Dev Containers through Docker, ensuring that everything in here is running on a consistent development environment.

You can run these on your own operating system directly, but using a Docker container will provide some guarantees of success.

### Easy mode (Windows, 15-20 min)

Run this command from this project folder in your terminal in this directory.

```powershell
.\start.cmd
```

When tool installation is complete, open this folder/directory in Visual Studio Code. Look for the prompt asking you to open the directory in
a dev container. Agree to to so.

### Easy mode (Mac, 15-20 min)

Run these commands from your terminal...

```bash
chmod +x start.sh
./start.sh
```

When tool installation is complete, open this folder/directory in Visual Studio Code. Look for the prompt asking you to open the directory in
a dev container. Agree to to so.

When the project is reopened, open your terminal with `` command + ` ``

Everything should be installed and ready for you to start playing with your first agents and large language models.

### Top Gun Mode (Windows, 30-60 min)

> This can take an hour if you're pretty good at this stuff.

Download these developer tools:

- [Visual Studio Community 2022](https://visualstudio.microsoft.com/vs/)
- [Visual Studio Code](https://code.visualstudio.com/download)
- [Python 3.13+](https://www.python.org/downloads/)
- [Rust](https://www.rust-lang.org/tools/install)

Then in a terminal (like VS Code) run this command:
```bash
rustup toolchain install 1.81-x86_64-pc-windows-msvc
```

Once the above tools are installed, create a virtual environment in the base of this project.

This will make sure that you have a clean, tidy "workspace" for Python to do its thing.

```bash
python -m venv .venv
```

You can enter the virtual environment by running this command...

```bash
./venv/Scripts/activate
```

Get the python packages you'll need by going into the Apps directory and using `pip` to install them.

```bash
cd ./Apps
pip install -r requirements.txt
```

##

Your console prompt should change to have a little (.venv) in front of the input line, but nothing else should look different.

