from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'src' / 'obsidian_writer.py'
text = path.read_text(encoding='utf-8')
start = text.find('## Actividades Recientes')
segment = text[start:start + 300]
print('SEGMENT_REPR:')
print(repr(segment))
new_text = text.replace('\\`\\`\\`', '```')
if new_text != text:
    path.write_text(new_text, encoding='utf-8')
    print('PATCHED')
else:
    print('NO CHANGE')
