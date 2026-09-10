#!/usr/bin/python3
from lib import ninja_syntax
from pathlib import Path
import sys
import argparse
import os
import shutil  # for directory removal

from PIL import Image, ImageFilter

game_name = "Guitar Hero II Deluxe Unified"

ninja = ninja_syntax.Writer(open("build.ninja", "w+"))

#versions
#gh1, gh2 - " "
#rb1, track packs - "-v 4"
#rb2, tbrb, gdrb - "-v 5"
#rb3, dc, blitz - "-v 6"
ninja.variable("ark_version", " ")

#set True for rb1 and newer 
new_gen = False

#patch for patch arks, main for patchcreator, old gen, and rb1
hdr_name = "main"

dtb_encrypt = "-e"
ark_encrypt = "-e"
miloVersion = "--miloVersion 25"

#paths in _ark/dx/custom_textures that should generate list dtbs
custom_texture_paths = [
    "main"
]

#patchcreator options
patchcreator = True
new_ark_part = "1"

#end of options

parser = argparse.ArgumentParser(prog="configure")
parser.add_argument("platform")
parser.add_argument("game")

args = parser.parse_args()

gen_folder = "gen"

#Wii should always use patchcreator
if args.platform == "wii":
    patchcreator = True

#THIS IS TEMPLATE YOU CAN REMOVE IF YOU DONT NEED IT
if args.platform == "ps2":
    #all milo ps2 games from gh to rb use MAIN_0.ARK
    hdr_name = "MAIN"
    if new_gen == False:
        #pre rb2 does not use miloVersion for superfreq image generation on ps2
        miloVersion = " "
        #remove these two if rock band 1
        ark_encrypt = " "
        dtb_encrypt = "-E"

if args.game == "gh2":
    GH2 = True

if args.game == "gh80s":
    GH80s = True

if args.game == "80s":
    GH80s = True

ninja.variable("dtb_encrypt", dtb_encrypt)
ninja.variable("ark_encrypt", ark_encrypt)
ninja.variable("miloVersion", miloVersion)

#new gen games (rb2 onward) add platform suffix to ark name
if new_gen == True:
    hdr_name = hdr_name + "_" + args.platform

print(f"Configuring {game_name}...")
print(f"Platform: {args.platform}, Game: {args.game}")

# configure tools
ark_dir = Path("obj", args.game, args.platform, "ark")

# ALWAYS remove obj/.../ark/ui/image to avoid stale images
stale_image_dir = ark_dir / "ui" / "image"
shutil.rmtree(stale_image_dir, ignore_errors=True)

def is_macos_junk(path: Path) -> bool:
    name = path.name
    # .DS_Store and AppleDouble resource fork files like ._whatever
    return name == ".DS_Store" or name.startswith("._")

match sys.platform:
    case "win32":
        ninja.variable("silence", ">nul")
        ninja.rule("copy", "cmd /c copy $in $out $silence", description="COPY $in")
        ninja.rule("bswap", "dependencies\\windows\\swap_art_bytes.exe $in $out", description="BSWAP $in")
        ninja.rule("version", "python dependencies\\python\\gen_version.py $out", description="Writing version info")
        ninja.rule("png_list", "python dependencies\\python\\png_list.py $dir $out", description="PNGLIST $dir")
        ninja.variable("superfreq", "dependencies\\windows\\superfreq.exe")
        ninja.variable("arkhelper", "dependencies\\windows\\arkhelper.exe")
        ninja.variable("dtab", "dependencies\\windows\\dtab.exe")
        ninja.variable("dtacheck", "dependencies\\windows\\dtacheck.exe")
    case "darwin":
        ninja.variable("silence", "> /dev/null")
        ninja.rule("copy", "cp $in $out", description="COPY $in")
        ninja.rule("bswap", "python3 dependencies/python/swap_rb_art_bytes.py $in $out", description="BSWAP $in")
        ninja.rule("version", "python3 dependencies/python/gen_version.py $out", description="Writing version info")
        ninja.rule("png_list", "python3 dependencies/python/png_list.py $dir $out", description="PNGLIST $dir")
        ninja.variable("superfreq", "dependencies/macos/superfreq")
        ninja.variable("arkhelper", "dependencies/macos/arkhelper")
        ninja.variable("dtab", "dependencies/macos/dtab")
        ninja.variable("dtacheck", "dependencies/macos/dtacheck")
    case "linux":
        ninja.variable("silence", "> /dev/null")
        ninja.rule("copy", "cp --reflink=auto $in $out", description="COPY $in")
        ninja.rule("bswap", "dependencies/linux/swap_art_bytes $in $out", "BSWAP $in")
        ninja.rule("version", "python dependencies/python/gen_version.py $out", description="Writing version info")
        ninja.rule("png_list", "python dependencies/python/png_list.py $dir $out", description="PNGLIST $dir")
        ninja.variable("superfreq", "dependencies/linux/superfreq")
        ninja.variable("arkhelper", "dependencies/linux/arkhelper")
        ninja.variable("dtab", "dependencies/linux/dtab")
        ninja.variable("dtacheck", "dependencies/linux/dtacheck")

#specify output directories per platform
match args.platform:
    case "ps3":
        out_dir = Path("out", args.game, args.platform, "USRDIR", gen_folder)
    case "xbox":
        out_dir = Path("out", args.game, args.platform, gen_folder)
    case "wii":
        out_dir = Path("out", args.game, args.platform, "files", gen_folder)
    case "ps2":
        out_dir = Path("out", args.game, args.platform, gen_folder.upper())

#building an ark
if patchcreator == False:
    ninja.rule(
        "ark",
        f"$arkhelper dir2ark -n {hdr_name} $ark_version $ark_encrypt -s 4073741823 --logLevel error {ark_dir} {out_dir}",
        description="Building ark",
    )

#patchcreating an ark
if patchcreator == True:
    #patch creator time!
    #patchcreator forces into a gen folder itself it sucks
    out_dir = out_dir.parent
    #force using main as the root name
    hdr_name = "main"
    #append platform if this is new style ark
    if new_gen == True:
        hdr_name = hdr_name + "_" + args.platform
    #this is fucking hilarious
    exec_path = ".gitignore"
    match args.platform:
        case "wii":
            hdr_path = "platform/" + args.game + "/" + args.platform + "/files/" + gen_folder + "/" + hdr_name + ".hdr"
        case "ps2":
            hdr_path = "platform/" + args.game + "/" + args.platform + "/" + gen_folder.upper() + "/" + hdr_name.upper() + ".HDR"
        case "ps3":
            hdr_path = "platform/" + args.game + "/" + args.platform + "/USRDIR/" + gen_folder + "/" + hdr_name + ".hdr"
        case "xbox":
            hdr_path = "platform/" + args.game + "/" + args.platform + "/" + gen_folder + "/" + hdr_name + ".hdr"
    ninja.rule(
        "ark",
        f"$arkhelper patchcreator -a {ark_dir} -o {out_dir} {hdr_path} {exec_path} --logLevel error",
        description="Building ark",
    )

ninja.rule(
    "sfreq",
    f"$superfreq png2tex -l error $miloVersion --platform $platform $in $out",
    description="SFREQ $in"
    )
ninja.rule("dtacheck", "$dtacheck $in .dtacheckfns", description="DTACHECK $in")
ninja.rule("dtab_serialize", "$dtab -b $in $out", description="DTAB SER $in")
ninja.rule("dtab_encrypt", f"$dtab $dtb_encrypt $in $out", description="DTAB ENC $in")
ninja.build("_always", "phony")

build_files = []

# For PS2, define additional folder names to ignore.
ps2_ignore_folders = {
    "ignore", "alterog1", "classog", "deathmetog1", "deathmetog2",
    "rocabiog1", "rockabiog2", "fuog1", "glog1", "glog2",
    "goog1", "goog2", "grog", "metog1", "metog2", "puog1",
    "puog2", "roog1", "roog2"
}

# copy whatever arbitrary files you need to output
def platform_file_filter(f: Path):
    if not f.is_file():
        return False
    # For PS2, check only the directory parts.
    if args.platform == "ps2":
        if "ng" in (part.lower() for part in f.parts[:-1]):
            return False
        if any(part.lower() in ps2_ignore_folders for part in f.parts[:-1]):
            return False
    # For Xbox, check only the directory parts.
    if args.platform == "xbox":
        if "og" in (part.lower() for part in f.parts[:-1]):
            return False
    return True

for f in filter(platform_file_filter, Path("dependencies", "platform_files", args.game, args.platform).rglob("*")):
    index = f.parts.index(args.platform)
    out_path = Path("out", args.game, args.platform).joinpath(*f.parts[index + 1 :])
    ninja.build(str(out_path), "copy", str(f))
    build_files.append(str(out_path))

def ark_file_filter(file: Path):
    if file.is_dir():
        return False
    if is_macos_junk(file):
        return False
    # For PS2, check only the directory parts.
    if args.platform == "ps2":
        if "ng" in (part.lower() for part in file.parts[:-1]):
            return False
        if any(part.lower() in ps2_ignore_folders for part in file.parts[:-1]):
            return False
    if file.suffix.endswith("_ps3") and args.platform != "ps3":
        return False
    if file.suffix.endswith("_xbox") and args.platform != "xbox":
        return False
    if file.suffix.endswith("_wii") and args.platform != "wii":
        return False
    if file.suffix.endswith("mogg") and args.platform == "ps2":
        return False
    if any(file.suffix.endswith(suffix) for suffix in ["_ps2", "vgs"]) and args.platform != "ps2":
        return False
    return True


# build ark files
ark_files = []

for f in filter(ark_file_filter, Path("_ark").rglob("*")):
    match f.suffixes:
        case [".bmp"]:
            output_directory = Path("obj", args.game, args.platform, "ark").joinpath(
                *f.parent.parts[1:]
            )
            match args.platform:
                case "xbox":
                    target_filename = Path(gen_folder, f.stem + ".bmp_xbox")
                    xbox_directory = Path("obj", args.game, args.platform, "ark").joinpath(
                        *f.parent.parts[1:]
                    )
                    xbox_output = xbox_directory.joinpath(target_filename)
                    ninja.build(str(xbox_output), "sfreq", str(f), variables={"platform": "x360"})
                    ark_files.append(str(xbox_output))
                case "ps2":
                    target_image = Path(gen_folder, f.stem + ".bmp")
                    img_directory = Path("obj", args.game, args.platform, "ark").joinpath(
                        *f.parent.parts[1:]
                    )
                    img_output = img_directory.joinpath(target_image)
                    img_output.parent.mkdir(parents=True, exist_ok=True)
                    with Image.open(f) as img:
                        resized_img = img.resize((int(img.width * 0.5), int(img.height * 0.5)), resample=Image.BOX)
                        resized_img = resized_img.convert("P", dither=Image.NONE, palette=Image.ADAPTIVE)
                        resized_img.save(img_output)
                    target_filename = Path(gen_folder, f.stem + ".bmp_ps2")
                    ps2_directory = Path("obj", args.game, args.platform, "ark").joinpath(
                        *f.parent.parts[1:]
                    )
                    ps2_output = ps2_directory.joinpath(target_filename)
                    ninja.build(str(ps2_output), "sfreq", str(img_output), variables={"platform": "ps2"})
                    ark_files.append(str(ps2_output))
        case [".png"]:
            output_directory = Path("obj", args.game, args.platform, "ark").joinpath(
                *f.parent.parts[1:]
            )
            match args.platform:
                case "xbox":
                    target_filename = Path(gen_folder, f.stem + ".png_xbox")
                    xbox_directory = Path("obj", args.game, args.platform, "ark").joinpath(
                        *f.parent.parts[1:]
                    )
                    xbox_output = xbox_directory.joinpath(target_filename)
                    ninja.build(str(xbox_output), "sfreq", str(f), variables={"platform": "x360"})
                    ark_files.append(str(xbox_output))
                case "ps2":
                    target_image = Path(gen_folder, f.stem + ".png")
                    img_directory = Path("obj", args.game, args.platform, "ark").joinpath(
                        *f.parent.parts[1:]
                    )
                    img_output = img_directory.joinpath(target_image)
                    img_output.parent.mkdir(parents=True, exist_ok=True)
                    with Image.open(f) as img:
                        resized_img = img.resize((int(img.width * 0.5), int(img.height * 0.5)), resample=Image.BOX)
                        resized_img = resized_img.convert("P", dither=Image.NONE, palette=Image.ADAPTIVE)
                        resized_img.save(img_output)
                    target_filename = Path(gen_folder, f.stem + ".png_ps2")
                    ps2_directory = Path("obj", args.game, args.platform, "ark").joinpath(
                        *f.parent.parts[1:]
                    )
                    ps2_output = ps2_directory.joinpath(target_filename)
                    ninja.build(str(ps2_output), "sfreq", str(img_output), variables={"platform": "ps2"})
                    ark_files.append(str(ps2_output))
        case [".dta"]:
            target_filename = Path(gen_folder, f.stem + ".dtb")
            stamp_filename = Path(gen_folder, f.stem + ".dtb.checked")

            output_directory = Path("obj", args.game, args.platform, "ark").joinpath(
                *f.parent.parts[1:]
            )
            serialize_directory = Path("obj", args.game, args.platform, "raw").joinpath(
                *f.parent.parts[1:]
            )

            serialize_output = serialize_directory.joinpath(target_filename)
            stamp = serialize_directory.joinpath(stamp_filename)

            # By default, use the source file directly
            src_dta = f

            # Special-case: patch _ark/config/gh2.dta per game without touching the source
            if args.game in ("gh2", "gh80s", "80s") and f == Path("_ark", "config", "gh2.dta"):
                patched_dta = Path(
                    "obj",
                    args.game,
                    args.platform,
                    "patched_dta",
                    *f.parent.parts[1:],
                    f.name,
                )
                patched_dta.parent.mkdir(parents=True, exist_ok=True)

                with open(f, "r", encoding="utf-8") as src_file:
                    lines = src_file.readlines()

                if len(lines) >= 2:
                    if args.game == "gh2":
                        lines[1] = "#define GAME_GH2 (TRUE)\n"
                    elif args.game == "gh80s":
                        lines[1] = ";#define GAME_GH2 (TRUE)\n"
                    elif args.game == "80s":
                        lines[1] = ";#define GAME_GH2 (TRUE)\n"

                with open(patched_dta, "w", encoding="utf-8") as dst_file:
                    dst_file.writelines(lines)

                src_dta = patched_dta

            iso_dta = Path(
                "obj",
                args.game,
                args.platform,
                "iso_dta",
                *f.parent.parts[1:],
                f.name,
            )
            iso_dta.parent.mkdir(parents=True, exist_ok=True)

            with open(src_dta, "r", encoding="iso-8859-1") as src_file:
                text = src_file.read()

            with open(iso_dta, "w", encoding="iso-8859-1") as dst_file:
                dst_file.write(text)

            # Use the re-encoded file for dtacheck/dtab
            src_dta = iso_dta

            ninja.build(str(stamp), "dtacheck", str(src_dta))
            ninja.build(
                str(serialize_output),
                "dtab_serialize",
                str(src_dta),
                implicit=[str(stamp), "_always"],
            )

            encryption_output = output_directory.joinpath(target_filename)
            ninja.build(str(encryption_output), "dtab_encrypt", str(serialize_output))
            ark_files.append(str(encryption_output))
        case [".ini"]:
            nothing = 0
        case _:
            index = f.parts.index("_ark")
            rel_parts = list(f.parts[index + 1:])

            # GH80s (Xbox): remap /_ark/ui/image/ng_80s/... -> obj/.../ark/ui/image/ng/...
            #if args.game in ("gh80s", "80s") and args.platform == "xbox":
            #    if (
            #        len(rel_parts) >= 3
            #        and rel_parts[0] == "ui"
            #        and rel_parts[1] == "image"
            #        and rel_parts[2] == "ng_80s"
            #    ):
            #        rel_parts[2] = "ng"

            out_path = Path("obj", args.game, args.platform, "ark").joinpath(*rel_parts)
            ninja.build(str(out_path), "copy", str(f))
            ark_files.append(str(out_path))

# write version info
dta = Path("obj", args.game, args.platform, "raw", "dx", "locale", "dx_version.dta")
dtb = Path("obj", args.game, args.platform, "raw", "dx", "locale", gen_folder, "dx_version.dtb")
enc = Path("obj", args.game, args.platform, "ark", "dx", "locale", gen_folder, "dx_version.dtb")

ninja.build(str(dta), "version", implicit="_always")
ninja.build(str(dtb), "dtab_serialize", str(dta))
ninja.build(str(enc), "dtab_encrypt", str(dtb))

ark_files.append(str(enc))

def generate_texture_list(input_path: Path):
    base = input_path.parts[1:]
    dta = Path("obj", args.game, args.platform, "raw").joinpath(*base).joinpath("_list.dta")
    dtb = Path("obj", args.game, args.platform, "raw").joinpath(*base).joinpath(gen_folder, "_list.dtb")
    enc = Path("obj", args.game, args.platform, "ark").joinpath(*base).joinpath(gen_folder, "_list.dtb")
    ninja.build(str(dta), "png_list", variables={"dir": str(input_path)}, implicit="_always")
    ninja.build(str(dtb), "dtab_serialize", str(dta))
    ninja.build(str(enc), "dtab_encrypt", str(dtb))

root_path = Path("_ark", "dx", "custom_textures")
for texture_list_path in [root_path.joinpath(path) for path in custom_texture_paths]:
    generate_texture_list(texture_list_path)

# build ark
ark_part = "0"
if patchcreator == True:
    ark_part = new_ark_part
    match args.platform:
        case "xbox":
            hdr = str(Path("out", args.game, args.platform, hdr_name + ".hdr"))
            ark = str(Path("out", args.game, args.platform, hdr_name + "_" + ark_part + ".ark"))
        case "ps2":
            hdr = str(Path("out", args.game, args.platform, hdr_name + ".HDR"))
            ark = str(Path("out", args.game, args.platform, hdr_name + "_" + ark_part + ".ARK"))
ninja.build(
    ark,
    "ark",
    implicit=ark_files,
    implicit_outputs=[hdr],
)
build_files.append(hdr)

# make the all target build everything
ninja.build("all", "phony", build_files)
ninja.close()
