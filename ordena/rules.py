from dataclasses import dataclass, asdict
import re

@dataclass
class Rule:
    name: str
    extensions: list[str]

def defaults():
    return [Rule(n, e.split()) for n, e in [
        ('Images', 'jpg jpeg png webp gif heic heif bmp tiff tif svg avif ico raw cr2 nef'),
        ('Documents', 'pdf doc docx txt rtf odt xls xlsx csv ppt pptx ods odp md epub'),
        ('Videos', 'mp4 mov mkv avi webm m4v wmv mpg mpeg'),
        ('Audio', 'mp3 wav flac m4a aac ogg opus aiff wma'),
        ('Archives', 'zip rar 7z tar gz bz2 xz'),
        ('Installers', 'exe msi msix appx')]]

def validate(rules):
    names, extensions, result = set(), set(), []
    if not rules:
        raise ValueError('rules_empty')
    for rule in rules:
        name = rule.name.strip()
        stem = name.split('.')[0].upper()
        if (not name or len(name) > 100 or name != rule.name or name[-1:] in '. '
            or re.search(r'[<>:"/\\|?*\x00-\x1f]', name)
            or name in {'.', '..'} or stem in {'CON', 'PRN', 'AUX', 'NUL', 'CLOCK$'}
            or re.fullmatch(r'(COM|LPT)[0-9¹²³]', stem)):
            raise ValueError('invalid_name')
        if name.casefold() in names:
            raise ValueError('duplicate_category')
        names.add(name.casefold())
        exts = []
        for ext in rule.extensions:
            ext = ext.lower().lstrip('.')
            if not re.fullmatch(r'[a-z0-9]{1,20}', ext):
                raise ValueError('invalid_extension')
            if ext in extensions:
                raise ValueError('duplicate_extension')
            extensions.add(ext)
            exts.append(ext)
        result.append(Rule(name, exts))
    return result

def serialize(rules):
    return [asdict(rule) for rule in rules]
