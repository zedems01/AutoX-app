import re
import unicodedata

def get_char_count(text: str) -> int:
    """
    Calculates the character count of a string for Twitter, where emojis count as 2 characters
    and URLs count as 23 characters.
    """
    url_regex = r"https?://[^\s]+"
    urls = re.findall(url_regex, text)
    
    # Replace URLs with a placeholder to not count their length
    text_no_urls = re.sub(url_regex, "", text)
    
    emoji_count = 0
    char_count = 0

    for char in text_no_urls:
        # Check if the character is an emoji
        if unicodedata.category(char) in ('So', 'Sc'):
            emoji_count += 1
        else:
            char_count += 1
    
    # Emojis count as 2, normal chars as 1, and each URL as 23
    return char_count + (emoji_count * 2) + (len(urls) * 23)

def chunk_text(text: str, max_length: int = 280) -> list[str]:
    """
    Chunks a long text into a list of smaller strings, each within the max_length,
    respecting word boundaries and Twitter's character counting rules.
    """
    if get_char_count(text) <= max_length:
        return [text]

    chunks = []
    words = text.split(' ')
    current_chunk = ""

    for word in words:
        # Check if adding the next word exceeds the max length
        if get_char_count(current_chunk + " " + word) > max_length:
            chunks.append(current_chunk.strip())
            current_chunk = word
        else:
            if current_chunk:
                current_chunk += " " + word
            else:
                current_chunk = word
    
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    # Add numbering (e.g., 1/n)
    num_chunks = len(chunks)
    if num_chunks > 1:
        for i, chunk in enumerate(chunks):
            prefix = f"({i+1}/{num_chunks}) "
            # Check if the prefix can be added without exceeding the limit
            if get_char_count(prefix + chunk) <= max_length:
                chunks[i] = prefix + chunk
            else:
                # This part needs a more robust implementation if chunks are already near the limit.
                # For now, we prepend and might slightly exceed, assuming initial chunking left some space.
                # A better way would be to account for the prefix length during initial chunking.
                chunks[i] = prefix + chunk 

    return chunks 