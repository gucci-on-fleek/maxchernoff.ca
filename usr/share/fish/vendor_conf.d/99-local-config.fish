# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2026 Max Chernoff

# Configure some interactive fish shell settings system-wide.
if not status --is-interactive
    return
end

# Set the base colour scheme.
fish_config theme choose ayu 2>/dev/null || fish_config theme choose 'ayu Dark'
set --global fish_color_cwd cyan
set --global fish_color_host_remote $fish_color_host

# Set the user colour. Cases:
#
# Blue:        Personal account on my personal computer.
# Yellow:      Personal account on a server.
# Red:         Root account on a server.
# Reverse Red: Root account on my personal computer.
# Green:       All other cases.
if test (id --user --name) = "max"
    if systemd-detect-virt --quiet
        set --global fish_color_user --bold yellow
    else
        set --global fish_color_user --bold brblue
    end
else if test (id --user) = 0
    if systemd-detect-virt --quiet
        set --global fish_color_user --bold --dim red
    else
        set --global fish_color_user --bold --dim --reverse red
    end
else
    set --global fish_color_user --bold green
end

# Keybindings
bind \f 'clear && commandline -f repaint'
bind ctrl-h backward-kill-word

# Variables
set --export LC_COLLATE "C.UTF-8"

# Strace
set strace_exclude "$(echo "!\
        _llseek, \
        arch_prctl, \
        brk, \
        clock_gettime, \
        clock_gettime64, \
        close, \
        epoll_ctl, \
        epoll_pwait, \
        fcntl, \
        futex_waitv, \
        futex, \
        getrandom, \
        gettid, \
        ioctl, \
        lseek, \
        madvise, \
        mmap, \
        mmap2, \
        mprotect, \
        munmap, \
        nanosleep, \
        ppoll, \
        prctl, \
        pread64, \
        prlimit64, \
        pselect6, \
        read, \
        recvmsg, \
        rseq, \
        rt_sigaction, \
        rt_sigprocmask, \
        sched_yield, \
        set_robust_list, \
        set_tid_address, \
    " | tr -d '[:space:]')"

function strace
    command strace \
        --decode-fds='all' \
        --decode-pids='comm' \
        --follow-forks \
        --no-abbrev \
        --string-limit='65535' \
        --strings-in-hex='non-ascii-chars' \
        --trace=$strace_exclude \
        $argv
end

# Aliases
function ls
    set --local cmd "ls"
    for arg in $argv
        if test \( -e $arg \) -a ! \( -r $arg \)
            set --local cmd "sudo" "ls"
            break
        end
    end
    command $cmd \
        --classify \
        --color='auto' \
        --human-readable \
        --almost-all \
        --no-group \
        --dereference-command-line-symlink-to-dir \
        $argv
end

function watch
    command watch \
        --interval='0.5' \
        --color \
        --no-wrap \
        $argv
end

function ping
    command ping -O $argv
end

function grep
    command grep \
        --color='auto' \
        --perl-regexp \
        $argv
end

function rg
    command rg \
        --max-columns-preview \
        --max-columns='200' \
        --hidden \
        --glob='!.snapshots' \
        $argv
end

function rgo
    command rg \
        --no-filename \
        --no-line-number \
        --only-matching \
        $argv
end
