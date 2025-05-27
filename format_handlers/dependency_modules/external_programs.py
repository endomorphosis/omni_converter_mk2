import subprocess


from logger import logger


EXTERNAL_PROGRAMS = {
    "ffmpeg": False,  # ffmpeg for video processing
    "ffprobe": False,  # ffprobe for video metadata extraction
    "tesseract": False,  # tesseract for OCR (optional)
    "calibre": False,  # calibre for ebook processing (optional)
}

for program, bool_ in EXTERNAL_PROGRAMS.items():
    try:
        _ = subprocess.run([program, "-help"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        EXTERNAL_PROGRAMS[program] = True
        logger.info(f"{program} is available")
    except subprocess.CalledProcessError:
        logger.warning(f"{program} is not available, functionality will be limited")
        EXTERNAL_PROGRAMS[program] = False
    except Exception as e:
        logger.warning(f"{type(e).__name__} checking {program} availability: {e}")
        EXTERNAL_PROGRAMS[program] = False
