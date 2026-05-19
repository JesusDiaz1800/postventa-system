
import sys
import time
from notebooklm_mcp.auth import load_cached_tokens
from notebooklm_mcp.api_client import NotebookLMClient

# ==================================================================================
# NOTEBOOK 1: UNREACHABLE ENTERPRISE ARCHITECTURE (2026)
# Focus: Scalability, Event-Driven, Clean Architecture, High Availability
# ==================================================================================
NB1_TITLE = "01. Arquitectura Empresarial Inalcanzable (2026)"
NB1_SOURCES = [
    # Principios Fundamentales & Clean Arch
    "https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html",
    "https://martinfowler.com/architecture/",
    "https://martinfowler.com/articles/microservices.html",
    
    # Event-Driven & Scalability
    "https://aws.amazon.com/event-driven-architecture/", 
    "https://cloud.google.com/architecture/event-driven-architecture",
    "https://microservices.io/patterns/index.html",
    
    # Modern Patterns (Outbox, Sagas, CQRS)
    "https://microservices.io/patterns/data/transactional-outbox.html",
    "https://microservices.io/patterns/data/saga.html",
    "https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs",
    
    # 12-Factor Moderno
    "https://12factor.net/",
    
    # High Performance
    "https://highscalability.com/",
]

# ==================================================================================
# NOTEBOOK 2: AI ENGINEERING & AGENTS REVOLUTION
# Focus: Building Autonomous Agents, RAG, LLM Ops, LangGraph
# ==================================================================================
NB2_TITLE = "02. AI Engineering & Revolución de Agentes"
NB2_SOURCES = [
    # Frameworks de Agentes (State of Art)
    "https://langchain-ai.github.io/langgraph/",
    "https://microsoft.github.io/autogen/",
    "https://www.crewai.com/",
    
    # Modelos & Capacidades
    "https://www.anthropic.com/news/claude-3-5-sonnet",
    "https://openai.com/index/gpt-4o/",
    "https://deepmind.google/technologies/gemini/",
    
    # RAG & Vector DBs
    "https://www.pinecone.io/learn/retrieval-augmented-generation/",
    "https://weaviate.io/blog/what-is-vector-database",
    
    # Agentic Workflows & Patterns
    "https://www.deeplearning.ai/the-batch/issue-242/", # Andrew Ng on Agentic Workflows
    "https://arxiv.org/abs/2303.11366", # Reflexion paper (Self-reflection)
    
    # Tools & IDEs
    "https://www.cursor.com/blog",
    "https://codeium.com/windsurf",
]

# ==================================================================================
# NOTEBOOK 3: MODERN DEVOPS & PLATFORM ENGINEERING
# Focus: Kubernetes, CI/CD, Observability, IaC
# ==================================================================================
NB3_TITLE = "03. Modern DevOps & Platform Engineering (2026)"
NB3_SOURCES = [
    # Platform Engineering
    "https://platformengineering.org/blog/what-is-platform-engineering",
    
    # Kubernetes & Cloud Native
    "https://kubernetes.io/docs/concepts/overview/what-is-kubernetes/",
    "https://mp.weixin.qq.com/s/0j4e7j6q1q1q1q1q1q1q1q", # Placeholder for high quality K8s
    "https://argoproj.github.io/argo-cd/", # GitOps Gold Standard
    
    # CI/CD & Observability
    "https://github.com/features/actions", # GitHub Actions logic
    "https://opentelemetry.io/", # Industry standard observability
    "https://sre.google/sre-book/table-of-contents/", # The Bible of Reliability
    
    # Infrastructure as Code
    "https://www.terraform.io/intro",
    "https://www.pulumi.com/",
]

# ==================================================================================
# NOTEBOOK 4: PRODUCT MANAGEMENT & STRATEGY FOR AI
# Focus: Agile, User Centricity, AI Product Lifecycle
# ==================================================================================
NB4_TITLE = "04. Estrategia de Producto & Gestión AI"
NB4_SOURCES = [
    # Product Frameworks
    "https://www.ycombinator.com/library", # Startup & Product wisdom
    "https://www.atlassian.com/agile",
    
    # AI Product Specifics
    "https://pair.withgoogle.com/", # People + AI Research (UX for AI)
    "https://a16z.com/ai/", # Trends & Strategy
    
    # Design & UX
    "https://m3.material.io/",
    "https://www.nielsenngroup.com/topics/artificial-intelligence/",
]
# ==================================================================================
# NOTEBOOK 5: AUTOMATIZACIÓN AVANZADA CON N8N (2025)
# Focus: AI Agents, Workflows, Integrations, Best Practices
# ==================================================================================
NB5_TITLE = "05. Automatización Avanzada con n8n (2025)"
NB5_SOURCES = [
    # Official & Core
    "https://n8n.io/blog/introducing-n8n-ai-agents/", 
    "https://docs.n8n.io/ai/agents/",
    
    # Advanced Patterns
    "https://n8n.io/workflows/categories/ai/", # N8n AI Workflow Templates
    "https://blog.langchain.dev/automating-workflows-with-langchain-and-n8n/", # LangChain Integration
    
    # Community & Tutorials (High Quality)
    "https://www.youtube.com/@n8n-io", # Official Channel (Often best for new features)
    "https://medium.com/@n8n_io",
    
    # Specific Architectures
    "https://docs.n8n.io/scaling/scaling-n8n/", # Scaling for Enterprise
    "https://docs.n8n.io/security/", # Security Best Practices
]
# ==================================================================================
# NOTEBOOK 6: CALIDAD, TESTING & FIABILIDAD EXTREMA (2026)
# Focus: QA Automation, SRE, Observability, Debugging
# ==================================================================================
NB6_TITLE = "06. Calidad, Testing & Fiabilidad Extrema (2026)"
NB6_SOURCES = [
    # Modern Testing Strategy (Shift-Left/Right)
    "https://playwright.dev/docs/intro", # modern E2E standard
    "https://docs.cypress.io/guides/overview/why-cypress",
    "https://k6.io/docs/", # Performance testing as code
    
    # SRE & Reliability Engineering
    "https://sre.google/books/", # The source of truth
    "https://landing.google.com/sre/sre-book/chapters/service-level-objectives/",
    "https://www.atlassian.com/incident-management/devops/sre",
    
    # Observability & Debugging
    "https://opentelemetry.io/docs/",
    "https://www.jaegertracing.io/docs/latest/", 
    
    # Code Quality & Technical Debt
    "https://www.sonarsource.com/knowledge/code-quality/",
    "https://martinfowler.com/articles/technicalDebt.html",
    
    # Checklists & Best Practices
    "https://github.com/checklists/checklist", # Comprehensive engineering checklists
    "https://12factor.net/", # Re-emphasizing for stability
]

ALL_NOTEBOOKS = [
    (NB1_TITLE, NB1_SOURCES),
    (NB2_TITLE, NB2_SOURCES),
    (NB3_TITLE, NB3_SOURCES),
    (NB4_TITLE, NB4_SOURCES),
    (NB5_TITLE, NB5_SOURCES),
    (NB6_TITLE, NB6_SOURCES),
]

def get_or_create_notebook(client, title):
    """Find existing notebook by title or create new one."""
    print(f"[*] Checking for notebook: '{title}'...")
    try:
        notebooks = client.list_notebooks()
    except Exception as e:
        print(f"    [ERROR] Listing failed: {e}")
        return None

    for nb in notebooks:
        if nb.title == title:
            print(f"    -> Found existing ID: {nb.id}")
            return nb.id
    
    print(f"    -> Not found. Creating new...")
    nb = client.create_notebook(title)
    if nb:
        print(f"    -> Created with ID: {nb.id}")
        return nb.id
    return None

def populate_notebook(client, notebook_id, sources):
    try:
        current_sources = client.get_notebook_sources_with_types(notebook_id)
        current_urls = [s.get('url') for s in current_sources if s.get('url')]
    except Exception:
        current_urls = []

    for url in sources:
        if url in current_urls:
            print(f"    -> Skipping existing source: {url}")
            continue

        print(f"    -> Adding source: {url}")
        try:
            client.add_url_source(notebook_id, url)
            print("       [OK]")
            time.sleep(3) # Polite delay
        except Exception as e:
            print(f"       [FAILED] {e}")

def main():
    print("Loading cached tokens...")
    tokens = load_cached_tokens()
    if not tokens:
        print("No tokens found! Please authenticate first.")
        sys.exit(1)

    client = NotebookLMClient(
        cookies=tokens.cookies,
        csrf_token=tokens.csrf_token,
        session_id=tokens.session_id
    )
    
    for title, sources in ALL_NOTEBOOKS:
        print(f"\n--- PROCESSING: {title} ---")
        nb_id = get_or_create_notebook(client, title)
        if nb_id:
            populate_notebook(client, nb_id, sources)
    
    print("\n[=] ALL NOTEBOOKS PROCESSED.")

if __name__ == "__main__":
    main()
