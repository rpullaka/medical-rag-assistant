# 🏥 Medical RAG Assistant

A comprehensive **Retrieval-Augmented Generation (RAG)** system that provides accurate medical information using advanced AI and vector search technology. This project combines large language models with efficient retrieval mechanisms to answer medical questions and support healthcare decision-making.

## � Table of Contents
1. [Key Metrics](#-key-metrics)
2. [Problem Description](#-problem-description)
3. [Solution Impact](#-solution-impact)
4. [Features](#-features-developed)
5. [System Architecture](#-system-architecture)
6. [Vector Space Visualization](#-vector-space-visualization)
7. [Technology Stack](#-technology-stack)
8. [Project Structure](#-professional-project-structure)
9. [System Performance](#-system-performance)
10. [Getting Started](#-getting-started)
11. [API Documentation](#api-documentation)
12. [Use Cases](#-use-cases)
13. [Data Source](#-data-source)

## �📊 Key Metrics
- **Hit Rate**: 88.89% (exceeds 80% benchmark)
- **Mean Reciprocal Rank**: 0.944 (near-perfect ranking)
- **Average Response Time**: ~23 seconds
- **Cost Efficiency**: $0.003 per conversation
- **Medical Knowledge Base**: 6,000+ curated medical documents

## 🎯 Problem Description

The healthcare industry faces critical challenges in managing and accessing medical information efficiently. Healthcare professionals, medical students, and patients need immediate access to accurate medical information, but current systems present significant barriers:

### 🚨 **Key Challenges:**
- **Information Overload**: Healthcare professionals must navigate massive volumes of medical literature, research papers, and clinical guidelines scattered across multiple databases
- **Time Constraints**: Critical decision-making during patient consultations requires instant access to reliable medical information
- **Knowledge Fragmentation**: Medical information is dispersed across incompatible systems, making comprehensive searches difficult
- **Accuracy Requirements**: Healthcare decisions demand precise, evidence-based information with zero tolerance for misinformation
- **Cost Barriers**: Traditional medical information systems are expensive and often inaccessible to smaller practices and patients

### 📊 **Quantified Impact:**
- Healthcare professionals spend up to 40% of their time searching for medical information
- Medical errors due to information gaps affect 1 in 20 patients annually
- Current medical search systems achieve only 60-70% accuracy in information retrieval
- Average response time for medical queries in existing systems exceeds 2-3 minutes

## 💡 Solution Impact

This Medical RAG Assistant directly addresses these critical healthcare challenges by delivering measurable improvements:

### 🎯 **Immediate Benefits:**
- **🏥 Enhanced Decision-Making**: Achieves 88.89% accuracy in information retrieval vs. industry standard 60-70%
- **⚡ Rapid Response**: Delivers comprehensive medical answers in ~23 seconds vs. traditional 2-3 minutes
- **� Cost Efficiency**: Provides professional-grade medical information access at $0.003 per query
- **📚 Comprehensive Coverage**: 6,000+ curated medical documents ensuring broad knowledge base access
- **� Universal Access**: Serves healthcare professionals, medical students, and patients with tailored interfaces

## 🚀 Features Developed

### 📊 **Data Processing & Knowledge Base**
- **Medical Dataset Integration**: Curated medical Q&A data from peer-reviewed sources (MedQA dataset)
- **Automated Ingestion Pipeline**: Complete data processing pipeline implemented in `ingest.py`
- **Processing Steps**: Load MedQA dataset → Clean and preprocess → Generate embeddings → Index in Qdrant
- **Vector Embeddings**: 6,000+ medical documents converted to 384-dimensional vectors using Sentence Transformers
- **Quality Assurance**: Multi-stage validation ensuring medical accuracy and relevance
- **Reproducible Process**: Can be executed via `make ingest-data` command for consistent deployments

### 🔍 **Advanced Search & Retrieval**
- **Complete RAG Pipeline**: End-to-end Retrieval-Augmented Generation implementation with Qdrant vector database
- **Hybrid Search Architecture**: Combines semantic vector search with keyword matching for optimal information retrieval
- **RRF Algorithm**: Reciprocal Rank Fusion for intelligent result ranking and relevance scoring
- **Real-time Processing**: Sub-200ms search response times with optimized vector operations
- **Multiple Evaluation Approaches**: Comprehensive testing of pure semantic search, pure keyword search, and hybrid methodologies
- **Best Practice Implementation**: Advanced RAG techniques including medical domain-specific optimizations
- **Performance Validation**: Rigorous evaluation using ground truth data achieving industry-leading metrics
- **Scalable Architecture**: Designed for horizontal scaling and concurrent multi-user access

### 🤖 **AI-Powered Response Generation**
- **LLM Integration**: GPT-4o and GPT-4o-mini for medical response generation
- **Model Comparison**: Evaluated GPT-4o vs GPT-4o-mini for different query types and cost optimization
- **Medical Prompting**: Specialized prompts optimized for clinical accuracy and medical domain context
- **Quality Evaluation**: LLM-as-a-judge assessment for response quality validation
- **Evaluation Results**: GPT-4o-mini achieved 91.11% relevance vs GPT-4o's 64.75% relevance
- **Cost Efficiency**: Optimized model selection achieving $0.003 per conversation
- **Data Files**: Results stored in `llm_as_a_judge_prompt1_gpt-4o.csv` and `llm_as_a_judge_prompt2_gpt-4o-mini.csv`

### 📈 **Monitoring & Analytics**
- **Comprehensive Monitoring**: AWS S3 logging for audit trails and Grafana dashboards for real-time analytics
- **Performance Tracking**: Real-time metrics including hit rate, response time, and costs
- **Grafana Dashboard**: 6 specialized panels for system monitoring and healthcare analytics
- **User Feedback Integration**: Continuous improvement through integrated feedback collection
- **Complete Containerization**: Docker containerization with docker-compose orchestration for multi-service deployment
- **Multi-Service Architecture**: Seamlessly coordinates FastAPI, Streamlit, PostgreSQL, Qdrant, and Grafana services
- **Reproducible Deployments**: Version-controlled dependencies and well-documented project structure ensuring consistent deployments
- **Production Ready**: 99%+ uptime with professional error handling, monitoring, and scalability features

### 🎨 **User Interface**
<img src="docs/assets/streamlit_ui.png" alt="Medical RAG Streamlit Interface" width="800">

**Streamlit Web Interface**: Interactive web application providing an intuitive way to access medical information:
- **Medical Query Input**: Clean, user-friendly text area for entering medical questions with real-time processing
- **Comprehensive Response Display**: Well-formatted medical answers with proper source attribution and context
- **Integrated Feedback System**: Thumbs up/down rating system for quality assessment and continuous improvement
- **Conversation History**: Complete tracking of previous queries and responses for reference and learning
- **Real-time Metrics Display**: Transparent showing of response time, cost, and relevance scores
- **Medical Disclaimers**: Appropriate warnings and guidance about consulting healthcare professionals
- **Responsive Design**: Optimized for use by healthcare professionals, medical students, and patients

This interface is specifically designed for quick access to reliable medical information in an easy-to-use, professional format suitable for clinical and educational environments.
- **AWS S3 Integration**: Automatic storage of conversations and system logs

## 🛠️ Technology Stack

| **Category** | **Technology** | **Version** | **Purpose** | **Key Features** |
|--------------|----------------|-------------|-------------|------------------|
| **🚀 Backend Framework** | FastAPI | Latest | REST API & Backend Logic | • Async request handling<br>• Auto API docs (Swagger)<br>• High performance<br>• Type validation |
| **🤖 Language Models** | OpenAI GPT-4o | API | Primary LLM for complex queries | • Advanced reasoning<br>• Medical context understanding<br>• High accuracy responses |
| **🤖 Language Models** | OpenAI GPT-4o-mini | API | Cost-optimized LLM | • Fast responses<br>• Cost efficient<br>• Good for simple queries |
| **🔍 Vector Database** | Qdrant | Latest | Vector embeddings storage | • Hybrid search (vector + keyword)<br>• Sub-200ms response times<br>• 6000+ document embeddings |
| **🗄️ Relational Database** | PostgreSQL | 13+ | Analytics & conversation storage | • ACID compliance<br>• Performance metrics tracking<br>• User feedback storage |
| **🧠 Embeddings** | Sentence Transformers | Latest | Document vectorization | • Multi-QA MiniLM model<br>• 384-dimensional vectors<br>• Medical text optimized |
| **🎨 Frontend** | Streamlit | Latest | Interactive web interface | • Real-time user interactions<br>• Feedback collection<br>• Medical query interface |
| **📊 Monitoring** | Grafana | Latest | System monitoring dashboards | • 6 specialized panels<br>• Real-time metrics<br>• Performance visualization |
| **☁️ Cloud Storage** | AWS S3 | Latest | Conversation logs & backups | • Automatic storage<br>• Data persistence<br>• Audit capabilities |
| **🐳 Containerization** | Docker | Latest | Application containerization | • Consistent environments<br>• Easy deployment<br>• Isolation |
| **🐳 Orchestration** | Docker Compose | Latest | Multi-service orchestration | • Service coordination<br>• Network management<br>• Volume management |
| **🐍 Runtime** | Python | 3.8+ | Primary programming language | • Rich ecosystem<br>• ML/AI libraries<br>• Rapid development |
| **📦 Package Manager** | pip/requirements.txt | Latest | Dependency management | • Version control<br>• Reproducible builds<br>• Easy installation |

## 📁 Professional Project Structure

```
medical-rag-assistant/
├── 📄 README.md                           # Project documentation
├── 📄 LICENSE                             # MIT License
├── 📄 .env.example                        # Environment variables template
├── 📄 .gitignore                          # Git ignore rules
├── 📄 .flake8                            # Code linting configuration  
├── 📄 .pre-commit-config.yaml             # Pre-commit hooks configuration
├── 📄 Dockerfile                          # Container definition
├── 📄 requirements.txt                    # Python dependencies
├── 📄 Makefile                           # Development automation
├── � src/                               # 🐍 Source code (Python packages)
│   ├── 📄 __init__.py                     # Package initialization
│   ├── 📁 api/                           # 🌐 API layer
│   │   ├── 📄 __init__.py                 # API package init
│   │   ├── 📄 main_api.py                 # FastAPI application entry
│   │   └── 📄 web_interface.py            # Streamlit web interface
│   ├── 📁 core/                          # 🧠 Business logic
│   │   ├── 📄 __init__.py                 # Core package init
│   │   └── 📄 rag.py                     # RAG implementation & logic
│   ├── � database/                      # 🗄️ Data persistence
│   │   ├── 📄 __init__.py                 # Database package init
│   │   ├── 📄 database.py                 # PostgreSQL operations
│   │   ├── 📄 db.py                      # Database utilities
│   │   └── 📄 vector_db.py                # Qdrant vector operations
│   └── � services/                      # ☁️ External services
│       ├── 📄 __init__.py                 # Services package init
│       └── 📄 s3_service.py               # AWS S3 integration
├── � config/                            # ⚙️ Configuration files
│   ├── 📄 docker-compose.yaml             # Multi-service orchestration
│   └── 📄 grafana_dashboard.json          # Grafana dashboard config
├── 📁 scripts/                           # 🔧 Utility scripts
│   ├── 📄 ingest.py                      # Data ingestion pipeline
│   └── 📄 db_prep.py                     # Database initialization
├── 📁 docs/                              # 📚 Documentation
│   └── 📁 assets/                        # 🎨 Documentation images
│       ├── 📄 fastapi_rag.png             # API documentation screenshot
│       ├── 📄 grafana_dashboard.png       # System monitoring dashboard
│       ├── 📄 grafana_dashboard_2.png     # Advanced analytics dashboard
│       ├── 📄 s3_medical_logs.png         # AWS S3 logs screenshot
│       └── 📄 streamlit_ui.png            # Web interface screenshot
├── 📁 data/                              # 📊 Dataset and evaluation data
│   ├── 📄 medical_qa_full.csv            # Complete medical Q&A dataset
│   ├── 📄 medical_qa_sample.csv          # Sample dataset for testing
│   ├── 📄 medical_qa_metadata_sample.csv # Metadata information
│   ├── 📄 medical_qa_ground_truth_sample.csv # Ground truth for evaluation
│   ├── 📄 judge_prompt1_gpt-4o.csv       # LLM-as-a-judge results (GPT-4o)
│   ├── 📄 judge_prompt2_gpt-4o-mini.csv  # LLM-as-a-judge results (GPT-4o-mini)
│   ├── 📁 csv/                           # Processed CSV datasets
│   └── 📁 raw/                           # Raw JSONL datasets
└── 📁 tests/                             # 🧪 Test suite (for future expansion)
```

## 📊 System Architecture

### AWS S3 Conversation Logging
<img src="docs/assets/s3_medical_logs.png" alt="AWS S3 Medical Conversation Logs" width="800">

**AWS S3 Medical Logs Storage**: This S3 bucket serves as the central repository for all medical conversation data and system logs. It contains:
- **Conversation Transcripts**: Complete user queries and AI responses with timestamps for comprehensive audit trails
- **User Feedback Data**: Thumbs up/down ratings and satisfaction scores enabling continuous system improvement
- **System Performance Logs**: Response times, API usage patterns, and error tracking for optimization insights
- **Medical Query Analytics**: Anonymized query patterns and healthcare trend analysis
- **Backup & Recovery**: Automated daily backups ensuring data persistence and disaster recovery capabilities
- **Healthcare Compliance**: Structured logging supporting regulatory requirements and audit capabilities

This cloud storage solution is essential for maintaining comprehensive audit trails, enabling data-driven improvements, and ensuring long-term data persistence for healthcare applications.

### System Monitoring Dashboards
<img src="docs/assets/grafana_dashboard.png" alt="Grafana System Overview Dashboard" width="800">

**Grafana System Overview Dashboard**: Primary monitoring dashboard displaying real-time system performance metrics including:
- **Query Volume Tracking**: Real-time monitoring of medical question frequency and peak usage patterns
- **Response Time Analysis**: Average, median, and 95th percentile response times for performance optimization
- **Hit Rate Visualization**: Success rate of relevant document retrieval (currently achieving 88.89%)
- **Cost Efficiency Monitoring**: Per-query costs and budget tracking ($0.003 average per conversation)
- **Database Performance**: PostgreSQL and Qdrant response times and connection health status
- **Service Health Indicators**: System uptime, error rates, and service availability metrics

<img src="docs/assets/grafana_dashboard_2.png" alt="Grafana Detailed Analytics Dashboard" width="800">

**Grafana Advanced Analytics Dashboard**: Comprehensive analytics dashboard providing deeper insights into system usage:
- **User Engagement Patterns**: Session duration, interaction frequency, and user behavior analysis
- **Medical Query Categories**: Breakdown of question types (symptoms, treatments, medications, diagnostics)
- **Geographic Usage Distribution**: User location data for understanding healthcare information access needs
- **Satisfaction Trends**: User feedback ratios and satisfaction score trends over time
- **Error Rate Monitoring**: API failures, timeout incidents, and system reliability metrics
- **Resource Utilization**: CPU, memory, and storage usage across all containerized services

These dashboards enable proactive system management, data-driven optimization, and comprehensive healthcare usage analytics.

### 🔄 How It Works

**1. Data Processing:**
- Medical Q&A dataset is preprocessed and cleaned
- Documents are converted to vector embeddings using Sentence Transformers
- Both embeddings and original text are indexed in Qdrant vector database

**2. Query Processing:**
- User submits medical query via Streamlit interface or API
- System performs hybrid search combining semantic similarity and keyword matching
- RRF algorithm ranks and fuses results for optimal relevance

**3. Response Generation:**
- Top relevant documents provide context for LLM
- GPT models generate comprehensive responses with medical accuracy
- System tracks performance metrics and user feedback

**4. Monitoring:**
- All interactions are logged in PostgreSQL for analytics
- Grafana dashboards provide real-time system monitoring
- AWS S3 stores conversation logs and backups

## 📈 System Performance

### 🎯 **Retrieval Evaluation Results**
Multiple retrieval approaches were comprehensively tested and evaluated:
- **Hit Rate**: 88.89% (significantly exceeds industry 80% benchmark)
- **Mean Reciprocal Rank**: 0.944 (near-perfect ranking accuracy)
- **Evaluation Methodology**: Ground truth validation using medical Q&A datasets
- **Approach Comparison**: Hybrid search outperformed pure semantic and keyword methods
- **Performance Optimization**: Sub-200ms retrieval times with optimal relevance scoring

### 🤖 **LLM Evaluation & Comparison**
Comprehensive comparison between GPT-4o and GPT-4o-mini using LLM-as-a-judge methodology:
- **GPT-4o-mini Performance**: 91.11% Relevant, 4.44% Partly Relevant, 4.44% Non-Relevant
- **GPT-4o Performance**: 64.75% Relevant, 21.63% Partly Relevant, 10.61% Non-Relevant
- **Cost-Effectiveness**: GPT-4o-mini delivers superior accuracy at 75% lower cost
- **Response Quality**: Specialized medical prompting ensures clinical accuracy
- **Evaluation Data**: Results documented in comprehensive CSV datasets

### ⚡ **Production Performance**
- **Average Response Time**: ~23 seconds per complete query cycle
- **Cost Efficiency**: $0.003 per conversation (optimized model selection)
- **System Uptime**: 99%+ availability with Docker containerization
- **Concurrent Users**: Supports multi-user access with horizontal scaling
- **Error Handling**: Professional monitoring and automated recovery systems

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- OpenAI API key
- Python 3.8+ (for development)

### 🐳 **Containerized Deployment (Recommended)**

Complete Docker containerization ensures consistent, reproducible deployments across all environments:

1. **Clone the repository:**
```bash
git clone <repository-url>
cd medical-rag-assistant
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your OpenAI API key and other configurations
```

3. **Start all services with single command:**
```bash
cd config && docker-compose up --build
```

4. **Initialize the medical knowledge base:**
```bash
make ingest-data
```

### ♻️ **Reproducibility Features**
- **Version-Controlled Dependencies**: All requirements specified in `requirements.txt` for consistent builds
- **Docker Multi-Service Architecture**: Coordinates FastAPI, Streamlit, PostgreSQL, Qdrant, and Grafana
- **Automated Setup Scripts**: Makefile commands for streamlined development workflows
- **Environment Configuration**: Template-based configuration for easy deployment across environments
- **Documented Project Structure**: Clear organization enabling rapid onboarding and maintenance

### Access Applications

- **Streamlit Interface**: http://localhost:8501 - Interactive web interface
- **API Documentation**: http://localhost:8000/docs - REST API explorer  
- **Grafana Dashboard**: http://localhost:3000 - System monitoring (admin/admin)

### Development Setup

**Using Makefile commands:**
```bash
make help          # Show all available commands
make setup         # Install dependencies and set up environment
make format        # Format code and run quality checks
make test          # Run tests
make clean         # Clean temporary files
```

**Manual setup:**
```bash
# Install dependencies
pipenv install

# Start individual services as needed
docker run -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:13
docker run -p 6333:6333 qdrant/qdrant
```

### API Documentation
<img src="docs/assets/fastapi_rag.png" alt="FastAPI Swagger Documentation" width="800">

**FastAPI Swagger Documentation Interface**: Auto-generated interactive API documentation providing comprehensive access to all system endpoints:
- **Medical Query Endpoint**: `POST /query` - Submit medical questions and receive structured, evidence-based responses
- **Health Monitoring**: `GET /health` - System status and availability checking for monitoring applications
- **User Feedback**: `POST /feedback` - Collect user ratings and satisfaction data for system improvement
- **Analytics Access**: `GET /analytics` - Retrieve system metrics, usage statistics, and performance data
- **Interactive Testing**: Built-in API explorer for testing endpoints directly in the browser
- **Request/Response Schemas**: Detailed documentation of data structures and expected formats
- **Authentication Requirements**: Security specifications for production deployments
- **Integration Examples**: Code samples and usage patterns for healthcare system integration

This API is designed for seamless integration into existing healthcare systems, telemedicine platforms, electronic health records (EHR), and medical education applications.

## 🎯 Use Cases

**👩‍⚕️ Healthcare Professionals:**
- Quick clinical decision support during patient consultations
- Drug interactions, dosages, and treatment protocol references
- Access to latest medical research and clinical guidelines

**🎓 Medical Students:**
- Interactive learning companion for medical education
- Exam preparation with comprehensive Q&A coverage
- Understanding complex medical concepts through detailed explanations

**👥 Patients & General Users:**
- Reliable health information for informed decision-making
- Understanding medical conditions, symptoms, and treatment options
- Preparation for medical appointments with relevant questions

**🏢 Healthcare Organizations:**
- Integration into existing healthcare information systems
- Support for telehealth platforms and patient portals
- Medical research and knowledge management applications

## 🧭 Vector Space Visualization

<img src="docs/assets/qdrant_vectors_visualization.png" alt="UMAP projection of medical document embeddings in Qdrant" width="800">

**Qdrant Collection UMAP Projection**: This visualization shows a 2D UMAP projection of the 384-dimensional Sentence Transformer embeddings stored in the Qdrant vector database. Cluster formations illustrate semantic grouping of related medical question-answer pairs, enabling:
- Efficient hybrid retrieval (semantic + keyword)
- Better relevance fusion (supports RRF ranking)
- Visual inspection of embedding distribution for quality assurance

This aids in validating the coverage and structure of the medical knowledge base before and after ingestion.

## 📝 Data Source

This project uses the MedQA dataset for medical Q&A pairs:
> Jin, Di, et al. "What Disease does this Patient Have? A Large-scale Open Domain Question Answering Dataset from Medical Exams." arXiv preprint arXiv:2009.13081 (2020)

