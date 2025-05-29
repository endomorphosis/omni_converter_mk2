class Constants:

    class SecurityMonitor:

        DANGEROUS_PATTERNS_REGEX = [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"<iframe.*?>.*?</iframe>",
            r"eval\s*\(",
            r"document\.write\s*\(",
            r"<object.*?>.*?</object>",
            r"<embed.*?>.*?</embed>",
            r"<applet.*?>.*?</applet>",
            r"<form.*?>.*?</form>"
        ]

        EXECUTABLE_EXTENSIONS = [
            ".exe", ".com", ".bat", ".cmd", ".sh", 
            ".ps1", ".vbs", ".js", ".jar", ".dll", 
            ".so"
        ]

        FILE_SIZE_LIMITS_IN_BYTES = { # TODO This should be in a config file
            "default": 100 * 1024 * 1024,  # 100 MB general limit
            "text": 10 * 1024 * 1024,      # 10 MB for text files
            "image": 50 * 1024 * 1024,     # 50 MB for images
            "audio": 100 * 1024 * 1024,    # 100 MB for audio
            "video": 500 * 1024 * 1024,    # 500 MB for video
            "application": 100 * 1024 * 1024,  # 100 MB for applications
        }

        FORMAT_NAMES = {
            "text": ["html", "xml", "plain", "csv", "calendar"],
            "image": ["jpeg", "png", "gif", "webp", "svg"],
            "audio": ["mp3", "wav", "ogg", "flac", "aac"],
            "video": ["mp4", "webm", "avi", "mkv", "mov"],
            "application": ["pdf", "json", "docx", "xlsx", "zip"]
        }

        PII_DETECTION_REGEX = [ # TODO This should be in a config file
            # Email addresses
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL REDACTED]'),
            # Phone numbers (various formats)
            (r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', '[PHONE REDACTED]'),
            # Social Security Numbers
            (r'\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b', '[SSN REDACTED]'),
            # Credit card numbers (simplistic)
            (r'\b(?:\d{4}[-.\s]?){3}\d{4}\b', '[CREDIT CARD REDACTED]'),
            # Dates of birth (various formats)
            (r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b', '[DATE REDACTED]'),
            # IP addresses
            (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP REDACTED]'),
            # URLs (simplified)
            (r'https?://[^\s<>"\']+', '[URL REDACTED]')
        ]

        REMOVE_ACTIVE_CONTENT_REGEX = [
            r"<iframe.*?>.*?</iframe>",
            r"<object.*?>.*?</object>",
            r"<embed.*?>.*?</embed>",
            r"<applet.*?>.*?</applet>",
            r"<form.*?>.*?</form>"
        ]

        REMOVE_SCRIPTS_REGEX = [
            r"<script.*?>.*?</script>",
            r"javascript:[^\s\"'<>]*",
            r"vbscript:[^\s\"'<>]*",
            r"eval\s*\([^)]*\)"
        ]

        SECURITY_RULES = { # TODO This should be in a config file
            "reject_executable": True,
            "reject_encrypted": True,
            "reject_password_protected": True,
            "max_compression_ratio": 100,  # Reject files with compression ratio > 100:1
            "sanitize_content": True,
            "remove_scripts": True,
            "remove_active_content": True,
            "remove_personal_data": True,
            "remove_metadata": False,  # We generally want to keep metadata
        }

        SENSITIVE_KEYS = [ # TODO This list should be in a config file, and also much longer.
            "author", "creator", "producer", "owner", "company", "email", 
            "phone", "address", "gps", "location", "username", "user",
            "password", "key", "secret", "token", "api_key", "auth"
        ]
