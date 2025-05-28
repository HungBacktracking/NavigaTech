# Hybrid RAG System Implementation Guide

## Overview

This guide documents the implementation of a Hybrid RAG (Retrieval-Augmented Generation) system that combines embedding-based vector search with graph-based knowledge retrieval using Neo4j.

## Architecture

### Components

1. **Embedding-based Retriever**
   - Uses Qdrant vector database for job descriptions
   - Uses pre-indexed course data with HuggingFace embeddings
   - Supports hybrid search (dense + sparse vectors)

2. **Graph-based Retriever (Neo4j)**
   - Stores structured relationships between entities
   - Enables traversal-based queries
   - Captures semantic relationships between jobs, courses, skills, and organizations

3. **Hybrid Retriever**
   - Implements Reciprocal Rank Fusion (RRF) for result merging
   - Configurable weights for each retrieval method
   - Uses Cohere reranker for final result optimization

## Graph Schema

### Nodes
- **Career**: Job postings with properties (id, title, url, location, salary, description)
- **Course**: Online courses with properties (title, url, website, organization, level, description)
- **Organization**: Companies and educational institutions
- **Industry**: Industry categories
- **Competency Nodes**:
  - ProgrammingLanguage
  - Framework
  - Platform
  - Tool
  - Knowledge
  - SoftSkill
  - Certification

### Relationships
- `(Career)-[:REQUIRES]->(Competency)`: Jobs require specific skills
- `(Course)-[:TEACHES]->(Competency)`: Courses teach specific skills
- `(Career)-[:IN_INDUSTRY]->(Industry)`: Job belongs to industry
- `(Organization)-[:COLLABORATES_WITH]->(Course)`: Organization offers course

## Setup Instructions

### 1. Neo4j Setup

```bash
# Using Docker
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

### 2. Environment Variables

Add to `.env`:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
```

### 3. Data Ingestion

```bash
# Run the ingestion script
python app/scripts/ingest_graph_data.py
```

## Usage

### Query Examples

1. **Job Search by Skills**
   - "Find jobs requiring Python and AWS"
   - Graph retriever finds jobs with REQUIRES relationships to these skills
   - Embedding retriever performs semantic search

2. **Course Recommendations**
   - "Courses to learn machine learning"
   - Graph retriever traverses TEACHES relationships
   - Embedding retriever finds semantically similar courses

3. **Skill Gap Analysis**
   - "What skills do I need for data engineer roles?"
   - Graph retriever analyzes required competencies
   - Results combined with embedding-based context

## Best Practices

### 1. Query Optimization
- Use graph queries for structured relationships
- Use embeddings for semantic similarity
- Balance weights based on query type

### 2. Graph Design
- Keep competency nodes normalized
- Use consistent naming conventions
- Create indices on frequently queried properties

### 3. Hybrid Retrieval Tuning
- **Embedding weight**: 0.6 (default) - Better for semantic queries
- **Graph weight**: 0.4 (default) - Better for structured queries
- Adjust based on your use case

### 4. Performance Tips
- Batch ingestion operations
- Use async operations where possible
- Cache frequently accessed graph patterns
- Limit traversal depth for complex queries

## Advanced Features

### 1. Dynamic Weight Adjustment
The system can adjust retrieval weights based on query intent:
- Job searches: Increase graph weight
- General questions: Increase embedding weight

### 2. Path-based Recommendations
Graph retriever can find learning paths:
```cypher
MATCH path = (c1:Course)-[:TEACHES]->(s:Skill)<-[:REQUIRES]-(j:Career)
WHERE c1.title = "Python Basics"
RETURN path
```

### 3. Skill Clustering
Identify related skills through graph traversal:
```cypher
MATCH (s1:Skill)<-[:REQUIRES]-(j:Career)-[:REQUIRES]->(s2:Skill)
WHERE s1.name = "Python"
RETURN s2, COUNT(j) as co_occurrence
ORDER BY co_occurrence DESC
```

## Monitoring and Debugging

### 1. Check Graph Connectivity
```cypher
MATCH (n) RETURN labels(n), COUNT(n)
```

### 2. Verify Relationships
```cypher
MATCH ()-[r]->() RETURN type(r), COUNT(r)
```

### 3. Query Performance
- Monitor retrieval times for each component
- Log RRF scores to understand fusion behavior
- Track reranker impact on results

## Future Enhancements

1. **Graph Embeddings**: Incorporate node2vec for graph-aware embeddings
2. **Query Understanding**: Use LLM to decompose complex queries
3. **Adaptive Fusion**: Learn optimal weights from user feedback
4. **Graph Analytics**: Add PageRank for entity importance
5. **Temporal Modeling**: Track skill trends over time 