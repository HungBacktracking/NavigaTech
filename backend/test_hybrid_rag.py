import asyncio
from app.core.containers.application_container import ApplicationContainer

async def test_hybrid_rag():
    container = ApplicationContainer()
    container.config.from_yaml(".env")
    
    # Get the chat engine
    chat_engine = container.chatbot.chat_engine()
    
    # Check if hybrid retrievers are properly configured
    print("=== Checking Hybrid RAG Configuration ===")
    
    # Check job retriever
    job_retriever = chat_engine.retrievers.get("job")
    print(f"Job Retriever Type: {type(job_retriever).__name__}")
    if hasattr(job_retriever, 'embedding_retriever') and hasattr(job_retriever, 'graph_retriever'):
        print("✓ Job retriever has both embedding and graph components")
        print(f"  - Embedding weight: {job_retriever.embedding_weight}")
        print(f"  - Graph weight: {job_retriever.graph_weight}")
    else:
        print("✗ Job retriever is not a hybrid retriever")
    
    # Check course retriever
    course_retriever = chat_engine.retrievers.get("course")
    print(f"\nCourse Retriever Type: {type(course_retriever).__name__}")
    if hasattr(course_retriever, 'embedding_retriever') and hasattr(course_retriever, 'graph_retriever'):
        print("✓ Course retriever has both embedding and graph components")
        print(f"  - Embedding weight: {course_retriever.embedding_weight}")
        print(f"  - Graph weight: {course_retriever.graph_weight}")
    else:
        print("✗ Course retriever is not a hybrid retriever")
    
    # Test a simple retrieval
    print("\n=== Testing Retrieval ===")
    try:
        # Initialize the chat engine
        chat_engine.compose(
            resume="Test user with Python and data engineering skills",
            memory=[],
            session_id="test_session"
        )
        
        # Test retrieval
        from llama_index.core.schema import QueryBundle
        query = QueryBundle(query_str="data engineer jobs")
        
        # Test job retriever
        print("\nTesting job retriever...")
        job_results = await job_retriever._aretrieve(query)
        print(f"Retrieved {len(job_results)} job results")
        
        # Test if graph retriever is working
        if hasattr(job_retriever, 'graph_retriever'):
            print("\nTesting graph component directly...")
            graph_results = await job_retriever.graph_retriever._aretrieve(query)
            print(f"Graph retriever returned {len(graph_results)} results")
        
    except Exception as e:
        print(f"Error during retrieval test: {e}")
        import traceback
        traceback.print_exc()
    
    # Cleanup
    container.shutdown_resources()

if __name__ == "__main__":
    asyncio.run(test_hybrid_rag()) 