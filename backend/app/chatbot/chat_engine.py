from llama_index.core import Settings
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core.chat_engine import (
    CondensePlusContextChatEngine,
    SimpleChatEngine,
)
from llama_index.core.tools import RetrieverTool
from llama_index.core.retrievers import RouterRetriever
from llama_index.core.selectors import LLMSingleSelector
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.llms import ChatMessage
import nest_asyncio
import json
import asyncio
from typing import Optional, Dict, List, AsyncGenerator
from dataclasses import dataclass
import re

nest_asyncio.apply()


@dataclass
class DebateConfig:
    """Configuration for multi-agent debate"""
    turns: int = 2
    temperature: float = 0.6

    expert_meta: str = """You are an expert career advisor specializing in computer science and IT. 
    You provide thoughtful, comprehensive advice based on the context provided."""

    expert_prompt: str = """
    You are an intelligent assistant specializing in job matching, job discovery, resume analysis, and career guidance. Your objective is to help users find relevant job opportunities and assess their fit based on job descriptions and their professional background. 

    You have access to:   
    - A vector database of job descriptions and online courses (retrieved based on contextual relevance)   
    - The user's resume or summarized professional experience   

    ### Guidelines for Handling User Queries: 

    1. **Understanding Intent:**   
    - Analyze the user's query to determine whether they are seeking job recommendations, course suggestions, or roadmap guidance. 

    2. **Contextual Query Rephrasing:**   
    - Use relevant job descriptions and resume content to rephrase or clarify the user's query as a specific, standalone question. 

    3. **Job Recommendations:**   
    - If the query involves job recommendations, respond in **bullet points** with the following format: 
    ## Data Engineer 

    **Company Name:** Digital Intellect  
    **Summary:** Role Overview: As a Data Engineer, you will collaborate closely with the client's Data Lead to design, develop, and maintain data architectures that enhance their data platforms.... 
    **URL:** https://www.vietnamworks.com/data-engineer--1906728-jv?source=searchResults&searchType=2&placement=1906728&sortBy=date 

    4. **Course Recommendations or Roadmaps:**   
    - If the query involves courses or roadmaps, respond in **bullet points** with the following format: 

    ## {Course Title} 

    **Skills:** {Skills Learned}   
    **What You Will Learn:** {What the user will learn here}   
    **Description:** {Course Description}   
    **URL:** {Course URL} 

    
    Based on the context and user query, provide detailed expert advice 
    highlighting opportunities, strengths, and positive paths forward.
    Instruction: Based on the context documents, provide a detailed answer for the user question. 
    Answer "don't know" if not present in the document.
    """

    critic_meta: str = """
    You are a critical analyzer who identifies potential challenges and gaps.
    You provide constructive criticism to ensure comprehensive guidance."""

    critic_prompt: str = """
    You are an intelligent assistant specializing in job matching, job discovery, resume analysis, and career guidance. Your objective is to help users find relevant job opportunities and assess their fit based on job descriptions and their professional background. 

    You have access to:   
    - A vector database of job descriptions and online courses (retrieved based on contextual relevance)   
    - The user's resume or summarized professional experience   

    ### Guidelines for Handling User Queries: 

    1. **Understanding Intent:**   
    - Analyze the user's query to determine whether they are seeking job recommendations, course suggestions, or roadmap guidance. 

    2. **Contextual Query Rephrasing:**   
    - Use relevant job descriptions and resume content to rephrase or clarify the user's query as a specific, standalone question. 

    3. **Job Recommendations:**   
    - If the query involves job recommendations, respond in **bullet points** with the following format: 
    ## Data Engineer 

    **Company Name:** Digital Intellect  
    **Summary:** Role Overview: As a Data Engineer, you will collaborate closely with the client's Data Lead to design, develop, and maintain data architectures that enhance their data platforms.... 
    **URL:** https://www.vietnamworks.com/data-engineer--1906728-jv?source=searchResults&searchType=2&placement=1906728&sortBy=date 

    4. **Course Recommendations or Roadmaps:**   
    - If the query involves courses or roadmaps, respond in **bullet points** with the following format: 

    ## {Course Title} 

    **Skills:** {Skills Learned}   
    **What You Will Learn:** {What the user will learn here}   
    **Description:** {Course Description}   
    **URL:** {Course URL} 

    
    Analyze the previous response and identify any gaps, challenges, 
    or areas that need more consideration. Be constructive but thorough.
    Instruction: Based on the context documents, provide a detailed answer for the user question. 
    Answer "don't know" if not present in the document.
    """

    synthesizer_meta: str = """You are a synthesis expert who combines multiple perspectives 
    into comprehensive, balanced advice."""

    synthesizer_prompt: str = """
    You are an intelligent assistant specializing in job matching, job discovery, resume analysis, and career guidance. Your objective is to help users find relevant job opportunities and assess their fit based on job descriptions and their professional background. 

            You have access to:   
            - A vector database of job descriptions and online courses (retrieved based on contextual relevance)   
            - The user's resume or summarized professional experience   

            ### Guidelines for Handling User Queries: 

            1. **Understanding Intent:**   
            - Analyze the user's query to determine whether they are seeking job recommendations, course suggestions, or roadmap guidance. 

            2. **Contextual Query Rephrasing:**   
            - Use relevant job descriptions and resume content to rephrase or clarify the user's query as a specific, standalone question. 

            3. **Job Recommendations:**   
            - If the query involves job recommendations, respond in **bullet points** with the following format: 
            ## Data Engineer 

            **Company Name:** Digital Intellect  
            **Summary:** Role Overview: As a Data Engineer, you will collaborate closely with the client's Data Lead to design, develop, and maintain data architectures that enhance their data platforms.... 
            **URL:** https://www.vietnamworks.com/data-engineer--1906728-jv?source=searchResults&searchType=2&placement=1906728&sortBy=date 

            4. **Course Recommendations or Roadmaps:**   
            - If the query involves courses or roadmaps, respond in **bullet points** with the following format: 

            ## {Course Title} 

            **Skills:** {Skills Learned}   
            **What You Will Learn:** {What the user will learn here}   
            **Description:** {Course Description}   
            **URL:** {Course URL} 
            
            5. **Response Formatting:**   
            - Ensure all responses are structured in **Markdown format** with appropriate headings for clarity and organization. 
            - Job and course Title MUST be heading like this: ## Job Title 

    
    Based on the expert perspective: {expert_response}
    And the critical analysis: {critic_response}

    Synthesize a comprehensive, balanced response that:
    1. Incorporates the strengths from the expert perspective
    2. Addresses the concerns raised by the critic
    3. Provides actionable, practical advice
    4. Maintains the same markdown formatting as requested

    User's original query: {user_query}
    Context provided: {context}
    
    Instruction: Based on the context documents and previous conversation, provide a detailed answer for the user question. 
    Answer "don't know" if not present in the document.
    """


class MultiAgentDebateEngine:
    """Multi-agent debate engine for enhanced responses"""

    def __init__(self, llm, config: Optional[DebateConfig] = None):
        self.llm = llm
        self.config = config or DebateConfig()

    async def debate(self, context: str, user_query: str) -> AsyncGenerator[str, None]:
        """Run multi-agent debate and yield results"""

        # Phase 1: Expert response
        expert_messages = [
            ChatMessage(role="system", content=self.config.expert_meta),
            ChatMessage(role="user",
                        content=f"Context: {context}\n\nQuery: {user_query}\n\n{self.config.expert_prompt}")
        ]

        expert_response = ""
        expert_stream = await self.llm.astream_chat(expert_messages)
        async for chunk in expert_stream:
            if chunk.delta:
                expert_response += chunk.delta

        # Phase 2: Critic response
        critic_messages = [
            ChatMessage(role="system", content=self.config.critic_meta),
            ChatMessage(role="user", content=f"Context: {context}\n\nQuery: {user_query}\n\nExpert's response: {expert_response}\n\n{self.config.critic_prompt}")
        ]

        critic_response = ""

        critic_stream = await self.llm.astream_chat(critic_messages)
        async for chunk in critic_stream:
            if chunk.delta:
                critic_response += chunk.delta



        # Phase 3: Synthesis
        synthesis_prompt = self.config.synthesizer_prompt.format(
            expert_response=expert_response,
            critic_response=critic_response,
            user_query=user_query,
            context=context
        )

        synthesizer_messages = [
            ChatMessage(role="system", content=self.config.synthesizer_meta),
            ChatMessage(role="user", content=synthesis_prompt)
        ]


        synthesis_stream = await self.llm.astream_chat(synthesizer_messages)
        async for chunk in synthesis_stream:
            if chunk.delta:
                yield chunk.delta


class ChatEngine:
    """
    Chatbot with two RAG pipelines (job & course) plus small talk.
    Now includes multi-agent debate capability.
    """

    def __init__(
            self,
            llm,
            embedding_model: HuggingFaceEmbedding,
            checker,
            job_retriever,
            course_retriever,
            chat_store,
            token_limit: int = 20000,
            job_collection: str = 'job_description_2',
            top_k: int = 20,
            temperature: float = 0.6,
            max_tokens: int = 10000,
            enable_debate: bool = False,
            debate_config: Optional[DebateConfig] = None  # New parameter
    ):
        # Load environment variables
        self.token_limit = token_limit
        self.top_k = top_k

        # Initialize LLM & embeddings
        self.llm = llm
        self.embedding_model = embedding_model
        self.retrievers = {
            "job": job_retriever,
            "course": course_retriever
        }
        self.chat_store = chat_store
        Settings.llm = self.llm
        Settings.embed_model = embedding_model

        # Setup persistent memory
        self.checker = checker
        self.rag_engine = None
        self.smalltalk_engine = None
        self.chat_memory = None

        # Multi-agent debate setup
        self.enable_debate = enable_debate
        self.debate_engine = MultiAgentDebateEngine(llm, debate_config)

    def compose(self, resume, memory, session_id):
        Settings.llm = self.llm
        Settings.embed_model = self.embedding_model

        self.build_prompt(resume=resume)
        self.build_memory(memory, session_id)
        self.build_chat_engine(self.retrievers)

    def build_prompt(self, resume):
        self.resume = resume
        self.rag_prompt = """ 
            You are an intelligent assistant specializing in job matching, job discovery, resume analysis, and career guidance. Your objective is to help users find relevant job opportunities and assess their fit based on job descriptions and their professional background. 

            You have access to:   
            - A vector database of job descriptions and online courses (retrieved based on contextual relevance)   
            - The user's resume or summarized professional experience   

            ### Guidelines for Handling User Queries: 

            1. **Understanding Intent:**   
            - Analyze the user's query to determine whether they are seeking job recommendations, course suggestions, or roadmap guidance. 

            2. **Contextual Query Rephrasing:**   
            - Use relevant job descriptions and resume content to rephrase or clarify the user's query as a specific, standalone question. 

            3. **Job Recommendations:**   
            - If the query involves job recommendations, respond in **bullet points** with the following format: 
            ## Data Engineer 

            **Company Name:** Digital Intellect  
            **Summary:** Role Overview: As a Data Engineer, you will collaborate closely with the client's Data Lead to design, develop, and maintain data architectures that enhance their data platforms.... 
            **URL:** https://www.vietnamworks.com/data-engineer--1906728-jv?source=searchResults&searchType=2&placement=1906728&sortBy=date 

            4. **Course Recommendations or Roadmaps:**   
            - If the query involves courses or roadmaps, respond in **bullet points** with the following format: 

            ## {Course Title} 

            **Skills:** {Skills Learned}   
            **What You Will Learn:** {What the user will learn here}   
            **Description:** {Course Description}   
            **URL:** {Course URL} 

            5. **Response Formatting:**   
            - Ensure all responses are structured in **Markdown format** with appropriate headings for clarity and organization. 
            - Job and course Title MUST be heading like this: ## Job Title 
        """

        self.context_prompt = f""" 
        USER RESUME: 
        {resume} 

        The following is a friendly conversation between a user and an AI assistant. 
        The assistant is talkative and provides lots of specific details from its context. 
        If the assistant does not know the answer to a question, it truthfully says it 
        does not know. 

        Here are the relevant documents for the context: 

        {{context_str}} 

        Instruction: Based on the above documents, provide a detailed answer for the user question below. 
        Answer "don't know" if not present in the document. 
        """

        self.smalltalk_prompt = f'You are a helpful assistant. and here is user resume: \n {resume}'

    def build_tool(self, retriever, tool_name, description):
        tool = RetrieverTool.from_defaults(
            retriever=retriever,
            name=tool_name,
            description=description
        )
        return tool

    def build_chat_engine(self, retrievers):
        job_tool = self.build_tool(retriever=retrievers["job"], tool_name="job retriever tool",
                                   description="Useful for retrieving job-related context")
        course_tool = self.build_tool(retriever=retrievers["course"], tool_name="course retriever tool",
                                      description="Useful for retrieving Handles course and learning path queries. context")

        main_retriever = RouterRetriever(
            selector=LLMSingleSelector.from_defaults(llm=self.llm),
            retriever_tools=[
                job_tool,
                course_tool
            ]
        )

        self.rag_engine = CondensePlusContextChatEngine(
            retriever=main_retriever,
            llm=self.llm,
            system_prompt=self.rag_prompt,
            context_prompt=self.context_prompt,
            memory=self.chat_memory,
        )

        prefix = [ChatMessage(role='system', content=self.smalltalk_prompt)]
        self.smalltalk_engine = SimpleChatEngine(
            llm=self.llm,
            memory=self.chat_memory,
            prefix_messages=prefix,
        )

    def build_memory(self, memory, session_id):
        self.memory = memory
        self.session_id = session_id
        # load if exists
        if memory and len(memory) > 0:
            json_memory = self.process_history()
            try:
                self.chat_store = SimpleChatStore.from_json(
                    json_memory
                )
            except Exception as e:
                print(f"Error initializing chat store from memory: {e}")
                # Initialize empty chat store if loading fails
                self.chat_store = SimpleChatStore()

        self.chat_memory = ChatMemoryBuffer.from_defaults(
            token_limit=self.token_limit,
            chat_store=self.chat_store,
            chat_store_key=self.session_id,
        )

    def process_history(self):
        chat_history = {
            "store": {
                self.session_id: []
            },
            "class_name": "SimpleChatStore"
        }
        for chat_turn in self.memory:
            message = {
                "role": chat_turn["role"],
                'additional_kwargs': {},
                "blocks": [
                    {
                        "block_type": "text",
                        "text": chat_turn["content"]
                    }
                ]
            }
            chat_history["store"][self.session_id].append(message)

        return json.dumps(chat_history)

    async def stream_chat(self, user_input: str, use_debate: bool = None):
        """
        Stream chat with optional multi-agent debate

        Args:
            user_input: The user's input query
            use_debate: Override the default debate setting. If None, uses self.enable_debate
        """
        if not self.rag_engine or not self.smalltalk_engine:
            yield "ERROR: Chat engine not properly initialized."
            return

        # Determine if we should use debate
        should_use_debate = use_debate if use_debate is not None else self.enable_debate

        try:
            if self.checker.is_small_talk(user_input):
                response = self.smalltalk_engine.stream_chat(user_input)
                async for chunk in self.process_streaming_response(response):
                    if chunk:
                        yield chunk
            else:
                if should_use_debate:
                    # Use multi-agent debate for RAG queries
                    async for chunk in self.stream_chat_with_debate(user_input):
                        yield chunk
                else:
                    # Use standard RAG response
                    response = self.rag_engine.stream_chat(user_input)
                    async for chunk in self.process_streaming_response(response):
                        if chunk:
                            yield chunk

        except Exception as e:
            print(f"Error in stream_chat: {str(e)}")
            yield f"ERROR: {str(e)}"

    async def stream_chat_with_debate(self, user_input: str):
        """Stream chat using multi-agent debate for enhanced responses"""

        # First, get the context from retriever
        job_tool = self.build_tool(
            retriever=self.retrievers["job"],
            tool_name="job retriever tool",
            description="Useful for retrieving job-related context"
        )
        course_tool = self.build_tool(
            retriever=self.retrievers["course"],
            tool_name="course retriever tool",
            description="Useful for retrieving course and learning path queries context"
        )

        main_retriever = RouterRetriever(
            selector=LLMSingleSelector.from_defaults(llm=self.llm),
            retriever_tools=[job_tool, course_tool]
        )

        # Retrieve context
        nodes = main_retriever.retrieve(user_input)
        context = "\n\n".join([node.get_content() for node in nodes])

        # Add resume context
        full_context = f"RETRIEVED CONTEXT:\n{context}"

        # Run multi-agent debate
        async for chunk in self.debate_engine.debate(full_context, user_input):
            yield chunk

    async def process_streaming_response(self, response):
        """Process various types of streaming responses."""
        # Handle async generators
        if hasattr(response, '__aiter__'):
            async for token in response:
                if token:
                    text = self.extract_text_from_token(token)
                    if text:
                        yield text
        # Handle sync generators
        elif hasattr(response, '__iter__') and not isinstance(response, str):
            for token in response:
                if token:
                    text = self.extract_text_from_token(token)
                    if text:
                        yield text
        # Handle response objects with generators
        elif hasattr(response, 'response_gen'):
            async for chunk in self.process_streaming_response(response.response_gen):
                yield chunk
        elif hasattr(response, 'content_generator'):
            async for chunk in self.process_streaming_response(response.content_generator):
                yield chunk
        # Handle response objects with text
        elif hasattr(response, 'response'):
            yield response.response
        else:
            # Final fallback
            yield str(response)

    def extract_text_from_token(self, token):
        if isinstance(token, str):
            return token
        elif hasattr(token, 'delta'):
            return token.delta
        elif hasattr(token, 'text'):
            return token.text
        elif hasattr(token, 'content'):
            return token.content
        return None

    def persist_memory(self):
        """
        Returning chat memory in JSON format
        """
        return self.chat_store.json()

    def clear_memory(self):
        if self.chat_memory:
            self.chat_memory.reset()
        self.chat_store = SimpleChatStore()
