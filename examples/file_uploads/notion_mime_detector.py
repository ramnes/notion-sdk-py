import os
import mimetypes
from typing import Optional, Tuple


class NotionMIMETypeDetector:
    """
    Custom MIME type detector to ensure returned MIME types comply with Notion API requirements.
    Addresses cross-platform inconsistencies in MIME type detection.
    """

    # MIME type mappings officially supported by the Notion API
    NOTION_MIME_TYPES = {
        # Audio
        ".aac": "audio/aac",
        ".adts": "audio/aac",
        ".mid": "audio/midi",
        ".midi": "audio/midi",
        ".mp3": "audio/mpeg",
        ".mpga": "audio/mpeg",
        ".m4a": "audio/mp4",
        ".m4b": "audio/mp4",
        ".mp4": "audio/mp4",  # Note: This refers to audio in MP4 format
        ".oga": "audio/ogg",
        ".ogg": "audio/ogg",
        ".wav": "audio/wav",
        ".wma": "audio/x-ms-wma",
        # Document
        ".pdf": "application/pdf",
        ".txt": "text/plain",
        ".json": "application/json",
        ".doc": "application/msword",
        ".dot": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".dotx": "application/vnd.openxmlformats-officedocument.wordprocessingml.template",
        ".xls": "application/vnd.ms-excel",
        ".xlt": "application/vnd.ms-excel",
        ".xla": "application/vnd.ms-excel",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xltx": "application/vnd.openxmlformats-officedocument.spreadsheetml.template",
        ".ppt": "application/vnd.ms-powerpoint",
        ".pot": "application/vnd.ms-powerpoint",
        ".pps": "application/vnd.ms-powerpoint",
        ".ppa": "application/vnd.ms-powerpoint",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".potx": "application/vnd.openxmlformats-officedocument.presentationml.template",
        # Image
        ".gif": "image/gif",
        ".heic": "image/heic",
        ".jpeg": "image/jpeg",
        ".jpg": "image/jpeg",
        ".png": "image/png",
        ".svg": "image/svg+xml",
        ".tif": "image/tiff",
        ".tiff": "image/tiff",
        ".webp": "image/webp",
        ".ico": "image/vnd.microsoft.icon",
        # Video
        ".amv": "video/x-amv",
        ".asf": "video/x-ms-asf",
        ".wmv": "video/x-ms-asf",
        ".avi": "video/x-msvideo",
        ".f4v": "video/x-f4v",
        ".flv": "video/x-flv",
        ".gifv": "video/x-flv",
        ".m4v": "video/mp4",
        ".mp4": "video/mp4",  # Note: This refers to video in MP4 format and may conflict with audio MP4
        ".mkv": "video/mp4",
        ".webm": "video/webm",
        ".mov": "video/quicktime",
        ".qt": "video/quicktime",
        ".mpeg": "video/mpeg",
    }

    # Handle file types with extension conflicts (e.g., .mp4 can be either audio or video)
    AMBIGUOUS_EXTENSIONS = {".mp4": {"video": "video/mp4", "audio": "audio/mp4"}}

    @classmethod
    def guess_type(
        cls, filename: str, content_type_hint: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Guess the MIME type of a file, prioritizing types supported by the Notion API.

        Args:
            filename: The name or path of the file.
            content_type_hint: A hint indicating the content type ('audio', 'video', 'image', 'document').

        Returns:
            A tuple (mime_type, encoding), following the format of mimetypes.guess_type().
        """

        # Get the file extension
        _, ext = os.path.splitext(filename.lower())

        if not ext:
            return None, None

        # First, check if the type is supported by Notion
        if ext in cls.NOTION_MIME_TYPES:
            # Handle ambiguous file extensions
            if ext in cls.AMBIGUOUS_EXTENSIONS:
                ambiguous_types = cls.AMBIGUOUS_EXTENSIONS[ext]
                if content_type_hint and content_type_hint in ambiguous_types:
                    return ambiguous_types[content_type_hint], None
                # If no hint is provided, return the first one (usually the most common)
                return list(ambiguous_types.values())[0], None

            return cls.NOTION_MIME_TYPES[ext], None

        # If not in the Notion supported list, fall back to the system default
        # Note: This may return a type not supported by Notion
        return mimetypes.guess_type(filename)

    @classmethod
    def is_supported_by_notion(cls, filename: str) -> bool:
        """
        Check if the file is supported by the Notion API.

        Args:
            filename: The name or path of the file.

        Returns:
            bool: Whether the file is supported.
        """

        _, ext = os.path.splitext(filename.lower())
        return ext in cls.NOTION_MIME_TYPES

    @classmethod
    def get_supported_extensions(cls) -> list:
        """
        Get all file extensions supported by Notion.

        Returns:
            list: A list of supported file extensions.
        """

        return list(cls.NOTION_MIME_TYPES.keys())

    @classmethod
    def get_supported_extensions_by_category(cls) -> dict:
        """
        Get supported file extensions by category.

        Returns:
            dict: Extensions grouped by category.
        """

        categories = {"audio": [], "document": [], "image": [], "video": []}

        for ext, mime_type in cls.NOTION_MIME_TYPES.items():
            if mime_type.startswith("audio/"):
                categories["audio"].append(ext)
            elif mime_type.startswith("application/") or mime_type.startswith("text/"):
                categories["document"].append(ext)
            elif mime_type.startswith("image/"):
                categories["image"].append(ext)
            elif mime_type.startswith("video/"):
                categories["video"].append(ext)

        return categories


if __name__ == "__main__":
    # Create an instance
    detector = NotionMIMETypeDetector()

    # Test various file types
    test_files = [
        "example.ico",
        "document.pdf",
        "music.mp3",
        "video.mp4",
        "image.jpg",
        "archive.zip",
        "figure.png",
        "data.json",
        "presentation.pptx",
        "music.flac"
    ]

    print("=== Notion MIME Type Detection Results ===")
    for filename in test_files:
        mime_type, encoding = detector.guess_type(filename)
        is_supported = detector.is_supported_by_notion(filename)

        # Compare with the system default result
        system_mime, _ = mimetypes.guess_type(filename)

        print(f"File: {filename}")
        print(f"  Notion Detection: {mime_type}")
        print(f"  System Default: {system_mime}")
        print(f"  Supported: {is_supported}")
        print(f"  Consistency: {'✓' if mime_type == system_mime else '✗'}")
        print()

    # Display all supported extensions
    print("=== Display Supported Extensions by Category ===")
    categories = detector.get_supported_extensions_by_category()
    for category, extensions in categories.items():
        print(f"{category.upper()}: {', '.join(sorted(extensions))}")
