"""CI helper: tweak godot/project.godot for the Android build (VRAM-compressed textures keep phone memory low)."""
import re, sys
p = sys.argv[1] if len(sys.argv) > 1 else 'godot/project.godot'
s = open(p).read()
s = s.replace('textures/canvas_textures/default_texture_filter=1',
              'textures/canvas_textures/default_texture_filter=1\ntextures/vram_compression/import_etc2_astc=true')
s += '''
[importer_defaults]

texture={
"compress/mode": 2,
"compress/high_quality": false,
"mipmaps/generate": false
}
'''
open(p, 'w').write(s)
print('mobile project settings applied')
