# ShulkerPi

![HitCount](https://hits.dwyl.com/EnguerranVidal/ShulkerPi.svg?style=flat) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![GitHub watchers](https://badgen.net/github/watchers/EnguerranVidal/ShulkerPi/)](https://GitHub.com/EnguerranVidal/ShulkerPi/watchers/) [![GitHub stars](https://badgen.net/github/stars/EnguerranVidal/ShulkerPi)](https://GitHub.com/EnguerranVidal/ShulkerPi/stargazers/) [![GitHub commits](https://badgen.net/github/commits/EnguerranVidal/ShulkerPi)](https://github.com/EnguerranVidal/ShulkerPi/) [![GitHub branches](https://badgen.net/github/branches/EnguerranVidal/ShulkerPi)](https://github.com/EnguerranVidal/ShulkerPi/) [![wakatime](https://wakatime.com/badge/user/d1fb42e6-38e1-489b-a7b0-fa05747ea94a/project/018d27ae-4295-4e1c-ae4d-a11ecace9b70.svg)](https://wakatime.com/badge/user/d1fb42e6-38e1-489b-a7b0-fa05747ea94a/project/018d27ae-4295-4e1c-ae4d-a11ecace9b70) [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)


## ABOUT THE PROJECT
___
<div style="text-align: justify;">

This repository contains a Discord Bot whose goal is to manage a Minecraft server hosted from a Raspberry Pi computer in your living room. This bot can start, stop and reset the server using Bash scripts as well as provide useful information to its users by displaying the world seed, the server ip or even playing statistics.

Distributed under the MIT License. See **[LICENSE](https://github.com/EnguerranVidal/ShulkerPi/blob/main/LICENSE)** 
for more information.

</div>

## GETTING STARTED
___
### CREATING A BOT
1. You first need to create a Discord application and Bot with administrator permissions. You should follow the [Discord documentation](https://discord.com/developers/docs/intro) and then invite it to your Discord server through the OAuth2 panel on the developer portal.
2. You must copy the app token on a clipboard



### INSTALLATION
This process must be done on the Raspberry Pi containing the Minecraft server. You can do these commands from your home directory.
1. Cloning the Github Repository
```
git clone https://github.com/EnguerranVidal/ShulkerPi.git
```
2. Going in the Repository Directory
```
cd ShulkerPi
```
3. Creating PyEnv Environment
```
pyenv virtualenv 3.10 discordbot
pyenv local discordbot
```
4. Installing ShulkerPi Requirements
```
pip install -r requirements.txt
```

### RUNNING AT BOOT - CRONTAB

If you want your bot to run at boot from your Raspberry Pi, you must set the botStart.sh.

1. Firstly, open the crontab file :
```
sudo crontab -e
```

2. You can now add the following line at the end of the file with SHULKER_REPO being the directory of the ShulkerPi bot :
```
@reboot sudo /bin/bash SHULKER_REPO/scripts/botStart.sh
```

