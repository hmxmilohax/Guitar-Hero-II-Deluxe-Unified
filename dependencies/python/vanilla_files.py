def vanilla(ark_files, args_platform, ninja, Path, vanilla_files=None):
    if vanilla_files is None:
        vanilla_files = []
    
    # copy vanilla files to obj/ark before building ark
    for f in filter(lambda x: x.is_file(), Path("vanilla", args_platform, "ark").rglob("*")):
        index = f.parts.index(args_platform)
        out_path = Path("obj", args_platform).joinpath(*f.parts[index + 1 :])
        if str(out_path) not in ark_files:
            ninja.build(str(out_path), "copy", str(f))
            vanilla_files.append(str(out_path))
    
    return ark_files, vanilla_files

