"""Curated skill taxonomy used by the deterministic analysis engine.

The taxonomy is intentionally explicit.  It makes matching behavior auditable,
handles common aliases, and avoids sending resume content to a third party.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SkillDefinition:
    name: str
    category: str
    aliases: tuple[str, ...]


SKILL_TAXONOMY: tuple[SkillDefinition, ...] = (
    SkillDefinition("Python", "Programming", ("python",)),
    SkillDefinition("Java", "Programming", ("java",)),
    SkillDefinition("JavaScript", "Programming", ("javascript", "js")),
    SkillDefinition("TypeScript", "Programming", ("typescript",)),
    SkillDefinition("C++", "Programming", ("c++",)),
    SkillDefinition("C#", "Programming", ("c#", "c sharp")),
    SkillDefinition("R", "Programming", ("r", "r programming")),
    SkillDefinition("Go", "Programming", ("golang", "go language")),
    SkillDefinition("Scala", "Programming", ("scala",)),
    SkillDefinition("SQL", "Programming", ("sql", "structured query language")),
    SkillDefinition("Bash", "Programming", ("bash", "shell scripting")),
    SkillDefinition("Machine Learning", "AI & Data", ("machine learning", "ml")),
    SkillDefinition("Deep Learning", "AI & Data", ("deep learning",)),
    SkillDefinition("Natural Language Processing", "AI & Data", ("natural language processing", "nlp")),
    SkillDefinition("Computer Vision", "AI & Data", ("computer vision",)),
    SkillDefinition("Generative AI", "AI & Data", ("generative ai", "genai", "gen ai")),
    SkillDefinition("Large Language Models", "AI & Data", ("large language model", "large language models", "llm", "llms")),
    SkillDefinition("RAG", "AI & Data", ("retrieval augmented generation", "retrieval-augmented generation", "rag")),
    SkillDefinition("LangChain", "AI & Data", ("langchain",)),
    SkillDefinition("TensorFlow", "AI & Data", ("tensorflow",)),
    SkillDefinition("PyTorch", "AI & Data", ("pytorch",)),
    SkillDefinition("scikit-learn", "AI & Data", ("scikit-learn", "sklearn", "scikit learn")),
    SkillDefinition("pandas", "AI & Data", ("pandas",)),
    SkillDefinition("NumPy", "AI & Data", ("numpy",)),
    SkillDefinition("Apache Spark", "AI & Data", ("apache spark", "pyspark", "spark")),
    SkillDefinition("Hadoop", "AI & Data", ("hadoop",)),
    SkillDefinition("Databricks", "AI & Data", ("databricks",)),
    SkillDefinition("Airflow", "Data Engineering", ("apache airflow", "airflow")),
    SkillDefinition("dbt", "Data Engineering", ("dbt", "data build tool")),
    SkillDefinition("ETL", "Data Engineering", ("etl", "extract transform load", "extract, transform, load")),
    SkillDefinition("AWS", "Cloud & DevOps", ("aws", "amazon web services")),
    SkillDefinition("Azure", "Cloud & DevOps", ("microsoft azure", "azure")),
    SkillDefinition("Google Cloud", "Cloud & DevOps", ("google cloud platform", "google cloud", "gcp")),
    SkillDefinition("Docker", "Cloud & DevOps", ("docker", "containerization")),
    SkillDefinition("Kubernetes", "Cloud & DevOps", ("kubernetes", "k8s")),
    SkillDefinition("Terraform", "Cloud & DevOps", ("terraform",)),
    SkillDefinition("CI/CD", "Cloud & DevOps", ("ci/cd", "continuous integration", "continuous delivery")),
    SkillDefinition("Git", "Cloud & DevOps", ("git", "github", "gitlab")),
    SkillDefinition("Linux", "Cloud & DevOps", ("linux", "unix")),
    SkillDefinition("PostgreSQL", "Databases", ("postgresql", "postgres")),
    SkillDefinition("MySQL", "Databases", ("mysql",)),
    SkillDefinition("SQL Server", "Databases", ("sql server", "mssql")),
    SkillDefinition("Oracle", "Databases", ("oracle database", "oracle db")),
    SkillDefinition("MongoDB", "Databases", ("mongodb", "mongo db")),
    SkillDefinition("Redis", "Databases", ("redis",)),
    SkillDefinition("Snowflake", "Databases", ("snowflake",)),
    SkillDefinition("BigQuery", "Databases", ("bigquery", "big query")),
    SkillDefinition("Redshift", "Databases", ("amazon redshift", "redshift")),
    SkillDefinition("ChromaDB", "Databases", ("chromadb", "chroma db")),
    SkillDefinition("Pinecone", "Databases", ("pinecone",)),
    SkillDefinition("Elasticsearch", "Databases", ("elasticsearch", "elastic search")),
    SkillDefinition("FastAPI", "Backend & Web", ("fastapi",)),
    SkillDefinition("Django", "Backend & Web", ("django",)),
    SkillDefinition("Flask", "Backend & Web", ("flask",)),
    SkillDefinition("REST APIs", "Backend & Web", ("rest api", "rest apis", "restful api", "restful services")),
    SkillDefinition("GraphQL", "Backend & Web", ("graphql",)),
    SkillDefinition("Node.js", "Backend & Web", ("node.js", "nodejs")),
    SkillDefinition("React", "Backend & Web", ("react.js", "reactjs", "react")),
    SkillDefinition("Streamlit", "Backend & Web", ("streamlit",)),
    SkillDefinition("Power BI", "Analytics", ("power bi", "powerbi")),
    SkillDefinition("Tableau", "Analytics", ("tableau",)),
    SkillDefinition("Excel", "Analytics", ("microsoft excel", "excel")),
    SkillDefinition("Statistics", "Analytics", ("statistics", "statistical analysis")),
    SkillDefinition("A/B Testing", "Analytics", ("a/b testing", "ab testing", "experimentation")),
    SkillDefinition("Data Visualization", "Analytics", ("data visualization", "data visualisation")),
    SkillDefinition("Agile", "Collaboration", ("agile",)),
    SkillDefinition("Scrum", "Collaboration", ("scrum",)),
    SkillDefinition("Stakeholder Management", "Collaboration", ("stakeholder management", "stakeholder communication")),
    SkillDefinition("Leadership", "Collaboration", ("leadership", "team lead")),
    SkillDefinition("Communication", "Collaboration", ("communication skills", "written and verbal communication")),
    SkillDefinition("Problem Solving", "Collaboration", ("problem solving", "problem-solving")),
)
