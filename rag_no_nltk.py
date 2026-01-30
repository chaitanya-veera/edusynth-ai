# ================= NLTK-FREE RAG SYSTEM =================
import re
from collections import Counter

class SimpleRAGNoNLTK:
    def __init__(self):
        self.chunks = []
        self.chunk_keywords = []
    
    def chunk_text(self, text, chunk_size=500):
        """Split text into chunks without NLTK"""
        # Simple sentence splitting by periods, exclamation, question marks
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def extract_keywords(self, text):
        """Extract keywords without NLTK"""
        # Common English stopwords
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your',
            'his', 'its', 'our', 'their', 'am', 'as', 'if', 'so', 'no', 'not', 'up', 'out', 'down', 'off',
            'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
            'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'only',
            'own', 'same', 'than', 'too', 'very', 'just', 'now', 'also', 'well', 'get', 'go', 'come', 'see'
        }
        
        # Simple word tokenization
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        keywords = [w for w in words if w not in stop_words]
        return Counter(keywords)
    
    def calculate_similarity(self, query_keywords, chunk_keywords):
        """Calculate similarity between query and chunk"""
        if not query_keywords or not chunk_keywords:
            return 0
        
        common_words = set(query_keywords.keys()) & set(chunk_keywords.keys())
        if not common_words:
            return 0
        
        score = 0
        for word in common_words:
            score += min(query_keywords[word], chunk_keywords[word])
        
        total_query_words = sum(query_keywords.values())
        return score / total_query_words if total_query_words > 0 else 0
    
    def index_document(self, text):
        """Index document for retrieval"""
        self.chunks = self.chunk_text(text)
        self.chunk_keywords = []
        
        for chunk in self.chunks:
            keywords = self.extract_keywords(chunk)
            self.chunk_keywords.append(keywords)
    
    def retrieve_relevant_chunks(self, query, top_k=3):
        """Retrieve most relevant chunks for query"""
        if not self.chunks:
            return []
        
        query_keywords = self.extract_keywords(query)
        chunk_scores = []
        
        for i, chunk_keywords in enumerate(self.chunk_keywords):
            score = self.calculate_similarity(query_keywords, chunk_keywords)
            chunk_scores.append((score, i))
        
        chunk_scores.sort(reverse=True)
        relevant_chunks = []
        
        for score, idx in chunk_scores[:top_k]:
            if score > 0.1:
                relevant_chunks.append(self.chunks[idx])
        
        return relevant_chunks