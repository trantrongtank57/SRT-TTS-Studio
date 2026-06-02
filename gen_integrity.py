import os, json, hashlib, sys

dist_dir = os.path.join('dist', 'SRT_TTS_Studio')

if not os.path.isdir(dist_dir):
    print('[ERROR] dist folder not found: ' + dist_dir)
    sys.exit(1)

# relative_path -> absolute_path pairs to hash
# Keys use forward slash so _check_integrity() can use os.path.normpath()
targets = [('SRT_TTS_Studio.exe', os.path.join(dist_dir, 'SRT_TTS_Studio.exe'))]

# Search root for .pyd
for fn in os.listdir(dist_dir):
    if fn.startswith('apppp_integrated') and fn.endswith('.pyd'):
        targets.append((fn, os.path.join(dist_dir, fn)))

# Also search _internal/ subdirectory (PyInstaller 6.x puts binaries here)
internal_dir = os.path.join(dist_dir, '_internal')
if os.path.isdir(internal_dir):
    for fn in os.listdir(internal_dir):
        if fn.startswith('apppp_integrated') and fn.endswith('.pyd'):
            rel_key = '_internal/' + fn
            targets.append((rel_key, os.path.join(internal_dir, fn)))

hashes = {}
for rel_key, fp in targets:
    if not os.path.exists(fp):
        print('  [SKIP] Not found: ' + fp)
        continue
    h = hashlib.sha256()
    with open(fp, 'rb') as fh:
        while True:
            chunk = fh.read(65536)
            if not chunk:
                break
            h.update(chunk)
    hashes[rel_key] = h.hexdigest()
    print('  Hashed: ' + rel_key + ' -> ' + h.hexdigest()[:16] + '...')

out = os.path.join(dist_dir, '.integrity')
with open(out, 'w') as f:
    json.dump(hashes, f, indent=2)

print('[OK] .integrity written with ' + str(len(hashes)) + ' entries.')
