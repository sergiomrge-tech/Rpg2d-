#!/bin/bash
# usage: tools/run.sh [timeout] [-- user args]   Imports (class_name/assets) then runs the Godot project headless-with-GL.
G=/opt/godot/Godot_v4.3-stable_linux.x86_64
cd "$(dirname "$0")/../godot"
TO=${1:-60}; shift
timeout 240 $G --headless --import > /tmp/import.log 2>&1
xvfb-run -a -s "-screen 0 1920x1080x24" timeout $TO $G --path . --rendering-driver opengl3 -- "$@" > /tmp/run.log 2>&1
grep -v -E "ALSA|audio|V-Sync|set_use_vsync|^\s*at: init_output|OpenGL API|Godot Engine v" /tmp/run.log | head -${LINES_MAX:-80}
