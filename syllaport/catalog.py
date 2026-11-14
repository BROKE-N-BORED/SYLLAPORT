"""The verified $0 catalog.

Every source and course here comes from
~/workspace/research_notes/free-colleges-master-list/report.md
(researched 2026-11-10/11 from official sources). The filter that
admitted each entry: no credit card to learn, no phone/SMS gate, no
paid certificate required to learn. Coursera's full courses fail the
filter (preview of the first module only since 2026-08-08) and are NOT
in this catalog; edX audit entries say so plainly.

No entry here is invented. Where the report does not state a length,
length is None and the UI says the length is not listed.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Sources: the 19 verified free sources (report Section 1, in report order)
# ---------------------------------------------------------------------------

SOURCES = [
    {"id": "mit-ocw", "name": "MIT OpenCourseWare",
     "url": "https://ocw.mit.edu/pages/get-started/",
     "signup": "None. No signup, no enrollment.",
     "certificate": "No certificate from OCW.",
     "subjects": ["Business", "Money", "Marketing", "Web design", "Coding",
                  "Game design", "Music", "Science", "Maths", "Humanities"]},
    {"id": "harvard-cs50", "name": "Harvard CS50",
     "url": "https://cs50.harvard.edu/x/",
     "signup": "No account for the material. A free edX account (email "
               "only) is needed only to submit problem sets.",
     "certificate": "Free CS50 Certificate at 70% or more on problem sets "
                    "and projects.",
     "subjects": ["Coding", "Game design", "Web design", "Business"]},
    {"id": "harvardx", "name": "HarvardX (via edX)",
     "url": "https://pll.harvard.edu/catalog?topics%5B715%5D=715&price%5B1%5D=1&max_price=&start_date=&keywords=",
     "signup": "Free edX account (email). No card for audit.",
     "certificate": "Paid verified certificate only. Audit access is "
                    "time-limited.",
     "subjects": ["Business", "Coding", "Humanities", "Science"]},
    {"id": "yale-oyc", "name": "Yale Open Yale Courses",
     "url": "https://oyc.yale.edu/",
     "signup": "None. Registration not required.",
     "certificate": "No certificate.",
     "subjects": ["Humanities", "Money", "Science"]},
    {"id": "stanford-see", "name": "Stanford Engineering Everywhere",
     "url": "https://see.stanford.edu/",
     "signup": "None for SEE materials. No card.",
     "certificate": "No certificate from SEE.",
     "subjects": ["Coding", "Science", "Maths"]},
    {"id": "stanford-online", "name": "Stanford Online (via edX)",
     "url": "https://support.edx.org/hc/en-us/articles/1500003964681-What-is-the-audit-track",
     "signup": "Free edX account (email). No card for audit.",
     "certificate": "Paid verified certificate only. Audit access is "
                    "time-limited.",
     "subjects": ["Coding", "Business", "Science"]},
    {"id": "openlearn", "name": "The Open University, OpenLearn",
     "url": "https://www.open.edu/openlearn/free-courses/full-catalogue?filter=date%2Fgrid%2F21%2Fall%2Fall%2Fall%2Fall&page=4",
     "signup": "Browse with no account. A free account (email) is needed "
               "only to track progress or claim a statement.",
     "certificate": "Free Statement of Participation on completion. "
                    "Badged courses also give a free digital badge.",
     "subjects": ["Money", "Business", "Science", "Humanities"]},
    {"id": "saylor", "name": "Saylor Academy",
     "url": "https://learn.saylor.org/course/index.php?categoryid=6",
     "signup": "Content readable without registering. A free account is "
               "required for final exams and certificates.",
     "certificate": "Free certificate of completion (account and final "
                    "exam required).",
     "subjects": ["Business", "Money", "Marketing", "Coding", "Maths",
                  "Humanities"]},
    {"id": "cmu-oli", "name": "Carnegie Mellon Open Learning Initiative",
     "url": "https://oli.cmu.edu/course-type/o-f/",
     "signup": "Free account for the LMS. No card for the Open and Free tier.",
     "certificate": "No certificate on Open and Free courses.",
     "subjects": ["Maths", "Coding", "Science", "Business"]},
    {"id": "openstax", "name": "Rice OpenStax (textbooks)",
     "url": "https://openstax.org/",
     "signup": "None for digital textbooks.",
     "certificate": "Textbooks, not courses. No certificate.",
     "subjects": ["Money", "Business", "Science", "Maths", "Humanities"]},
    {"id": "tudelft", "name": "TU Delft OpenCourseWare",
     "url": "https://ocw.tudelft.nl/about-ocw/",
     "signup": "No registration required.",
     "certificate": "No certificate.",
     "subjects": ["Science", "Coding", "Maths"]},
    {"id": "berkeley", "name": "UC Berkeley, BerkeleyX (via edX)",
     "url": "https://rtl.berkeley.edu/services-programs/edx-and-coursera",
     "signup": "Free edX account (email). No card for audit. Use the edX "
               "route, not Coursera.",
     "certificate": "Paid certificate only. No academic credit on audit.",
     "subjects": ["Humanities", "Coding", "Money", "Business"]},
    {"id": "jhu", "name": "Johns Hopkins OCW (Public Health)",
     "url": "https://publichealth.jhu.edu/2005/ocw",
     "signup": "No registration.",
     "certificate": "No certificate via OCW.",
     "subjects": ["Science", "Maths"]},
    {"id": "helsinki", "name": "University of Helsinki, Elements of AI",
     "url": "https://elementsofai.com/",
     "signup": "Free account on the course site. No card for learning.",
     "certificate": "Free digital certificate for Introduction to AI. "
                    "Building AI certificate is paid.",
     "subjects": ["Coding"]},
    {"id": "nptel", "name": "NPTEL (IITs and IISc, India)",
     "url": "https://nptel.ac.in/",
     "signup": "Free account to enrol. No card to learn.",
     "certificate": "Optional certificate needs an in-person proctored "
                    "exam with a fee. Learning is free without it.",
     "subjects": ["Coding", "Science", "Maths", "Business", "Humanities"]},
    {"id": "uci", "name": "UC Irvine Open (OpenChem)",
     "url": "http://ocw.uci.edu/collections/open_chemistry.html",
     "signup": "None for OCW materials.",
     "certificate": "No certificate via OCW.",
     "subjects": ["Science", "Maths"]},
    {"id": "usu", "name": "Utah State University OCW (archive)",
     "url": "https://digitalcommons.usu.edu/ocw_bio",
     "signup": "None.",
     "certificate": "No credit via OCW. Older material, an archive library.",
     "subjects": ["Science", "Humanities"]},
    {"id": "utokyo", "name": "University of Tokyo OCW",
     "url": "https://www.he.u-tokyo.ac.jp/en/activities/utokyo-ocw/",
     "signup": "None for OCW materials. Much content is Japanese-first.",
     "certificate": "No certificate via OCW.",
     "subjects": ["Science", "Humanities"]},
    {"id": "libretexts", "name": "UC Davis LibreTexts (textbooks)",
     "url": "https://libretexts.org/",
     "signup": "None for reading.",
     "certificate": "Textbooks, not courses. No certificate.",
     "subjects": ["Science", "Maths", "Business", "Humanities"]},
]

SOURCE_BY_ID = {s["id"]: s for s in SOURCES}

# ---------------------------------------------------------------------------
# Courses: named courses from the report (Sections 1, 4, 5).
# length is shown only where the report states it; otherwise None.
# ---------------------------------------------------------------------------

COURSES = [
    # Harvard CS50
    {"id": "cs50x", "title": "CS50x: Introduction to Computer Science",
     "source_id": "harvard-cs50", "subject": "Coding",
     "url": "https://cs50.harvard.edu/x/",
     "blurb": "The full introductory computer science course, built for "
              "beginners. The report's first pick for a solo learner "
              "starting to code.",
     "certificate": "Free CS50 Certificate at 70% or more.",
     "length": "11 weeks"},
    {"id": "cs50-python", "title": "CS50 Python: Introduction to "
     "Programming with Python",
     "source_id": "harvard-cs50", "subject": "Coding",
     "url": "https://cs50.harvard.edu/x/",
     "blurb": "Introduction to programming with Python, from the CS50 family.",
     "certificate": "Free CS50 Certificate at 70% or more.",
     "length": None},
    {"id": "cs50-web", "title": "CS50 Web Programming with Python and "
     "JavaScript",
     "source_id": "harvard-cs50", "subject": "Web design",
     "url": "https://cs50.harvard.edu/x/",
     "blurb": "Web programming with Python, JavaScript, SQL, Django, and React.",
     "certificate": "Free CS50 Certificate at 70% or more.",
     "length": None},
    {"id": "cs50-ai", "title": "CS50 AI: Introduction to Artificial "
     "Intelligence with Python",
     "source_id": "harvard-cs50", "subject": "Coding",
     "url": "https://cs50.harvard.edu/x/",
     "blurb": "Artificial intelligence with Python, from the CS50 family.",
     "certificate": "Free CS50 Certificate at 70% or more.",
     "length": None},
    {"id": "cs50-game", "title": "CS50 Game Development: Introduction to "
     "Game Development (2D)",
     "source_id": "harvard-cs50", "subject": "Game design",
     "url": "https://cs50.harvard.edu/x/",
     "blurb": "Build 2D games. The report's top pick for game design, "
              "paired with MIT Game Design for the theory.",
     "certificate": "Free CS50 Certificate at 70% or more.",
     "length": None},
    {"id": "cs50-business", "title": "CS50 for Business: Computer Science "
     "for Business Professionals",
     "source_id": "harvard-cs50", "subject": "Business",
     "url": "https://cs50.harvard.edu/x/",
     "blurb": "Computer science for business professionals, from the CS50 family.",
     "certificate": "Free CS50 Certificate at 70% or more.",
     "length": None},
    # MIT OCW
    {"id": "mit-60001", "title": "6.0001 Introduction to Computer Science "
     "and Programming in Python",
     "source_id": "mit-ocw", "subject": "Coding",
     "url": "https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/",
     "blurb": "MIT's introductory programming course in Python. A strong "
              "second pass after CS50x.",
     "certificate": "No certificate from OCW.",
     "length": None},
    {"id": "mit-64500", "title": "6.4500 Design for the Web",
     "source_id": "mit-ocw", "subject": "Web design",
     "url": "https://designftw.mit.edu",
     "blurb": "The report's top pick for website design and UX.",
     "certificate": "No certificate from OCW.",
     "length": None},
    {"id": "mit-15515", "title": "15.515 Financial Accounting",
     "source_id": "mit-ocw", "subject": "Money",
     "url": "https://ocw.mit.edu/courses/15-515-financial-accounting-fall-2003/",
     "blurb": "Business money: financial accounting, with the free OpenStax "
              "Principles of Accounting textbook beside it.",
     "certificate": "No certificate from OCW.",
     "length": None},
    {"id": "mit-15835", "title": "15.835 Entrepreneurial Marketing",
     "source_id": "mit-ocw", "subject": "Marketing",
     "url": "https://ocw.mit.edu/courses/15-835-entrepreneurial-marketing-spring-2002/",
     "blurb": "Marketing written for start-ups with no budget. The report's "
              "top pick for marketing.",
     "certificate": "No certificate from OCW.",
     "length": None},
    {"id": "mit-15834", "title": "15.834 Marketing Strategy",
     "source_id": "mit-ocw", "subject": "Marketing",
     "url": "https://ocw.mit.edu/courses/15-834-marketing-strategy-spring-2003/",
     "blurb": "Marketing strategy from MIT Sloan course material.",
     "certificate": "No certificate from OCW.",
     "length": None},
    {"id": "mit-cms608", "title": "CMS.608 Game Design",
     "source_id": "mit-ocw", "subject": "Game design",
     "url": "https://ocw.mit.edu/courses/cms-608-game-design-fall-2010/",
     "blurb": "Game design theory. Pairs with CS50 Game Development, "
              "which is the building side.",
     "certificate": "No certificate from OCW.",
     "length": None},
    {"id": "mit-21m385", "title": "21M.385 Interactive Music Systems",
     "source_id": "mit-ocw", "subject": "Music",
     "url": "https://ocw.mit.edu/courses/21m-385-interactive-music-systems-fall-2016/pages/syllabus/",
     "blurb": "The only fully free, schedulable university music-tech "
              "anchor the report verified. Berklee's catalogue is "
              "Coursera-walled.",
     "certificate": "No certificate from OCW.",
     "length": None},
    {"id": "mit-6837", "title": "6.837 Computer Graphics",
     "source_id": "mit-ocw", "subject": "Web design",
     "url": "https://ocw.mit.edu/courses/6-837-computer-graphics-fall-2012/pages/syllabus/",
     "blurb": "Computer graphics: the design and rendering lane.",
     "certificate": "No certificate from OCW.",
     "length": None},
    {"id": "mit-ecology", "title": "Ecology I: The Earth System",
     "source_id": "mit-ocw", "subject": "Science",
     "url": "https://ocw.mit.edu/pages/get-started/",
     "blurb": "Hydrologic, carbon, and nitrogen cycles, trophic dynamics, "
              "population growth, competition, predation.",
     "certificate": "No certificate from OCW.",
     "length": None},
    {"id": "mit-12003", "title": "12.003 Atmosphere, Ocean and Climate "
     "Dynamics",
     "source_id": "mit-ocw", "subject": "Science",
     "url": "http://ocw.mit.edu/courses/12-003-atmosphere-ocean-and-climate-dynamics-fall-2008/",
     "blurb": "Atmosphere, ocean, and climate dynamics. Needs multivariable "
              "calculus and Physics I first.",
     "certificate": "No certificate from OCW.",
     "length": None},
    {"id": "mit-entre101", "title": "Entrepreneurship 101: Who Is Your "
     "Customer?",
     "source_id": "mit-ocw", "subject": "Business",
     "url": "http://openlearning.mit.edu/news/free-online-courses-mit-entrepreneurs-and-innovators",
     "blurb": "MIT entrepreneurship sequence, built for founders, not MBA "
              "students. The report's top pick for business.",
     "certificate": "No certificate from OCW.",
     "length": None},
    {"id": "mit-entre-become", "title": "Becoming an Entrepreneur",
     "source_id": "mit-ocw", "subject": "Business",
     "url": "http://openlearning.mit.edu/news/free-online-courses-mit-entrepreneurs-and-innovators",
     "blurb": "The next step in the MIT entrepreneurship sequence after "
              "Entrepreneurship 101.",
     "certificate": "No certificate from OCW.",
     "length": None},
    # OpenLearn
    {"id": "ou-money", "title": "Managing my money",
     "source_id": "openlearn", "subject": "Money",
     "url": "https://www.open.edu/openlearn/money-management/free-courses?filter=date%2Fgrid%2F107%2C108%2Fall%2Fall%2Fall%2Fall",
     "blurb": "Budgets, debt, investing basics, property, insurance. The "
              "strongest single source in the report for personal money skills.",
     "certificate": "Free Statement of Participation.",
     "length": "24 hours"},
    {"id": "ou-academy-money", "title": "MSE's Academy of Money",
     "source_id": "openlearn", "subject": "Money",
     "url": "https://www.open.edu/openlearn/money-management/free-courses?filter=date%2Fgrid%2F107%2C108%2Fall%2Fall%2Fall%2Fall",
     "blurb": "Money skills from the Open University Money and Business catalogue.",
     "certificate": "Free Statement of Participation.",
     "length": None},
    {"id": "ou-risk", "title": "Understanding and managing risk",
     "source_id": "openlearn", "subject": "Money",
     "url": "https://www.open.edu/openlearn/money-management/free-courses?filter=date%2Fgrid%2F107%2C108%2Fall%2Fall%2Fall%2Fall",
     "blurb": "Understanding and managing risk, from the Open University "
              "Money and Business catalogue.",
     "certificate": "Free Statement of Participation.",
     "length": None},
    # Saylor
    {"id": "saylor-bus101", "title": "BUS101 Introduction to Business",
     "source_id": "saylor", "subject": "Business",
     "url": "https://learn.saylor.org/course/index.php?categoryid=6",
     "blurb": "Introduction to business, from the best structured free "
              "business catalogue in the report.",
     "certificate": "Free certificate of completion.",
     "length": None},
    {"id": "saylor-bus103", "title": "BUS103 Introduction to Financial "
     "Accounting",
     "source_id": "saylor", "subject": "Money",
     "url": "https://learn.saylor.org/course/index.php?categoryid=6",
     "blurb": "Introduction to financial accounting.",
     "certificate": "Free certificate of completion.",
     "length": None},
    {"id": "saylor-bus202", "title": "BUS202 Principles of Finance",
     "source_id": "saylor", "subject": "Money",
     "url": "https://learn.saylor.org/course/index.php?categoryid=6",
     "blurb": "Principles of finance.",
     "certificate": "Free certificate of completion.",
     "length": None},
    {"id": "saylor-bus203", "title": "BUS203 Principles of Marketing",
     "source_id": "saylor", "subject": "Marketing",
     "url": "https://learn.saylor.org/course/index.php?categoryid=6",
     "blurb": "Principles of marketing.",
     "certificate": "Free certificate of completion.",
     "length": None},
    {"id": "saylor-bus208", "title": "BUS208 Principles of Management",
     "source_id": "saylor", "subject": "Business",
     "url": "https://learn.saylor.org/course/index.php?categoryid=6",
     "blurb": "Principles of management.",
     "certificate": "Free certificate of completion.",
     "length": None},
    {"id": "saylor-bus651", "title": "BUS651 Business Law and "
     "Entrepreneurship",
     "source_id": "saylor", "subject": "Business",
     "url": "https://learn.saylor.org/course/index.php?categoryid=6",
     "blurb": "Business law and entrepreneurship.",
     "certificate": "Free certificate of completion.",
     "length": None},
    {"id": "saylor-bus653", "title": "BUS653 Innovation and "
     "Entrepreneurship Launch",
     "source_id": "saylor", "subject": "Business",
     "url": "https://learn.saylor.org/course/index.php?categoryid=6",
     "blurb": "Innovation and entrepreneurship launch.",
     "certificate": "Free certificate of completion.",
     "length": None},
    # Yale OYC
    {"id": "yale-psyc110", "title": "PSYC 110 Introduction to Psychology",
     "source_id": "yale-oyc", "subject": "Humanities",
     "url": "https://oyc.yale.edu/",
     "blurb": "Full recorded Yale lectures. The report's top pick for "
              "psychology and humanities.",
     "certificate": "No certificate.",
     "length": None},
    {"id": "yale-econ251", "title": "ECON 251 Financial Theory",
     "source_id": "yale-oyc", "subject": "Money",
     "url": "https://oyc.yale.edu/",
     "blurb": "Robert Shiller's Yale lectures on financial theory, full "
              "course on Open Yale Courses.",
     "certificate": "No certificate.",
     "length": None},
    # Helsinki
    {"id": "helsinki-elements", "title": "Elements of AI: Introduction to AI",
     "source_id": "helsinki", "subject": "Coding",
     "url": "https://elementsofai.com/",
     "blurb": "Introduction to AI, no programming needed, six chapters. "
              "The best beginner AI course in the report for a "
              "non-programmer start.",
     "certificate": "Free digital certificate for Introduction to AI.",
     "length": "About 30 hours"},
    # Stanford SEE
    {"id": "stanford-cs106", "title": "CS106 Programming sequence",
     "source_id": "stanford-see", "subject": "Coding",
     "url": "https://see.stanford.edu/",
     "blurb": "Stanford's introductory programming sequence, full lecture "
              "videos plus syllabi, handouts, homework, and exams.",
     "certificate": "No certificate from SEE.",
     "length": None},
    # CMU OLI
    {"id": "oli-stats", "title": "OLI Statistics",
     "source_id": "cmu-oli", "subject": "Maths",
     "url": "https://oli.cmu.edu/course-type/o-f/",
     "blurb": "Interactive, self-paced statistics with heavy practice. "
              "The report's top pick for maths foundations.",
     "certificate": "No certificate on Open and Free courses.",
     "length": None},
    {"id": "oli-python", "title": "OLI Python Programming",
     "source_id": "cmu-oli", "subject": "Coding",
     "url": "https://oli.cmu.edu/course-type/o-f/",
     "blurb": "Interactive, self-paced Python programming with heavy practice.",
     "certificate": "No certificate on Open and Free courses.",
     "length": None},
    # Berkeley (edX audit)
    {"id": "berkeley-writing", "title": "Academic and Business Writing "
     "(edX audit)",
     "source_id": "berkeley", "subject": "Humanities",
     "url": "https://rtl.berkeley.edu/services-programs/edx-and-coursera",
     "blurb": "The best writing pick in the report. Free to audit on edX; "
              "start it only when ready to finish inside the audit window.",
     "certificate": "Paid certificate only.",
     "length": None},
    {"id": "berkeley-happiness", "title": "The Science of Happiness "
     "(edX audit)",
     "source_id": "berkeley", "subject": "Humanities",
     "url": "https://rtl.berkeley.edu/services-programs/edx-and-coursera",
     "blurb": "The science of happiness, free to audit on edX.",
     "certificate": "Paid certificate only.",
     "length": None},
    # NPTEL
    {"id": "nptel-python", "title": "NPTEL Python Programming",
     "source_id": "nptel", "subject": "Coding",
     "url": "https://nptel.ac.in/",
     "blurb": "Python programming from the IITs and IISc. Learn free; the "
              "certificate exam is in-person in India and not needed.",
     "certificate": "No free certificate.",
     "length": None},
    # UCI
    {"id": "uci-openchem", "title": "OpenChem: General Chemistry",
     "source_id": "uci", "subject": "Science",
     "url": "http://ocw.uci.edu/collections/open_chemistry.html",
     "blurb": "The full undergraduate chemistry curriculum, 15 "
              "quarter-length courses. The best chemistry in the report.",
     "certificate": "No certificate via OCW.",
     "length": None},
    {"id": "uci-maths", "title": "UCI Mathematics: Pre-Calculus and Calculus",
     "source_id": "uci", "subject": "Maths",
     "url": "https://www.math.uci.edu/~remote_teaching/onlineresources.html",
     "blurb": "Pre-Calculus, Calculus, Probability and Statistics, and "
              "Math of Finance resources.",
     "certificate": "No certificate via OCW.",
     "length": None},
    # OpenStax textbooks
    {"id": "openstax-accounting", "title": "Principles of Accounting "
     "(textbook)",
     "source_id": "openstax", "subject": "Money",
     "url": "https://openstax.org/",
     "blurb": "Free peer-reviewed college textbook, web and PDF. Open it "
              "beside a finance course.",
     "certificate": "Textbooks, not courses. No certificate.",
     "length": None},
    {"id": "openstax-business", "title": "Introduction to Business "
     "(textbook)",
     "source_id": "openstax", "subject": "Business",
     "url": "https://openstax.org/",
     "blurb": "Free peer-reviewed college textbook, web and PDF.",
     "certificate": "Textbooks, not courses. No certificate.",
     "length": None},
    {"id": "openstax-biology", "title": "Biology 2e (textbook)",
     "source_id": "openstax", "subject": "Science",
     "url": "https://openstax.org/",
     "blurb": "Free peer-reviewed college textbook, web and PDF.",
     "certificate": "Textbooks, not courses. No certificate.",
     "length": None},
    # TU Delft
    {"id": "tudelft-water", "title": "TU Delft water and sustainability OCW",
     "source_id": "tudelft", "subject": "Science",
     "url": "https://ocw.tudelft.nl/about-ocw/",
     "blurb": "Water management and sustainable development course materials.",
     "certificate": "No certificate.",
     "length": None},
    # Johns Hopkins
    {"id": "jhu-biostats", "title": "Biostatistics (OCW)",
     "source_id": "jhu", "subject": "Maths",
     "url": "https://publichealth.jhu.edu/2005/ocw",
     "blurb": "Biostatistics and statistical reasoning, the deepest free "
              "health-data material in the report.",
     "certificate": "No certificate via OCW.",
     "length": None},
]

COURSE_BY_ID = {c["id"]: c for c in COURSES}

SUBJECTS = ["Business", "Money", "Marketing", "Web design", "Coding",
            "Game design", "Music", "Science", "Maths", "Humanities"]

# Guided picks (report Section 5, top pick per category). Runner-up is None
# where the report verifies no second fully free anchor (Music).
SUBJECT_PICKS = {
    "Business": ("mit-entre101", "saylor-bus101"),
    "Money": ("ou-money", "mit-15515"),
    "Marketing": ("mit-15835", "saylor-bus203"),
    "Web design": ("mit-64500", "cs50-web"),
    "Coding": ("cs50x", "mit-60001"),
    "Game design": ("cs50-game", "mit-cms608"),
    "Music": ("mit-21m385", None),
    "Science": ("mit-ecology", "uci-openchem"),
    "Maths": ("oli-stats", "uci-maths"),
    "Humanities": ("yale-psyc110", "berkeley-writing"),
}


def courses_for_subject(subject):
    """Catalog courses in one subject, in catalog order."""
    return [c for c in COURSES if c["subject"] == subject]


def search_courses(query):
    """Catalog courses whose title, source, or subject matches the query."""
    q = (query or "").strip().lower()
    if not q:
        return list(COURSES)
    out = []
    for c in COURSES:
        source = SOURCE_BY_ID.get(c["source_id"], {})
        hay = " ".join([c["title"], c["subject"], c.get("blurb", ""),
                        source.get("name", "")]).lower()
        if q in hay:
            out.append(c)
    return out
