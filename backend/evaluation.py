"""
Simple RAGAS Evaluation for NavigaTech Chatbot
==============================================
This script provides a straightforward evaluation of the RAG pipeline
using RAGAS framework with minimal complexity.

Key Feature: Ground truth is generated from your actual retrieved data!
"""

import asyncio
from typing import List, Dict
import pandas as pd
from ragas import evaluate
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (
    answer_relevancy,
    faithfulness,
    context_recall,
    context_precision
)
from datasets import Dataset
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
key = os.getenv("OPENAI_API_KEY")

# Import your chatbot components
from app.core.containers.application_container import ApplicationContainer
from app.chatbot.chat_engine import ChatEngine


class SimpleRAGASEvaluator:
    """
    A simple evaluator for testing RAG performance using RAGAS metrics.
    """

    def __init__(self):
        """Initialize the evaluator with your existing chatbot setup."""
        # Initialize containers
        self.app_container = ApplicationContainer()
        # self.app_container.config.from_dict({
        #     "GEMINI_TOKEN": os.getenv("GEMINI_TOKEN"),
        #     "COHERE_API_TOKEN": os.getenv("COHERE_API_TOKEN"),
        #     "QDRANT_COLLECTION_NAME": "job_description_2",
        #     "COURSE_DB": "./courses_db",
        #     "EMBEDDING_MODEL_NAME": "sentence-transformers/all-MiniLM-L6-v2",
        #     "GEMINI_MODEL_NAME": "gemini-2.0-flash",
        #     "MAX_TOKENS": 10000,
        #     "TEMPERATURE": 0.6,
        # })

        # Get components
        self.chat_engine = self.app_container.chatbot.chat_engine()
        self.llm = self.app_container.AI.llm_gemini()
        self.embeddings = self.app_container.AI.embed_model()
        self.job_retriever = self.app_container.chatbot.job_retriever()
        self.course_retriever = self.app_container.chatbot.course_retriever()

    def create_test_questions(self) -> List[str]:
        """
        Create simple test questions about jobs and courses.
        Ground truth will be generated from actual retrieved data.
        """
        questions = [
            "What skills are needed for a Data Engineer position?",
            "Can you recommend Python courses for beginners?",
            "What are the responsibilities of a Software Engineer?",
            "How can I improve my data analysis skills?",
            "What is the typical salary range for a Machine Learning Engineer?",
            "What are the requirements for a DevOps Engineer role?",
            "Which online courses teach React development?",
            "What does a Product Manager do?",
            "How to transition into a data science career?",
            "What programming languages should a backend developer know?"
        ]
        return questions

    async def generate_ground_truth_from_retrieval(self, question: str) -> Dict:
        """
        Generate ground truth answer based on retrieved documents.
        This ensures ground truth is based on actual data in your system.
        """
        # Retrieve relevant documents
        contexts = []

        # Determine which retriever to use based on question content
        if any(word in question.lower() for word in ['course', 'learn', 'study', 'tutorial']):
            # Use course retriever
            nodes = await self.course_retriever.aretrieve(question)
            contexts = [node.text for node in nodes[:5]]  # Top 5 contexts
        else:
            # Use job retriever (default)
            nodes = await self.job_retriever.aretrieve(question)
            contexts = [node.text for node in nodes[:5]]  # Top 5 contexts

        # Create prompt to generate ground truth from contexts
        context_str = "\n\n".join(contexts)
        prompt = f"""Based on the following retrieved documents, provide a comprehensive and accurate answer to the question.

Retrieved Documents:
{context_str}

Question: {question}

Instructions:
- Base your answer ONLY on the information provided in the retrieved documents
- Be specific and include relevant details from the documents
- If the documents don't contain enough information, acknowledge this
- Keep the answer concise but complete (2-3 paragraphs maximum)

Answer:"""

        # Generate ground truth using LLM
        response = await self.llm.acomplete(prompt)
        ground_truth = response.text.strip()

        return {
            "question": question,
            "ground_truth": ground_truth,
            "source_contexts": contexts
        }

    async def generate_responses(self, test_cases: List[Dict]) -> List[Dict]:
        """
        Generate responses from the chatbot for each test case.
        """
        results = []

        # Mock resume for testing
        mock_resume = """
        John Doe - Software Developer
        Skills: Python, JavaScript, SQL
        Experience: 2 years in web development
        Education: BS in Computer Science
        """

        for test_case in test_cases:
            print(f"Processing question: {test_case['question']}")

            # Initialize chat engine for this session
            self.chat_engine.compose(
                resume=mock_resume,
                memory=[],
                session_id=f"test_session_{test_cases.index(test_case)}"
            )

            # Get response from chatbot
            response_text = ""
            async for chunk in self.chat_engine.stream_chat(test_case['question']):
                response_text += chunk

            # Get contexts from retrievers (simplified)
            contexts = []

            # For job-related questions
            if any(word in test_case['question'].lower() for word in ['engineer', 'developer', 'salary', 'position']):
                job_nodes = await self.chat_engine.retrievers['job'].aretrieve(test_case['question'])
                contexts.extend([node.text for node in job_nodes[:3]])

            # For course-related questions
            if any(word in test_case['question'].lower() for word in ['course', 'learn', 'improve', 'skills']):
                course_nodes = await self.chat_engine.retrievers['course'].aretrieve(test_case['question'])
                contexts.extend([node.text for node in course_nodes[:3]])

            result = {
                "question": test_case["question"],
                "answer": response_text,
                "contexts": contexts if contexts else ["No specific context found"],
                "ground_truth": test_case["ground_truth"]
            }
            results.append(result)

            # Clear memory for next test
            self.chat_engine.clear_memory()

        return results

    def evaluate_with_ragas(self, results: List[Dict]) -> Dict:
        """
        Evaluate the results using RAGAS metrics.
        """
        # Convert to RAGAS dataset format
        dataset_dict = {
            "question": [r["question"] for r in results],
            "answer": [r["answer"] for r in results],
            "contexts": [r["contexts"] for r in results],
            "ground_truth": [r["ground_truth"] for r in results]
        }

        dataset = Dataset.from_dict(dataset_dict)

        # Run RAGAS evaluation
        evaluation_result = evaluate(
            dataset,
            metrics=[
                answer_relevancy,
                faithfulness,
                context_recall,
                context_precision
            ],
            raise_exceptions=True,
        )

        return evaluation_result

    def print_results(self, evaluation_result: Dict, detailed_results: List[Dict]):
        """
        Print evaluation results in a readable format.
        """
        print("\n" + "="*60)
        print("RAGAS EVALUATION RESULTS")
        print("="*60)

        # Overall metrics
        print("\nOVERALL METRICS:")
        print(evaluation_result)
        # for metric, score in evaluation_result.items():
        #     if isinstance(score, (int, float)):
        #         print(f"  {metric}: {score:.3f}")

        # Detailed results for each question
        print("\n" + "-"*60)
        print("DETAILED RESULTS:")
        print("-"*60)

        for i, result in enumerate(detailed_results):
            print(f"\nQuestion {i+1}: {result['question']}")
            print(f"Answer: {result['answer'][:200]}..." if len(result['answer']) > 200 else f"Answer: {result['answer']}")
            print(f"Ground Truth: {result['ground_truth']}")
            print(f"Number of contexts retrieved: {len(result['contexts'])}")

        # Save results to CSV
        df = pd.DataFrame(detailed_results)
        df.to_csv("ragas_evaluation_results.csv", index=False)
        print("\n✅ Results saved to 'ragas_evaluation_results.csv'")


async def main():
    """
    Main function to run the evaluation.
    """
    print("🚀 Starting Simple RAGAS Evaluation...")
    print("📝 Ground truth will be generated from your actual data!\n")

    # Initialize evaluator
    evaluator = SimpleRAGASEvaluator()

    # Create test questions
    print("📋 Creating test questions...")
    questions = evaluator.create_test_questions()
    print(f"Created {len(questions)} test questions")

    # Generate ground truth from retrieved data
    print("\n🔍 Generating ground truth from retrieved documents...")
    test_cases = []
    for i, question in enumerate(questions[:5]):  # Use first 5 questions for quick evaluation
        print(f"  Processing question {i+1}/5: {question[:50]}...")
        ground_truth_data = await evaluator.generate_ground_truth_from_retrieval(question)
        test_cases.append(ground_truth_data)
        print(f"  ✓ Generated ground truth from {len(ground_truth_data['source_contexts'])} retrieved documents")

    print(f"\n✅ Generated ground truth for {len(test_cases)} questions")

    # Generate responses
    print("\n💬 Generating responses from chatbot...")
    results = await evaluator.generate_responses(test_cases)

    # Evaluate with RAGAS
    print("\n📈 Evaluating with RAGAS metrics...")
    evaluation_result = evaluator.evaluate_with_ragas(results)

    # Print results
    evaluator.print_results(evaluation_result, results)

    # Save ground truth data for reference
    ground_truth_df = pd.DataFrame(test_cases)
    ground_truth_df.to_csv("ground_truth_from_retrieval.csv", index=False)
    print("\n📄 Ground truth data saved to 'ground_truth_from_retrieval.csv'")

    print("\n✨ Evaluation complete!")


if __name__ == "__main__":
    # Run the evaluation
    asyncio.run(main())