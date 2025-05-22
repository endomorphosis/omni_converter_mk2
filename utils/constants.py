FORMAT_SIGNATURES: dict[str, str] = {
    # Map of MIME types to formats
    # Text formats
    'text/html': 'html',
    'application/xhtml+xml': 'html',
    'text/xml': 'xml',
    'application/xml': 'xml',
    'text/plain': 'plain',
    'text/calendar': 'calendar',
    'text/csv': 'csv',
    
    # Image formats
    'image/jpeg': 'jpeg',
    'image/png': 'png',
    'image/gif': 'gif',
    'image/webp': 'webp',
    'image/svg+xml': 'svg',
    
    # Audio formats
    'audio/mpeg': 'mp3',
    'audio/mp3': 'mp3',
    'audio/wav': 'wav',
    'audio/x-wav': 'wav',
    'audio/ogg': 'ogg',
    'audio/flac': 'flac',
    'audio/aac': 'aac',
    
    # Video formats
    'video/mp4': 'mp4',
    'video/webm': 'webm',
    'video/x-msvideo': 'avi',
    'video/x-matroska': 'mkv',
    'video/quicktime': 'mov',
    
    # Application formats
    'application/pdf': 'pdf',
    'application/json': 'json',
    'application/zip': 'zip',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx'
}


FORMAT_EXTENSIONS = {
    # Text formats
    'html': 'html',
    'htm': 'html',
    'xhtml': 'html',
    'xml': 'xml',
    'txt': 'plain',
    'text': 'plain',
    'ics': 'calendar',
    'csv': 'csv',
    
    # Image formats
    'jpg': 'jpeg',
    'jpeg': 'jpeg',
    'png': 'png',
    'gif': 'gif',
    'webp': 'webp',
    'svg': 'svg',
    
    # Audio formats
    'mp3': 'mp3',
    'wav': 'wav',
    'ogg': 'ogg',
    'flac': 'flac',
    'aac': 'aac',
    
    # Video formats
    'mp4': 'mp4',
    'webm': 'webm',
    'avi': 'avi',
    'mkv': 'mkv',
    'mov': 'mov',
    
    # Application formats
    'pdf': 'pdf',
    'json': 'json',
    'zip': 'zip',
    'docx': 'docx',
    'xlsx': 'xlsx'
}
