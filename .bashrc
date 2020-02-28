# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

# User specific aliases and functions
export PS1="
[\D{%F %T} \u@\h:\w ] "
export LANG=C

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
export M2_HOME=/opt/apache-maven-3.5.4
export PATH=${HOME}/.local/bin:${M2_HOME}/bin:${PATH}
export JAVA_HOME=$(dirname $(dirname $(readlink /etc/alternatives/java)))
export GO_HOME=$(dirname $(dirname $(which go)))
export GOPATH=${HOME}/go
export PATH=${GO_HOME}/bin:${JAVA_HOME}/bin:${PATH}

alias dockerclean='docker container stop $(docker container ls -aq) > /dev/null 2>&1 ; docker container rm $(docker container ls -aq) > /dev/null 2>&1 ; docker image rm -f $(docker images -q) > /dev/null 2>&1 ; docker volume rm $(docker volume ls -q) > /dev/null 2>&1 ; docker network rm $(docker network ls -q -f name=.*net) > /dev/null 2>&1'
alias dockerls='echo -e "\nContainers\n" ; docker container ls ; echo -e "\nImages\n" ; docker image ls ; echo -e "\nVolumes\n" ; docker volume ls ; echo -e "\nNetworks\n" ; docker network ls'
alias docker-compose='/usr/local/bin/docker-compose'
alias ddsclean='find . -name __pycache__ | sudo xargs rm -rf ; find . -name "*.log" | sudo xargs rm -f ; find . -name "*.log.[0-9]*" | sudo xargs rm -f' ; sudo rm -rf bluefiles/*
alias ls='ls --color=never'
alias dir='dir --color=never'
alias vdir='vdir --color=never'
alias grep='grep --color=never'
alias fgrep='fgrep --color=never'
alias egrep='egrep --color=never'
alias cls='clear ; echo -e "\e[3J"'
