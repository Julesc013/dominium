import pathlib 
for p in pathlib.Path('.').rglob('*'): 
    if p.is_file(): 
        try: 
            text=p.read_text(errors='ignore') 
        except Exception: 
            continue 
        if needle in text: 
            print(p) 
