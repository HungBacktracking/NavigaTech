# New Project Structure

With the evaluation framework at the root level, your project structure is now:

```
backend/
├── app/                          # Main application
│   ├── api/                      # API endpoints
│   ├── chatbot/                  # RAG components
│   ├── core/                     # Core functionality
│   ├── model/                    # Data models
│   ├── repository/               # Data access
│   ├── services/                 # Business logic
│   └── ...
│
├── evaluation/                   # Evaluation framework (NEW LOCATION)
│   ├── __init__.py
│   ├── dataset_generator.py      # Generate eval datasets
│   ├── evaluator.py             # Main evaluation engine
│   ├── ablation_configs.py      # Ablation study configs
│   ├── rag_adapter.py          # RAG system adapter
│   ├── run_evaluation.py       # CLI runner
│   ├── example_usage.py        # Usage examples
│   ├── requirements.txt        # Evaluation dependencies
│   ├── README.md              # Documentation
│   └── RESEARCH_GUIDE.md      # Academic guide
│
├── migrations/                   # Database migrations
├── docs/                        # Documentation
├── sample_data/                 # Sample data
├── docker-compose.yml
├── requirements.txt             # Main app requirements
└── README.md

```

## Benefits of This Structure

1. **Clear Separation**: Evaluation is clearly separate from the main app
2. **Independent Development**: Can work on evaluation without touching app code
3. **Easier Testing**: Run evaluation from root with simple commands
4. **Better Organization**: Research/evaluation tools separate from production code
5. **Standard Practice**: Most ML projects keep evaluation at root level

## Running Evaluation

From the project root:

```bash
# Quick test
python -m evaluation.run_evaluation --quick-test

# Full evaluation
python -m evaluation.run_evaluation --num-samples 50

# With specific dataset
python -m evaluation.run_evaluation --dataset evaluation_datasets/my_dataset.csv
```

## Import Examples

```python
# In evaluation scripts
from evaluation.dataset_generator import DatasetGenerator
from evaluation.evaluator import HybridRAGEvaluator

# Importing from main app
from app.chatbot.chat_engine import ChatEngine
from app.core.containers.application_container import ApplicationContainer
``` 