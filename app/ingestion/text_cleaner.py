import re


class TextCleaner:
    @staticmethod
    def clean(text: str) -> str:
        if not text:
            return ""

        text = re.sub(r"\r\n", "\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{2,}", "\n\n", text)

        return text.strip()