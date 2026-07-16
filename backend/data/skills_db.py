"""
skills_db.py
------------
Deterministic knowledge base for CareerCopilot AI.

This is what makes resume analysis, ATS scoring, role matching and the
learning roadmap ACCURATE and CONSISTENT (same resume -> same result),
instead of depending entirely on an LLM mock response.

Contains:
- SKILL_ALIASES: normalizes variant spellings/abbreviations to one canonical skill
- ROLES: canonical job roles -> required + nice-to-have skills
- RESOURCES: canonical skill -> real learning resources (docs + YouTube search + course)
"""

import re

# Canonical skill -> list of ways it might appear in a resume (lowercase)
SKILL_ALIASES = {
    "Python": ["python", "py"],
    "Java": ["java"],
    "C++": ["c++", "cpp"],
    "C": [" c ", "c programming"],
    "JavaScript": ["javascript", "js", "es6"],
    "TypeScript": ["typescript", "ts"],
    "SQL": ["sql", "mysql", "postgresql", "postgres", "sqlite", "t-sql", "pl/sql"],
    "NoSQL": ["nosql", "mongodb", "dynamodb", "cassandra"],
    "HTML/CSS": ["html", "css", "html5", "css3"],
    "React": ["react", "reactjs", "react.js"],
    "Angular": ["angular", "angularjs"],
    "Vue": ["vue", "vuejs", "vue.js"],
    "Node.js": ["node.js", "nodejs", "node js", "express.js", "express"],
    "Django": ["django"],
    "Flask": ["flask"],
    "FastAPI": ["fastapi"],
    "Spring Boot": ["spring boot", "spring framework", "springboot"],
    "REST API": ["rest api", "restful", "rest apis", "api development"],
    "Git": ["git", "github", "gitlab", "version control"],
    "Docker": ["docker", "containerization"],
    "Kubernetes": ["kubernetes", "k8s"],
    "AWS": ["aws", "amazon web services", "ec2", "s3", "lambda"],
    "Azure": ["azure", "microsoft azure"],
    "GCP": ["gcp", "google cloud"],
    "CI/CD": ["ci/cd", "cicd", "jenkins", "github actions", "continuous integration"],
    "Linux": ["linux", "unix", "shell scripting", "bash"],
    "Machine Learning": ["machine learning", "ml", "scikit-learn", "sklearn"],
    "Deep Learning": ["deep learning", "neural network", "cnn", "rnn", "tensorflow", "pytorch", "keras"],
    "NLP": ["nlp", "natural language processing", "spacy", "nltk", "llm", "transformers"],
    "Data Analysis": ["data analysis", "data analytics", "data analyst"],
    "Data Visualization": ["data visualization", "tableau", "power bi", "powerbi", "matplotlib", "seaborn"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Excel": ["excel", "ms excel", "spreadsheets", "vlookup", "pivot table"],
    "Statistics": ["statistics", "statistical analysis", "hypothesis testing"],
    "Big Data": ["big data", "spark", "hadoop", "pyspark"],
    "Data Structures & Algorithms": ["data structures", "algorithms", "dsa"],
    "OOP": ["object oriented", "oop", "object-oriented"],
    "Testing": ["unit testing", "test automation", "selenium", "pytest", "junit", "qa testing"],
    "Figma": ["figma", "adobe xd", "sketch"],
    "UI/UX Design": ["ui/ux", "ui design", "ux design", "user experience", "wireframing", "prototyping"],
    "Product Management": ["product management", "product manager", "roadmapping", "user stories"],
    "Project Management": ["project management", "scrum", "agile", "jira", "kanban", "pmp"],
    "Digital Marketing": ["digital marketing", "seo", "sem", "google ads", "social media marketing"],
    "Content Writing": ["content writing", "copywriting", "content strategy"],
    "Communication": ["communication", "public speaking", "presentation skills"],
    "Leadership": ["leadership", "team lead", "mentoring", "people management"],
    "Problem Solving": ["problem solving", "analytical skills", "critical thinking"],
    "Android Development": ["android", "android studio", "android sdk"],
    "Kotlin": ["kotlin"],
    "iOS Development": ["ios", "swift", "swiftui", "xcode"],
    "Cybersecurity": ["cybersecurity", "penetration testing", "network security", "ethical hacking"],
    "Networking": ["networking", "computer networks", "tcp/ip", "network administration", "ccna"],
    "Blockchain": ["blockchain", "solidity", "web3", "smart contracts"],
    "R": [" r programming", "r language"],
    "Power BI": ["power bi", "powerbi"],
    "Financial Modeling": ["financial modeling", "valuation", "equity research"],
    "Accounting": ["accounting", "bookkeeping", "tally", "gaap"],
}

def _all_canonical_skills():
    return list(SKILL_ALIASES.keys())

# role -> (required core skills, nice-to-have skills)
ROLES = {
    "Data Analyst": {
        "required": ["SQL", "Excel", "Data Analysis", "Statistics", "Data Visualization"],
        "nice_to_have": ["Python", "Power BI", "Pandas"],
    },
    "Data Scientist": {
        "required": ["Python", "Machine Learning", "Statistics", "SQL", "Pandas"],
        "nice_to_have": ["Deep Learning", "NLP", "Big Data", "Data Visualization"],
    },
    "Machine Learning Engineer": {
        "required": ["Python", "Machine Learning", "Deep Learning", "Data Structures & Algorithms"],
        "nice_to_have": ["Docker", "AWS", "NLP", "Big Data"],
    },
    "Backend Developer": {
        "required": ["Python", "SQL", "REST API", "Git", "Data Structures & Algorithms"],
        "nice_to_have": ["Django", "FastAPI", "Docker", "AWS", "Node.js"],
    },
    "Frontend Developer": {
        "required": ["JavaScript", "HTML/CSS", "React", "Git"],
        "nice_to_have": ["TypeScript", "Vue", "Angular", "UI/UX Design"],
    },
    "Full Stack Developer": {
        "required": ["JavaScript", "HTML/CSS", "React", "Node.js", "SQL", "Git"],
        "nice_to_have": ["Docker", "AWS", "TypeScript", "REST API"],
    },
    "Java Developer": {
        "required": ["Java", "OOP", "SQL", "Data Structures & Algorithms", "Git"],
        "nice_to_have": ["Spring Boot", "REST API", "Docker"],
    },
    "DevOps Engineer": {
        "required": ["Linux", "Docker", "CI/CD", "Git"],
        "nice_to_have": ["Kubernetes", "AWS", "Azure", "GCP"],
    },
    "Cloud Engineer": {
        "required": ["AWS", "Linux", "CI/CD"],
        "nice_to_have": ["Docker", "Kubernetes", "Azure", "GCP"],
    },
    "Android Developer": {
        "required": ["Android Development", "Java", "OOP", "Git"],
        "nice_to_have": ["Kotlin", "REST API", "Testing"],
    },
    "QA / Test Engineer": {
        "required": ["Testing", "SQL", "Problem Solving"],
        "nice_to_have": ["Python", "CI/CD", "Git"],
    },
    "Product Manager": {
        "required": ["Product Management", "Communication", "Project Management", "Problem Solving"],
        "nice_to_have": ["SQL", "Data Analysis", "UI/UX Design"],
    },
    "UI/UX Designer": {
        "required": ["UI/UX Design", "Figma", "Communication"],
        "nice_to_have": ["HTML/CSS", "Problem Solving"],
    },
    "Digital Marketing Executive": {
        "required": ["Digital Marketing", "Content Writing", "Communication"],
        "nice_to_have": ["Data Analysis", "Excel"],
    },
    "Business Analyst": {
        "required": ["Excel", "SQL", "Data Analysis", "Communication", "Problem Solving"],
        "nice_to_have": ["Power BI", "Project Management"],
    },
    "Cybersecurity Analyst": {
        "required": ["Cybersecurity", "Linux", "Problem Solving"],
        "nice_to_have": ["Python", "AWS", "Networking"],
    },
    "Financial Analyst": {
        "required": ["Excel", "Financial Modeling", "Statistics", "Communication"],
        "nice_to_have": ["SQL", "Data Visualization", "Accounting"],
    },
}

# canonical skill -> curated, real, clickable learning resources
RESOURCES = {
    "Python": [
        ("Python Official Docs", "https://docs.python.org/3/tutorial/"),
        ("YouTube: Python Full Course", "https://www.youtube.com/results?search_query=python+full+course+for+beginners"),
        ("freeCodeCamp: Python", "https://www.freecodecamp.org/learn/scientific-computing-with-python/"),
    ],
    "SQL": [
        ("Mode SQL Tutorial", "https://mode.com/sql-tutorial/"),
        ("YouTube: SQL for Beginners", "https://www.youtube.com/results?search_query=sql+full+course+for+beginners"),
        ("W3Schools SQL", "https://www.w3schools.com/sql/"),
    ],
    "Excel": [
        ("Microsoft Excel Training", "https://support.microsoft.com/en-us/excel"),
        ("YouTube: Excel for Data Analysis", "https://www.youtube.com/results?search_query=excel+for+data+analysis+full+course"),
    ],
    "Data Analysis": [
        ("Google Data Analytics (Coursera)", "https://www.coursera.org/professional-certificates/google-data-analytics"),
        ("YouTube: Data Analysis Full Course", "https://www.youtube.com/results?search_query=data+analysis+full+course"),
    ],
    "Data Visualization": [
        ("Tableau Free Training", "https://www.tableau.com/learn/training"),
        ("YouTube: Power BI Full Course", "https://www.youtube.com/results?search_query=power+bi+full+course"),
    ],
    "Statistics": [
        ("Khan Academy: Statistics", "https://www.khanacademy.org/math/statistics-probability"),
        ("YouTube: Statistics for Data Science", "https://www.youtube.com/results?search_query=statistics+for+data+science+full+course"),
    ],
    "Pandas": [
        ("Pandas Official Docs", "https://pandas.pydata.org/docs/getting_started/index.html"),
        ("YouTube: Pandas Tutorial", "https://www.youtube.com/results?search_query=pandas+python+tutorial"),
    ],
    "NumPy": [
        ("NumPy Official Quickstart", "https://numpy.org/doc/stable/user/quickstart.html"),
        ("YouTube: NumPy Full Tutorial", "https://www.youtube.com/results?search_query=numpy+full+tutorial+for+beginners"),
    ],
    "NoSQL": [
        ("MongoDB Official Docs", "https://www.mongodb.com/docs/manual/tutorial/getting-started/"),
        ("YouTube: NoSQL Databases Explained", "https://www.youtube.com/results?search_query=nosql+databases+full+course"),
    ],
    "R": [
        ("R for Data Science (free book)", "https://r4ds.hadley.nz/"),
        ("YouTube: R Programming Full Course", "https://www.youtube.com/results?search_query=r+programming+full+course+for+beginners"),
    ],
    "Machine Learning": [
        ("Andrew Ng: Machine Learning (Coursera)", "https://www.coursera.org/specializations/machine-learning-introduction"),
        ("YouTube: Machine Learning Full Course", "https://www.youtube.com/results?search_query=machine+learning+full+course"),
    ],
    "Deep Learning": [
        ("DeepLearning.AI Specialization", "https://www.coursera.org/specializations/deep-learning"),
        ("YouTube: Deep Learning Full Course", "https://www.youtube.com/results?search_query=deep+learning+full+course"),
    ],
    "NLP": [
        ("Hugging Face NLP Course", "https://huggingface.co/learn/nlp-course"),
        ("YouTube: NLP Full Course", "https://www.youtube.com/results?search_query=natural+language+processing+full+course"),
    ],
    "Big Data": [
        ("Apache Spark Docs", "https://spark.apache.org/docs/latest/quick-start.html"),
        ("YouTube: Big Data Full Course", "https://www.youtube.com/results?search_query=big+data+spark+hadoop+full+course"),
    ],
    "JavaScript": [
        ("MDN JavaScript Guide", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide"),
        ("YouTube: JavaScript Full Course", "https://www.youtube.com/results?search_query=javascript+full+course+for+beginners"),
    ],
    "TypeScript": [
        ("TypeScript Official Handbook", "https://www.typescriptlang.org/docs/handbook/intro.html"),
        ("YouTube: TypeScript Crash Course", "https://www.youtube.com/results?search_query=typescript+crash+course"),
    ],
    "HTML/CSS": [
        ("MDN HTML/CSS Basics", "https://developer.mozilla.org/en-US/docs/Learn/Getting_started_with_the_web"),
        ("YouTube: HTML CSS Full Course", "https://www.youtube.com/results?search_query=html+css+full+course"),
    ],
    "React": [
        ("React Official Docs", "https://react.dev/learn"),
        ("YouTube: React Full Course", "https://www.youtube.com/results?search_query=react+js+full+course"),
    ],
    "Angular": [
        ("Angular Official Docs", "https://angular.dev/tutorials"),
        ("YouTube: Angular Full Course", "https://www.youtube.com/results?search_query=angular+full+course"),
    ],
    "Vue": [
        ("Vue Official Guide", "https://vuejs.org/guide/introduction.html"),
        ("YouTube: Vue.js Full Course", "https://www.youtube.com/results?search_query=vue+js+full+course"),
    ],
    "Node.js": [
        ("Node.js Official Docs", "https://nodejs.org/en/learn"),
        ("YouTube: Node.js Full Course", "https://www.youtube.com/results?search_query=node+js+full+course"),
    ],
    "Django": [
        ("Django Official Tutorial", "https://docs.djangoproject.com/en/stable/intro/tutorial01/"),
        ("YouTube: Django Full Course", "https://www.youtube.com/results?search_query=django+full+course"),
    ],
    "Flask": [
        ("Flask Official Docs", "https://flask.palletsprojects.com/en/latest/quickstart/"),
        ("YouTube: Flask Full Course", "https://www.youtube.com/results?search_query=flask+full+course"),
    ],
    "FastAPI": [
        ("FastAPI Official Docs", "https://fastapi.tiangolo.com/tutorial/"),
        ("YouTube: FastAPI Full Course", "https://www.youtube.com/results?search_query=fastapi+full+course"),
    ],
    "Spring Boot": [
        ("Spring Boot Official Guide", "https://spring.io/guides/gs/spring-boot"),
        ("YouTube: Spring Boot Full Course", "https://www.youtube.com/results?search_query=spring+boot+full+course"),
    ],
    "REST API": [
        ("MDN: HTTP & APIs", "https://developer.mozilla.org/en-US/docs/Web/HTTP"),
        ("YouTube: REST API Crash Course", "https://www.youtube.com/results?search_query=rest+api+crash+course"),
    ],
    "Git": [
        ("Git Official Docs", "https://git-scm.com/doc"),
        ("YouTube: Git & GitHub Full Course", "https://www.youtube.com/results?search_query=git+and+github+full+course"),
    ],
    "Docker": [
        ("Docker Official Get Started", "https://docs.docker.com/get-started/"),
        ("YouTube: Docker Full Course", "https://www.youtube.com/results?search_query=docker+full+course"),
    ],
    "Kubernetes": [
        ("Kubernetes Official Docs", "https://kubernetes.io/docs/tutorials/"),
        ("YouTube: Kubernetes Full Course", "https://www.youtube.com/results?search_query=kubernetes+full+course"),
    ],
    "AWS": [
        ("AWS Skill Builder (Free)", "https://skillbuilder.aws/"),
        ("YouTube: AWS Full Course", "https://www.youtube.com/results?search_query=aws+full+course+for+beginners"),
    ],
    "Azure": [
        ("Microsoft Learn: Azure", "https://learn.microsoft.com/en-us/training/azure/"),
        ("YouTube: Azure Full Course", "https://www.youtube.com/results?search_query=azure+full+course"),
    ],
    "GCP": [
        ("Google Cloud Skills Boost", "https://www.cloudskillsboost.google/"),
        ("YouTube: GCP Full Course", "https://www.youtube.com/results?search_query=google+cloud+platform+full+course"),
    ],
    "CI/CD": [
        ("GitHub Actions Docs", "https://docs.github.com/en/actions/learn-github-actions"),
        ("YouTube: CI/CD Pipeline Tutorial", "https://www.youtube.com/results?search_query=ci+cd+pipeline+tutorial"),
    ],
    "Linux": [
        ("Linux Journey", "https://linuxjourney.com/"),
        ("YouTube: Linux Full Course", "https://www.youtube.com/results?search_query=linux+full+course+for+beginners"),
    ],
    "Data Structures & Algorithms": [
        ("NeetCode Roadmap", "https://neetcode.io/roadmap"),
        ("YouTube: DSA Full Course", "https://www.youtube.com/results?search_query=data+structures+and+algorithms+full+course"),
    ],
    "OOP": [
        ("GeeksforGeeks: OOP Concepts", "https://www.geeksforgeeks.org/object-oriented-programming-oops-concept-in-java/"),
        ("YouTube: OOP Concepts", "https://www.youtube.com/results?search_query=object+oriented+programming+concepts"),
    ],
    "Testing": [
        ("Selenium Official Docs", "https://www.selenium.dev/documentation/"),
        ("YouTube: Software Testing Full Course", "https://www.youtube.com/results?search_query=software+testing+full+course"),
    ],
    "Figma": [
        ("Figma Official Learn Hub", "https://help.figma.com/hc/en-us/categories/360002051613-Learn-design-in-Figma"),
        ("YouTube: Figma Full Course", "https://www.youtube.com/results?search_query=figma+full+course"),
    ],
    "UI/UX Design": [
        ("Google UX Design (Coursera)", "https://www.coursera.org/professional-certificates/google-ux-design"),
        ("YouTube: UI/UX Design Full Course", "https://www.youtube.com/results?search_query=ui+ux+design+full+course"),
    ],
    "Product Management": [
        ("Product School Free Resources", "https://productschool.com/free-product-management-resources"),
        ("YouTube: Product Management Basics", "https://www.youtube.com/results?search_query=product+management+full+course"),
    ],
    "Project Management": [
        ("Google Project Management (Coursera)", "https://www.coursera.org/professional-certificates/google-project-management"),
        ("YouTube: Agile & Scrum Full Course", "https://www.youtube.com/results?search_query=agile+scrum+full+course"),
    ],
    "Digital Marketing": [
        ("Google Digital Garage", "https://learndigital.withgoogle.com/digitalgarage"),
        ("YouTube: Digital Marketing Full Course", "https://www.youtube.com/results?search_query=digital+marketing+full+course"),
    ],
    "Content Writing": [
        ("HubSpot Content Marketing Course", "https://academy.hubspot.com/courses/content-marketing"),
        ("YouTube: Content Writing Tutorial", "https://www.youtube.com/results?search_query=content+writing+tutorial"),
    ],
    "Communication": [
        ("Coursera: Improve Communication Skills", "https://www.coursera.org/learn/wharton-communication-skills"),
        ("YouTube: Communication Skills", "https://www.youtube.com/results?search_query=communication+skills+course"),
    ],
    "Leadership": [
        ("Coursera: Leadership Skills", "https://www.coursera.org/learn/leadership-skills"),
        ("YouTube: Leadership Training", "https://www.youtube.com/results?search_query=leadership+skills+training"),
    ],
    "Problem Solving": [
        ("Coursera: Problem Solving Techniques", "https://www.coursera.org/learn/problem-solving"),
        ("YouTube: Analytical Thinking", "https://www.youtube.com/results?search_query=problem+solving+and+analytical+thinking"),
    ],
    "Android Development": [
        ("Android Developers Official Docs", "https://developer.android.com/courses"),
        ("YouTube: Android Development Full Course", "https://www.youtube.com/results?search_query=android+development+full+course+kotlin"),
    ],
    "Kotlin": [
        ("Kotlin Official Docs", "https://kotlinlang.org/docs/getting-started.html"),
        ("YouTube: Kotlin Full Course", "https://www.youtube.com/results?search_query=kotlin+full+course+for+beginners"),
    ],
    "iOS Development": [
        ("Apple: Learn Swift", "https://developer.apple.com/swift/resources/"),
        ("YouTube: iOS Development Full Course", "https://www.youtube.com/results?search_query=ios+development+full+course+swift"),
    ],
    "Cybersecurity": [
        ("TryHackMe Free Rooms", "https://tryhackme.com/"),
        ("YouTube: Cybersecurity Full Course", "https://www.youtube.com/results?search_query=cybersecurity+full+course+for+beginners"),
    ],
    "Networking": [
        ("Cisco Networking Academy (free)", "https://www.netacad.com/courses/networking"),
        ("YouTube: Computer Networking Full Course", "https://www.youtube.com/results?search_query=computer+networking+full+course"),
    ],
    "Blockchain": [
        ("Ethereum Developer Docs", "https://ethereum.org/en/developers/docs/"),
        ("YouTube: Blockchain Full Course", "https://www.youtube.com/results?search_query=blockchain+full+course"),
    ],
    "Power BI": [
        ("Microsoft Learn: Power BI", "https://learn.microsoft.com/en-us/training/powerplatform/power-bi"),
        ("YouTube: Power BI Full Course", "https://www.youtube.com/results?search_query=power+bi+full+course"),
    ],
    "Financial Modeling": [
        ("CFI Free Resources", "https://corporatefinanceinstitute.com/resources/financial-modeling/"),
        ("YouTube: Financial Modeling Tutorial", "https://www.youtube.com/results?search_query=financial+modeling+tutorial"),
    ],
    "Accounting": [
        ("Khan Academy: Accounting Basics", "https://www.khanacademy.org/economics-finance-domain/core-finance/accounting-and-financial-stateme"),
        ("YouTube: Accounting Basics", "https://www.youtube.com/results?search_query=accounting+basics+full+course"),
    ],
    "Java": [
        ("Oracle Java Tutorials", "https://docs.oracle.com/javase/tutorial/"),
        ("YouTube: Java Full Course", "https://www.youtube.com/results?search_query=java+full+course+for+beginners"),
    ],
    "C++": [
        ("cplusplus.com Reference", "https://cplusplus.com/doc/tutorial/"),
        ("YouTube: C++ Full Course", "https://www.youtube.com/results?search_query=c%2B%2B+full+course"),
    ],
    "C": [
        ("GeeksforGeeks C Tutorial", "https://www.geeksforgeeks.org/c-programming-language/"),
        ("YouTube: C Programming Full Course", "https://www.youtube.com/results?search_query=c+programming+full+course"),
    ],
}

def default_resource(skill: str):
    return [
        (f"YouTube: {skill} Full Course", f"https://www.youtube.com/results?search_query={skill.replace(' ', '+')}+full+course"),
        (f"Google Search: Learn {skill}", f"https://www.google.com/search?q=best+free+course+to+learn+{skill.replace(' ', '+')}"),
    ]


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


_ALIAS_PATTERN_CACHE = {}


def _alias_pattern(alias: str):
    """Compile a word-boundary-safe regex for an alias so short tokens like
    'ts', 'r', 'c' don't false-positive-match inside unrelated words/URLs
    (e.g. 'ts' inside 'https', 'git' inside 'github.com').

    Very short aliases (<=2 chars, e.g. 'c', 'js', 'ts', 'py') get an extra
    strict boundary that also excludes '.' and '-' as valid neighbors. Without
    this, 'c' matches inside address fragments like 'C-401, Green Park', and
    'js'/'ts' match inside filename-style mentions like 'react.js', 'node.js'
    or 'resume.js'/'example.ts' - none of which actually indicate the skill.
    Longer aliases keep the original, more permissive boundary since they
    aren't ambiguous enough to need it (e.g. AWS's 's3-bucket' should still
    match 's3').
    """
    if alias not in _ALIAS_PATTERN_CACHE:
        stripped = alias.strip()
        escaped = re.escape(stripped)
        if len(stripped) <= 2:
            boundary_chars = "a-z0-9.\\-"
        else:
            boundary_chars = "a-z0-9"
        pattern = rf"(?<![{boundary_chars}]){escaped}(?![{boundary_chars}])"
        _ALIAS_PATTERN_CACHE[alias] = re.compile(pattern)
    return _ALIAS_PATTERN_CACHE[alias]


def extract_skills(text: str):
    """Return the list of canonical skills found in free text (resume, JD, etc.)."""
    norm = normalize_text(text)
    found = []
    for canonical, aliases in SKILL_ALIASES.items():
        for alias in aliases:
            alias = alias.strip()
            if not alias:
                continue
            if _alias_pattern(alias).search(norm):
                found.append(canonical)
                break
    return sorted(set(found))


def get_resources(skill: str):
    return RESOURCES.get(skill, default_resource(skill))
