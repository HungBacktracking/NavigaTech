import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import nltk
from nltk.translate.bleu_score import sentence_bleu, corpus_bleu
from rouge_score import rouge_scorer
import asyncio


class RetrievalMetrics:
    """Metrics for evaluating retrieval quality"""
    
    @staticmethod
    def precision_at_k(retrieved_docs: List[str], relevant_docs: List[str], k: int) -> float:
        """Calculate Precision@K"""
        if k <= 0:
            return 0.0
        
        retrieved_k = retrieved_docs[:k]
        relevant_retrieved = len(set(retrieved_k) & set(relevant_docs))
        
        return relevant_retrieved / k if k > 0 else 0.0
    
    @staticmethod
    def recall_at_k(retrieved_docs: List[str], relevant_docs: List[str], k: int) -> float:
        """Calculate Recall@K"""
        if not relevant_docs or k <= 0:
            return 0.0
        
        retrieved_k = retrieved_docs[:k]
        relevant_retrieved = len(set(retrieved_k) & set(relevant_docs))
        
        return relevant_retrieved / len(relevant_docs)
    
    @staticmethod
    def f1_at_k(retrieved_docs: List[str], relevant_docs: List[str], k: int) -> float:
        """Calculate F1@K"""
        precision = RetrievalMetrics.precision_at_k(retrieved_docs, relevant_docs, k)
        recall = RetrievalMetrics.recall_at_k(retrieved_docs, relevant_docs, k)
        
        if precision + recall == 0:
            return 0.0
        
        return 2 * (precision * recall) / (precision + recall)
    
    @staticmethod
    def mean_reciprocal_rank(retrieved_docs: List[str], relevant_docs: List[str]) -> float:
        """Calculate Mean Reciprocal Rank (MRR)"""
        for i, doc in enumerate(retrieved_docs):
            if doc in relevant_docs:
                return 1.0 / (i + 1)
        return 0.0
    
    @staticmethod
    def ndcg_at_k(retrieved_docs: List[str], relevant_docs: List[str], 
                  relevance_scores: Dict[str, float], k: int) -> float:
        """Calculate Normalized Discounted Cumulative Gain (nDCG@K)"""
        def dcg(docs, scores, k):
            dcg_value = 0.0
            for i, doc in enumerate(docs[:k]):
                relevance = scores.get(doc, 0.0)
                dcg_value += relevance / np.log2(i + 2)  # i+2 because indexing starts at 0
            return dcg_value
        
        # Calculate DCG for retrieved docs
        dcg_value = dcg(retrieved_docs, relevance_scores, k)
        
        # Calculate ideal DCG (sort by relevance)
        ideal_docs = sorted(relevant_docs, key=lambda x: relevance_scores.get(x, 0.0), reverse=True)
        idcg_value = dcg(ideal_docs, relevance_scores, k)
        
        return dcg_value / idcg_value if idcg_value > 0 else 0.0
    
    @staticmethod
    def map_score(queries_results: List[Tuple[List[str], List[str]]]) -> float:
        """Calculate Mean Average Precision (MAP)"""
        ap_scores = []
        
        for retrieved_docs, relevant_docs in queries_results:
            if not relevant_docs:
                continue
                
            precisions = []
            relevant_count = 0
            
            for i, doc in enumerate(retrieved_docs):
                if doc in relevant_docs:
                    relevant_count += 1
                    precisions.append(relevant_count / (i + 1))
            
            if precisions:
                ap_scores.append(sum(precisions) / len(relevant_docs))
            else:
                ap_scores.append(0.0)
        
        return np.mean(ap_scores) if ap_scores else 0.0


class GenerationMetrics:
    """Metrics for evaluating text generation quality"""
    
    def __init__(self):
        self.sentence_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.rouge_scorer_instance = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        
        # Download NLTK data if needed
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
    
    def bleu_score(self, reference: str, candidate: str, n_gram: int = 4) -> float:
        """Calculate BLEU score"""
        reference_tokens = nltk.word_tokenize(reference.lower())
        candidate_tokens = nltk.word_tokenize(candidate.lower())
        
        weights = tuple([1.0/n_gram] * n_gram)
        
        return sentence_bleu([reference_tokens], candidate_tokens, weights=weights)
    
    def rouge_scores(self, reference: str, candidate: str) -> Dict[str, float]:
        """Calculate ROUGE scores"""
        scores = self.rouge_scorer_instance.score(reference, candidate)
        
        return {
            'rouge1_precision': scores['rouge1'].precision,
            'rouge1_recall': scores['rouge1'].recall,
            'rouge1_f1': scores['rouge1'].fmeasure,
            'rouge2_precision': scores['rouge2'].precision,
            'rouge2_recall': scores['rouge2'].recall,
            'rouge2_f1': scores['rouge2'].fmeasure,
            'rougeL_precision': scores['rougeL'].precision,
            'rougeL_recall': scores['rougeL'].recall,
            'rougeL_f1': scores['rougeL'].fmeasure,
        }
    
    def semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity using sentence embeddings"""
        embeddings = self.sentence_model.encode([text1, text2])
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        return float(similarity)
    
    def bertscore(self, references: List[str], candidates: List[str]) -> Dict[str, float]:
        """Calculate BERTScore (simplified version using sentence transformers)"""
        ref_embeddings = self.sentence_model.encode(references)
        cand_embeddings = self.sentence_model.encode(candidates)
        
        # Calculate cosine similarities
        similarities = cosine_similarity(cand_embeddings, ref_embeddings)
        
        # Precision: for each candidate token, find max similarity to reference tokens
        precision_scores = np.max(similarities, axis=1).mean()
        
        # Recall: for each reference token, find max similarity to candidate tokens
        recall_scores = np.max(similarities, axis=0).mean()
        
        # F1
        f1_score = 2 * (precision_scores * recall_scores) / (precision_scores + recall_scores) if (precision_scores + recall_scores) > 0 else 0
        
        return {
            'precision': float(precision_scores),
            'recall': float(recall_scores),
            'f1': float(f1_score)
        }
    
    def answer_relevance(self, question: str, answer: str) -> float:
        """Measure how relevant the answer is to the question"""
        return self.semantic_similarity(question, answer)
    
    def faithfulness_score(self, context: str, answer: str) -> float:
        """Measure how faithful the answer is to the provided context"""
        # Split answer into sentences
        answer_sentences = nltk.sent_tokenize(answer)
        
        if not answer_sentences:
            return 0.0
        
        # Calculate similarity of each sentence to context
        scores = []
        for sentence in answer_sentences:
            score = self.semantic_similarity(context, sentence)
            scores.append(score)
        
        return np.mean(scores) if scores else 0.0


class HybridRAGMetrics:
    """Combined metrics for evaluating the full Hybrid RAG pipeline"""
    
    def __init__(self):
        self.retrieval_metrics = RetrievalMetrics()
        self.generation_metrics = GenerationMetrics()
    
    def evaluate_retrieval_stage(self, retrieved_docs: List[Dict[str, Any]], 
                                ground_truth_docs: List[str], 
                                relevance_scores: Dict[str, float] = None) -> Dict[str, Any]:
        """Evaluate retrieval stage comprehensively"""
        # Extract document IDs from retrieved docs
        retrieved_ids = [doc.get('id', str(i)) for i, doc in enumerate(retrieved_docs)]
        
        k_values = [1, 3, 5, 10, 20]
        results = {}
        
        for k in k_values:
            results[f'precision@{k}'] = self.retrieval_metrics.precision_at_k(retrieved_ids, ground_truth_docs, k)
            results[f'recall@{k}'] = self.retrieval_metrics.recall_at_k(retrieved_ids, ground_truth_docs, k)
            results[f'f1@{k}'] = self.retrieval_metrics.f1_at_k(retrieved_ids, ground_truth_docs, k)
            
            if relevance_scores:
                results[f'ndcg@{k}'] = self.retrieval_metrics.ndcg_at_k(
                    retrieved_ids, ground_truth_docs, relevance_scores, k
                )
        
        results['mrr'] = self.retrieval_metrics.mean_reciprocal_rank(retrieved_ids, ground_truth_docs)
        
        return results
    
    def evaluate_generation_stage(self, question: str, generated_answer: str, 
                                 reference_answer: str, context: str) -> Dict[str, Any]:
        """Evaluate generation stage comprehensively"""
        results = {}
        
        # BLEU scores
        results['bleu-1'] = self.generation_metrics.bleu_score(reference_answer, generated_answer, n_gram=1)
        results['bleu-2'] = self.generation_metrics.bleu_score(reference_answer, generated_answer, n_gram=2)
        results['bleu-4'] = self.generation_metrics.bleu_score(reference_answer, generated_answer, n_gram=4)
        
        # ROUGE scores
        rouge_scores = self.generation_metrics.rouge_scores(reference_answer, generated_answer)
        results.update(rouge_scores)
        
        # Semantic similarity
        results['semantic_similarity'] = self.generation_metrics.semantic_similarity(reference_answer, generated_answer)
        
        # Answer relevance to question
        results['answer_relevance'] = self.generation_metrics.answer_relevance(question, generated_answer)
        
        # Faithfulness to context
        results['faithfulness'] = self.generation_metrics.faithfulness_score(context, generated_answer)
        
        return results
    
    def evaluate_end_to_end(self, question: str, retrieved_docs: List[Dict[str, Any]], 
                           generated_answer: str, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate the complete pipeline"""
        results = {
            'question': question,
            'retrieval_metrics': {},
            'generation_metrics': {},
            'hybrid_metrics': {}
        }
        
        # Retrieval evaluation
        if 'relevant_docs' in ground_truth:
            results['retrieval_metrics'] = self.evaluate_retrieval_stage(
                retrieved_docs, 
                ground_truth['relevant_docs'],
                ground_truth.get('relevance_scores', {})
            )
        
        # Generation evaluation
        if 'reference_answer' in ground_truth:
            # Combine retrieved docs as context
            context = "\n\n".join([doc.get('text', '') for doc in retrieved_docs[:5]])
            
            results['generation_metrics'] = self.evaluate_generation_stage(
                question,
                generated_answer,
                ground_truth['reference_answer'],
                context
            )
        
        # Hybrid-specific metrics
        results['hybrid_metrics']['response_length'] = len(generated_answer.split())
        results['hybrid_metrics']['retrieval_diversity'] = self._calculate_retrieval_diversity(retrieved_docs)
        
        return results
    
    def _calculate_retrieval_diversity(self, retrieved_docs: List[Dict[str, Any]]) -> float:
        """Calculate diversity of retrieved documents"""
        if len(retrieved_docs) < 2:
            return 0.0
        
        # Extract text from documents
        texts = [doc.get('text', '')[:500] for doc in retrieved_docs[:10]]  # First 500 chars of top 10 docs
        
        if not any(texts):
            return 0.0
        
        # Calculate pairwise similarities
        embeddings = self.generation_metrics.sentence_model.encode(texts)
        similarities = cosine_similarity(embeddings)
        
        # Calculate average pairwise dissimilarity
        n = len(texts)
        total_dissimilarity = 0
        count = 0
        
        for i in range(n):
            for j in range(i + 1, n):
                total_dissimilarity += (1 - similarities[i][j])
                count += 1
        
        return total_dissimilarity / count if count > 0 else 0.0 