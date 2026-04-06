import re
from typing import List

def chunk_text(text: str, max_words: int = 150) -> List[str]:
    """
    Split content into meaningful chunks (paragraphs, falling back to ~150 words).
    """
    if not text:
        return []
        
    # Clean up excessive newlines
    text = text.replace('\r', '\n')
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Split by double newline to get primary paragraphs
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    chunks = []
    
    for p in paragraphs:
        if len(p.split()) <= max_words:
            chunks.append(p)
        else:
            # Paragraph is too long, split by sentences
            sentences = re.split(r'(?<=[.!?])\s+', p)
            current_chunk = []
            current_len = 0
            
            for sentence in sentences:
                sentence_words = sentence.split()
                sentence_len = len(sentence_words)
                
                # If a single sentence is itself too long, split it by words (rare but possible)
                if sentence_len > max_words:
                    if current_chunk:
                        chunks.append(' '.join(current_chunk))
                        current_chunk = []
                        current_len = 0
                    
                    sub_chunks = [' '.join(sentence_words[i:i+max_words]) 
                                  for i in range(0, sentence_len, max_words)]
                    chunks.extend(sub_chunks[:-1])
                    if sub_chunks[-1]:
                        current_chunk = [sub_chunks[-1]]
                        current_len = len(sub_chunks[-1].split())
                elif current_len + sentence_len <= max_words:
                    current_chunk.append(sentence)
                    current_len += sentence_len
                else:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = [sentence]
                    current_len = sentence_len
                    
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                
    return chunks
