from typing import List, Dict


class MetadataBuilder:
    @staticmethod
    def build(
        chunks: List[str],
        source_type: str,
        filename: str
    ) -> List[Dict]:
        metadata = []

        for idx, _ in enumerate(chunks):
            metadata.append({
                "chunk_id": idx,
                "source_type": source_type,
                "filename": filename
            })

        return metadata