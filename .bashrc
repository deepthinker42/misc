# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# User specific environment
if ! [[ "$PATH" =~ "$HOME/.local/bin:$HOME/bin:" ]]
then
    PATH="$HOME/.local/bin:$HOME/bin:$PATH"
fi
export PATH

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

# User specific aliases and functions

shopt -s histappend
export PROMPT_COMMAND="history -a; history -c; history -r; ${PROMPT_COMMAND}"

GIT_BRANCH_BLACK="0;30"
GIT_BRANCH_RED="0;31"
GIT_BRANCH_GREEN="0;32"
GIT_BRANCH_BROWN_ORANGE="0;33"
GIT_BRANCH_BLUE="0;34"
GIT_BRANCH_PURPLE="0;35"
GIT_BRANCH_CYAN="0;36"
GIT_BRANCH_LIGHT_GRAY="0;37"
GIT_BRANCH_DARK_GRAY="1;30"
GIT_BRANCH_LIGHT_RED="1;31"
GIT_BRANCH_LIGHT_GREEN="1;32"
GIT_BRANCH_YELLOW="1;33"
GIT_BRANCH_LIGHT_BLUE="1;34"
GIT_BRANCH_LIGHT_PURPLE="1;35"
GIT_BRANCH_LIGHT_CYAN="1;36"
GIT_BRANCH_WHITE="1;37"
export GIT_BRANCH_COLOR_ON="\[\033[${GIT_BRANCH_YELLOW}m\]"
export GIT_BRANCH_COLOR_OFF="\[\033[00m\]"

parse_git_branch() {
	git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/ (\1)/'
}
export PS1="\n[\D{%F %T} \h \u \w${GIT_BRANCH_COLOR_ON}\$(parse_git_branch)${GIT_BRANCH_COLOR_OFF}] "

export NVM_DIR="$HOME/.nvm"
#[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
#[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
#export M2_HOME=/opt/apache-maven-3.5.4
#export PATH=${HOME}/.local/bin:${M2_HOME}/bin:${PATH}
export JAVA_HOME=$(dirname $(dirname $(readlink /etc/alternatives/java)))
export GO_HOME=/usr/local/bin/go
export FLUTTER_HOME="$HOME/.local/share/flutter"
export ANDROID_STUDIO_HOME="$HOME/.local/share/android-studio"
export PATH=${ANDROID_STUDIO_HOME}/bin:${GO_HOME}/bin:${FLUTTER_HOME}/bin:${PATH}
export HISTSIZE=1000000
export HISTFILESIZE=1000000
export HISTCONTROL=ignoredups
export HISTIGNORE="subscription-manager register*"

alias cls='clear ; echo -e "\e[3J"'
alias dockerclean='docker container stop $(docker container ls -aq) > /dev/null 2>&1 ; docker container rm $(docker container ls -aq) > /dev/null 2>&1 ; docker image rm -f $(docker images -q) > /dev/null 2>&1 ; docker volume rm $(docker volume ls -q) > /dev/null 2>&1 ; docker network rm $(docker network ls -q -f name=.*net) > /dev/null 2>&1'
alias dockerls='echo -e "\nContainers\n" ; docker container ls ; echo -e "\nImages\n" ; docker image ls ; echo -e "\nVolumes\n" ; docker volume ls ; echo -e "\nNetworks\n" ; docker network ls'
alias docker-compose='/usr/local/bin/docker-compose'
alias filesin='git diff-tree --no-commit-id --name-only -r '
alias ls='ls --color=never'
alias dir='dir --color=never'
alias vdir='vdir --color=never'
alias grep='grep --color=never'
alias fgrep='fgrep --color=never'
alias egrep='egrep --color=never'
alias vpn='sudo openconnect --user=rgoodman --protocol=pulse -b -q sslgate.ticom-geo.com'
alias vpnd='sudo pkill openconnect'
alias vbox='sudo dpkg-reconfigure virtualbox-dkms && sudo dpkg-reconfigure $(dpkg -l | grep virtualbox-\[0-9\] | awk "{print \$2}") && sudo modprobe vboxdrv'

