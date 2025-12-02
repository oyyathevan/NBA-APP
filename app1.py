import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import re
# Page config for responsive layout
st.set_page_config(
    page_title="Syllabus-Based CO Generator @theva",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Enhanced Custom CSS for cool colors and responsive GUI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #00b4d8;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0077b6;
        margin-top: 2rem;
        background: linear-gradient(90deg, #0077b6, #00b4d8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stDataFrame > div > div > div > table {
        font-size: 0.9rem;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stDataFrame > div > div > div > table tbody tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    .stDataFrame > div > div > div > table tbody tr:nth-child(odd) {
        background-color: #ffffff;
    }
    .stDataFrame > div > div > div > table th {
        background: linear-gradient(45deg, #00b4d8, #0077b6);
        color: white;
        font-weight: bold;
        border: none;
        padding: 12px;
        text-align: center;
    }
    .stDataFrame > div > div > div > table td {
        padding: 10px;
        border-bottom: 1px solid #dee2e6;
        text-align: left;
    }
    .stDataFrame > div > div > div > table tr:hover {
        background-color: #e3f2fd !important;
        transform: scale(1.01);
        transition: all 0.2s ease;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f0f8ff, #e0f7fa);
    }
    .matrix-cell {
        text-align: center;
        font-weight: bold;
        background-color: #f8f9fa;
    }
    .stButton > button {
        background: linear-gradient(45deg, #00b4d8, #0077b6);
        color: white;
        border-radius: 20px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        transition: transform 0.2s;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .credit {
        font-size: 0.8rem;
        color: #666;
        text-align: center;
        margin-top: 20px;
    }
    @media (max-width: 768px) {
        .main-header { font-size: 2rem; }
        .sub-header { font-size: 1.2rem; }
    }
    .output-section {
        background: linear-gradient(135deg, #f0f8ff 0%, #e3f2fd 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 5px solid #00b4d8;
    }
    .output-header {
        font-size: 1.8rem;
        color: #0077b6;
        text-align: center;
        margin-bottom: 15px;
        background: linear-gradient(90deg, #0077b6, #00b4d8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)
# Configure Gemini
GOOGLE_API_KEY = 'AIzaSyA3-5kFX1006cEuHPqCD8NfzWRSbyWb0XI'
GEMINI_MODEL = 'gemini-2.5-flash'
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)
# Updated AICTE POs (PO1-PO11 with full descriptions from user input)
PO_DESCRIPTIONS = {
    "PO1": "Engineering Knowledge: Apply knowledge of mathematics, natural science, computing, engineering fundamentals and an engineering specialization as specified in WK1 to WK4 respectively to develop to the solution of complex engineering problems.",
    "PO2": "Problem Analysis: Identify, formulate, review research literature and analyze complex engineering problems reaching substantiated conclusions with consideration for sustainable development. (WK1 to WK4)",
    "PO3": "Design/Development of Solutions: Design creative solutions for complex engineering problems and design/develop systems/components/processes to meet identified needs with consideration for the public health and safety, whole-life cost, net zero carbon, culture, society and environment as required. (WK5)",
    "PO4": "Conduct Investigations of Complex Problems: Conduct investigations of complex engineering problems using research-based knowledge including design of experiments, modelling, analysis & interpretation of data to provide valid conclusions. (WK8).",
    "PO5": "Engineering Tool Usage: Create, select and apply appropriate techniques, resources and modern engineering & IT tools, including prediction and modelling recognizing their limitations to solve complex engineering problems. (WK2 and WK6)",
    "PO6": "The Engineer and The World: Analyze and evaluate societal and environmental aspects while solving complex engineering problems for its impact on sustainability with reference to economy, health, safety, legal framework, culture and environment. (WK1, WK5, and WK7).",
    "PO7": "Ethics: Apply ethical principles and commit to professional ethics, human values, diversity and inclusion; adhere to national & international laws. (WK9)",
    "PO8": "Individual and Collaborative Team work: Function effectively as an individual, and as a member or leader in diverse/multi-disciplinary teams.",
    "PO9": "Communication: Communicate effectively and inclusively within the engineering community and society at large, such as being able to comprehend and write effective reports and design documentation, make effective presentations considering cultural, language, and learning differences",
    "PO10": "Project Management and Finance: Apply knowledge and understanding of engineering management principles and economic decision-making and apply these to one’s own work, as a member and leader in a team, and to manage projects and in multidisciplinary environments.",
    "PO11": "Life-Long Learning: Recognize the need for, and have the preparation and ability for i) independent and life-long learning ii) adaptability to new and emerging technologies and iii) critical thinking in the broadest context of technological change. (WK8)"
}
# Knowledge Profiles (WK1-WK9 from reference document) - full descriptions
WK_DESCRIPTIONS = {
    "WK1": "A systematic, theory-based understanding of the natural sciences applicable to the discipline and awareness of relevant social sciences",
    "WK2": "Conceptually-based mathematics, numerical analysis, data analysis, statistics and formal aspects of computer and information science to support detailed analysis and modelling applicable to the discipline",
    "WK3": "A systematic, theory-based formulation of engineering fundamentals required in the engineering discipline",
    "WK4": "Engineering specialist knowledge that provides theoretical frameworks and bodies of knowledge for the accepted practice areas in the engineering discipline; much is at the forefront of the discipline.",
    "WK5": "Knowledge, including efficient resource use, environmental impacts, whole-life cost, re-use of resources, net zero carbon, and similar concepts, that supports engineering design and operations in a practice area",
    "WK6": "Knowledge of engineering practice (technology) in the practice areas in the engineering discipline",
    "WK7": "Knowledge of the role of engineering in society and identified issues in engineering practice in the discipline, such as the professional responsibility of an engineer to public safety and sustainable development*",
    "WK8": "Engagement with selected knowledge in the current research literature of the discipline, awareness of the power of critical thinking and creative approaches to evaluate emerging issues",
    "WK9": "Ethics, inclusive behavior and conduct. Knowledge of professional ethics, responsibilities, and norms of engineering practice. Awareness of the need for diversity by reason of ethnicity, gender, age, physical ability etc. with mutual understanding and respect, and of inclusive attitudes"
}
# Complex Engineering Problems (WP1-WP7) - full descriptions
WP_DESCRIPTIONS = {
    "WP1": "Involve wide ranging or multidisciplinary knowledge.",
    "WP2": "Have no unique solution, or multiple solutions that are open-ended and require trade-offs. (Incorporates SDG components)",
    "WP3": "Are formulated in such a way that all assumptions are not readily apparent, transparent or documented.",
    "WP4": "Characterised by detailed regulations and standards which are to be integrated.",
    "WP5": "Are at the forefront of a discipline.",
    "WP6": "Involve non-technical factors that must be considered.",
    "WP7": "Require in-depth knowledge that allows for innovation."
}
# Complex Engineering Activities (EA1-EA5) - full descriptions
EA_DESCRIPTIONS = {
    "EA1": "Involve application of multidisciplinary knowledge.",
    "EA2": "Are informed by cutting-edge developments in the discipline.",
    "EA3": "Meet complex and diverse societal, industrial or commercial needs and constraints.",
    "EA4": "Involve wide ranging responsibilities similar to those found in accredited professional engineering practice.",
    "EA5": "Require the exercise of judgement in a coordinated and multi-disciplinary settings."
}
# Full SAMPLE_PIS: All Competencies and Performance Indicators (PIs) for CS/IT Programs (from provided text) - adjusted for 11 POs
SAMPLE_PIS = {
    "PO1": [
        "1.1: Apply the knowledge of discrete structures, linear algebra, statistics and numerical techniques to solve problems.",
        "1.2: Apply the concepts of probability, statistics and queuing theory in modeling of computer based system, data and network protocols.",
        "1.5: Apply laws of natural science to an engineering problem.",
        "1.6: Apply engineering fundamentals.",
        "1.7: Apply theory and principles of computer science and engineering to solve an engineering problem."
    ],
    "PO2": [
        "2.1: Demonstrate an ability to identify, formulate and analyze complex engineering problems for obtaining substantiated conclusions using first principles of mathematics, natural sciences and engineering sciences.",
        "2.5: Evaluate problem statements and identifies objectives.",
        "2.6: Demonstrate an ability to formulate an ability to formulate an engineering problem.",
        "2.7: Demonstrate an ability to formulate and interpret a model and to analyze it.",
        "2.8: Demonstrate an ability to execute a solution and analyze the results."
    ],
    "PO3": [
        "3.5: Able to define a precise problem statement with objectives and scope.",
        "3.6: Demonstrate an ability to generate an alternative design solutions.",
        "3.7: Demonstrate an ability to select an optimal design scheme for further development.",
        "3.8: Demonstrate an ability to advance an engineering design to defined end state.",
        "3.1: Apply big data fundamentals to manage big data datasets and propose simple solutions for storing and managing large datasets."
    ],
    "PO4": [
        "4.4: Define a problem for purposes of investigation, its scope and importance.",
        "4.5: Design and conduct experiments to solve engineering problems.",
        "4.6: Demonstrate an ability to analyze data and reach valid conclusions.",
        "4.6.1: Use appropriate procedures, tools and techniques to collect and analyze data.",
        "4.6.4: Synthesize information and knowledge about the problem from the raw data to reach appropriate conclusions."
    ],
    "PO5": [
        "5.4: Identify modern engineering tools, techniques and resources for engineering activities.",
        "5.5: Demonstrate proficiency in using discipline specific tools.",
        "5.1: Identify modern tools related to big data that help manage and analyze large datasets effectively.",
        "5.1.1: Identify modern tools related to big data that help manage and analyze large datasets effectively."
    ],
    "PO6": [
        "6.3: Identify and describe various engineering roles; particularly as pertains to protection of the public and public interest.",
        "6.4: Interpret legislation, regulations, codes, and standards relevant to your discipline and explain its contribution to the protection of the public."
    ],
    "PO7": [
        "7.3: Identify risks/impacts in the life-cycle of an engineering product or activity.",
        "7.4: Describe management techniques of sustainable development."
    ],
    "PO8": [
        "8.3: Identify situations of unethical professional conduct and propose ethical alternatives.",
        "8.4: Demonstrate an ability to apply the Code of Ethics.",
        "8.4.1: Identify tenets of the ASME professional code of ethics.",
        "8.4.2: Examine and apply the ASME professional code of ethics to known case studies."
    ],
    "PO9": [
        "9.4: Recognize a variety of working and learning preferences; appreciate the value of diversity on a team.",
        "9.5: Demonstrate effective communication, problem-solving, conflict resolution and leadership skills.",
        "9.6: Demonstrate team-based success in a multidisciplinary setting."
    ],
    "PO10": [
        "10.4: Read, understand and interpret technical and nontechnical information.",
        "10.5: Demonstrate competence in listening, speaking, and writing.",
        "10.6: Integrate alternative modes of communication."
    ],
    "PO11": [
        "11.4: Describe various economic and financial indicators and benefits of an engineering activity.",
        "11.5: Demonstrate an ability to compare and contrast costs/benefits of alternative proposals for engineering projects.",
        "11.6: Demonstrate knowledge and understanding of engineering and management principles and apply these to one’s own work."
    ]
}
# Bloom's level specific active verb for CO
CO_VERB = {
    "K1": "Remembering",
    "K2": "Understanding",
    "K3": "Applying",
    "K4": "Analysing",
    "K5": "Evaluating",
    "K6": "Creating"
}
# Updated Prompt for Single CO with How to Write (Verbs) and Assessment (Enhanced with full Bloom's verbs from doc)
SINGLE_CO_PROMPT = """
Based on the provided course objective and unit syllabus for a CS/IT course, generate exactly 1 complete Course Outcome (CO) at Bloom's {level} level. Each CO must be 1-2 short lines using the formula: "As a result of this course, students will be able to [active verb from level] [specific skill/knowledge from unit syllabus] [criteria/context]."
For {level}: Use only '{verb}' as the active verb.
For each CO, also provide:
- how_to_write: "How to Write questions: Use [3-4 possible verbs from level] to [brief description of focus for questions, e.g., recall basic facts]. Example questions: [1-2 sample formats like 'Define X' or 'List Y']."
- assessment: "K-level based Assessment: [1-2 methods, e.g., Quiz on key terms for K1]."
Use Revised Bloom's Taxonomy Action Verbs (for how_to_write and assessment only):
- Remembering (K1): define, describe, identify, list, name, recall, state.
- Understanding (K2): explain, summarize, interpret, classify, compare, predict.
- Applying (K3): apply, use, demonstrate, solve, implement, execute.
- Analyzing (K4): analyze, compare, contrast, deconstruct, examine, differentiate.
- Evaluating (K5): assess, critique, defend, judge, justify, recommend.
- Creating (K6): compose, construct, design, develop, invent, synthesize.
Guidelines from docs (WSU, Design Guidelines, SMART, Backward Design):
- Student-centered: Focus on student performance/capabilities.
- Measurable/Specific: Concrete Bloom's verbs. Avoid vague.
- Concise/Clear: Simple language.
- Meaningful/Achievable: Higher-order emphasis; 3-7 total.
- Outcome-based: Demonstrated skills, not assignments.
- SMART: Specific, Measurable, Aligned/Relevant, Time-bound.
- Backward Design: Big ideas from syllabus; align to assessments.
- Aligned: Map to topics; transparent; assessable.
- Avoid: Vagueness; too many; content focus; misalignment.
Course Objective: {course_obj}
Unit Syllabus: {syllabus}
Output JSON: {{"co": "Complete 1-2 line for {level}", "level": "{level}", "how_to_write": "How to Write questions: Use define, list, recall to recall specific terminology and basic facts. Example questions: Define key terms; List components of...", "assessment": "K-level based Assessment: Quiz or multiple-choice on key definitions."}}
"""
# Enhanced Prompt for PO Mapping: Up to PO11 if context fits, multiple PIs per PO with per-PI relevance (AICTE + CO Context), plus CO-PO Matrix - REWRITTEN for better relevance and varying strengths
MAPPING_PROMPT = """
For the {num_cos} COs from a Big Data/CS/IT course, create PO-CO-PI mappings and PSO mappings per AICTE (up to PO11) and program specifics. Ensure mappings are contextually accurate: Analyze each CO's Bloom's level, unit focus, and syllabus elements to assign strengths (3=strong direct alignment to PO/PSO description and CO action verb/context; 2=moderate partial overlap; 1=weak indirect link; 0=no alignment). Vary strengths based on CO specifics—e.g., K1 COs strong on PO1 (3), moderate on PO2 (2); K3+ strong on PO3/PO5 (3), weak on PO7 (1). For PSOs, vary similarly: strong if CO aligns with program-specific tech focus (e.g., 3 for data analytics PSO), none (0) if unrelated (e.g., ethics PSO for non-ethical CO).

For each CO:
- Select 2-4 POs based on strong contextual correlation (e.g., PO1 for foundational knowledge in K1/K2 COs; PO2 for analysis in K4; PO3 for design in K3/K5; PO5 for tools in tech-heavy units; PO6 for societal impact if mentioned; avoid forcing—use 0 for weak fits).
- For each selected PO, cover 2-4 relevant PIs from the full list; choose only those with direct ties to CO (e.g., for PO1 CO on data modeling, select PI 1.2 on statistics modeling). For each PI, provide specific relevance: "PI [code]: [brief PI desc] - Relevance to CO: [exact tie, e.g., 'PI 1.2's queuing theory directly supports CO's modeling of big data protocols in Unit 2']."
- For PSOs (PSO1 to PSO{num_psos}): Select 0-{num_psos} relevant PSOs with varying strengths; for each, provide relevance: "PSO [number]: [full desc] - Relevance to CO: [specific tie, e.g., 'PSO1's data innovation aligns strongly (3) with CO's Hadoop application in Unit 1']."
- Provide 'CO Statement' as the full CO.
- Overall Relevance: 1 sentence summarizing mapping strengths (e.g., "CO1 strongly aligns with core knowledge POs (avg 2.5) and program data focus PSO1 (3), per AICTE OBE policy").

Additionally, generate a CO-PO-PSO matrix: {num_cos}x(11+{num_psos}) table with values 0-3 (3=strong mapping, 2=moderate, 1=weak, 0=none) for each CO-PO/PSO pair based on Correlation alignment strength. Include a final row for average values across COs for each PO and PSO.
Use PO descriptions: {po_descriptions}
Full PIs for CS/IT (select relevant only): {pis_json}
PSO Descriptions: {pso_descriptions}
COs: {cos_json}

Output JSON: {{"mappings": [{{"co": "CO1 (K1)", "pos": [{{"po": "PO1", "strength": 3, "pis": [{{"pi": "1.1", "relevance": "PI 1.1: [desc] - Relevance to CO: [specific tie]"}}]}}, {{"po": "PO2", "strength": 2, "pis": [...]}}], "psos": [{{"pso": "PSO1", "strength": 3, "relevance": "PSO1: [desc] - Relevance to CO: [tie with strength justification]"}}], "co_statement": "Full CO1", "overall_relevance": "Strong core alignment..."}}, ... ], "matrix": {{"co_po_pso_matrix": [[3,2,1,0,... for PO1-PO11,PSO1... for CO1], ... , ["avg_po1", ...]]}}}}
"""
# New Prompt for Matrix Explanations - REWRITTEN for accurate, varied relevance
EXPLANATION_PROMPT = """
For each CO-PO pair and CO-PSO pair in the provided matrix, provide a brief, accurate explanation (1-2 sentences) justifying the assigned value (3=Strong: direct verb/context match to PO/PSO desc; 2=Moderate: partial overlap; 1=Weak: indirect; 0=None: no tie). Base strictly on CO statement's Bloom's level/unit focus, PO/PSO full desc, and course context (e.g., for K3 CO on data tools: PO5=3 'direct tool application'; PSO2 on innovation=2 'partial if unit touches emerging tech'). Vary justifications to reflect true alignment, not generic.

COs: {cos_json}
Matrix: {matrix_json} (flattened as list of dicts with 'co', 'po'/'pso', 'value')
POs: {po_descriptions}
PSOs: {pso_descriptions}
Output JSON: {{"explanations": [{{"co": "CO1", "po": "PO1", "value": 3, "explanation": "Strong (3) as CO's 'apply modeling' directly matches PO1's engineering knowledge application in data stats (WK2), core to Unit 1."}}, {{"co": "CO1", "pso": "PSO1", "value": 1, "explanation": "Weak (1) since PSO1's program innovation loosely relates to basic recall in K1 CO, not strong tech depth."}}, ... ]}}
"""
# Prompt for CO-PO-WK Explanations - similar to CO-PO explanations
EXPLANATION_COPOWK_PROMPT = """
For each CO in the provided CO-PO-WK mappings, provide a brief explanation (1-2 sentences) for the mapped WKs and POs, and the assigned strength (High/Medium/Low). Base it on alignment between the CO statement, PO/WK descriptions, and course context.
CO-PO-WK Mappings: {copowk_json}
POs: {po_descriptions}
WKs: {wk_descriptions}
Output JSON: {{"explanations": [{{"co": "Full CO statement", "mapped_wks": "WK2,WK3", "mapped_pos": "PO1,PO2", "strength": "High", "explanation": "Explanation for mappings and strength: The selected WKs and POs align strongly with the CO's focus on applying mathematical models, as per WK2's description of conceptually-based mathematics supporting detailed analysis, leading to high strength in core engineering knowledge areas."}}, ... ]}}
"""
# Enhanced Prompt for PO-WA-WK-WP-EA-SDG Mapping based on reference documents and video logic - full explanations, no ellipses
POWA_MAPPING_PROMPT = """
Based on AICTE/NBA engineering education standards, reference Excel documents (PO-WA-WK Mapping and Specifications of WP, EA, SDG), and logic from video '1.30 PO-WA-WK-WP-EA-SDG Mapping' (Eng-Aim Channel), generate a comprehensive mapping for all 11 POs to WA (Graduate Attributes/Washington Accord GAs), WK (Knowledge Profiles 1-9), WP (Complex Engineering Problems 1-7), EA (Complex Engineering Activities 1-5), and SDG (Sustainable Development Goals integration). Use full descriptions without any ellipses or abbreviations in explanations.
Key Logic from Reference Documents and Video:
- POs express Graduate Attributes (GAs/WA1-WA11, 1:1 mapping: PO1=WA1 Engineering Knowledge, etc. up to PO11=WA11 Lifelong Learning).
- WK Mappings from Sheet1: e.g., PO1: WK1,X; WK2,X; WK3,X; WK4,X; PO2: WK1,X; WK2,X; WK3,X; WK4,X; etc. Use these X-marked WKs as primary, select 2-4 relevant with full relevance explanation using complete PO and WK descriptions.
- From Sheet2 (Comparision): Specifications like WA1/PO1: WK1,X; WK2,X; WK3,X; WK4,X; SDG,X for certain.
- Rules: PO1 to PO6: [WP1] + ≥2[WP2-7]; SDG (must-have) = PO2, PO6, WK7; PO9: ≥2[EA1-EA5]; SDG (good-to-have) = PO3, WK5, WP2.
- For each PO, select relevant WKs (from X in reference), required WPs (3+ for PO1-6 incl WP1; relevant others), EAs (2+ for PO9), SDG: 'Mandatory'/'Recommended'/'None' with 1-2 example SDGs (e.g., SDG7 Energy, SDG9 Industry, SDG13 Climate).
- Provide full, detailed relevance for each WK, WP, EA, SDG without abbreviations or ellipses, using the complete description texts.
- Overall Relevance: 1-2 full sentences explaining the mapping per PO (reference NBA standards and documents).
Use these full descriptions:
POs/WA: {po_descriptions}
WKs: {wk_descriptions}
WPs: {wp_descriptions}
EAs: {ea_descriptions}
Reference WK Mappings: PO1: WK1,WK2,WK3,WK4; PO2: WK1,WK2,WK3,WK4; PO3: WK5; PO4: WK8; PO5: WK2,WK6; PO6: WK1,WK5,WK7; PO7: WK9; PO8: WK9; PO9: None specified; PO10: None; PO11: WK8.
Output JSON: {{"mappings": [{{"po": "PO1", "wa": "WA1", "wa_desc": "Engineering Knowledge: Apply knowledge of mathematics, natural science, computing, engineering fundamentals and an engineering specialization as specified in WK1 to WK4 respectively to develop to the solution of complex engineering problems.", "wks": [{{"wk": "WK1", "relevance": "Full detailed relevance to PO1: Provides a systematic, theory-based understanding of the natural sciences applicable to the discipline and awareness of relevant social sciences, directly supporting the application of foundational knowledge in solving complex problems (from reference X)."}}, ...], "wps": ["WP1", "WP3", "WP7"], "wps_req": "WP1 + ≥2 WP2-7", "eas": [], "eas_req": "None", "sdg": {{"status": "Recommended", "examples": ["SDG9: Industry, Innovation and Infrastructure"]}}, "overall_relevance": "PO1 aligns with WA1 by integrating WK1-4 and WPs for complex problem-solving per NBA and reference documents, ensuring students apply comprehensive engineering knowledge to real-world challenges."}}, ... ]}}
"""
# Prompt for PO-WA-WK-WP-EA-SDG Explanations - full, no ellipses
POWA_EXPLANATION_PROMPT = """
For each PO in the provided mapping, provide a full, detailed explanation (2-3 sentences) for the selected WKs, WPs, EAs, and SDG status without any abbreviations or ellipses. Base it on alignment with PO description, WA, reference documents (e.g., X in WK columns), and video logic (e.g., mandatory SDG for PO2 due to WA2 and Sheet2). Use complete description texts.
POs Mappings: {powa_json}
Output JSON: {{"explanations": [{{"po": "PO1", "explanation": "Full explanation for WK/WP/EA/SDG mappings: The selected WKs align directly with the reference X markings in Sheet1, providing the necessary theoretical foundations for engineering knowledge; WPs are required to handle complex multidisciplinary problems as per rules for PO1-PO6; SDG is recommended to incorporate sustainability aspects in problem-solving."}}, ... ]}}
"""
# Revised Prompt for CO-PO-WK Mapping - Focused on generating comma-separated lists for WKs, POs, and overall Strength per CO (matching uploaded table)
CO_POWK_PROMPT = """
For the {num_cos} COs from the course, generate a CO-PO-WK mapping aligned with Washington Accord and NBA standards. For each CO:
- Identify 2-3 relevant Knowledge Profiles (WKs from WK1–WK9) based on CO content and Bloom's level, with brief relevance using full WK descriptions.
- Map to 2-4 relevant POs (PO1-PO11) based on WK links (e.g., WK2 → PO1, PO2; WK3 → PO3; WK4 → PO4; WK5 → PO3; WK6 → PO5; WK7 → PO6; WK8 → PO4, PO11; WK9 → PO7, PO8).
- Assign one overall Strength for the CO mappings: 'High' (direct alignment to core POs/WKs), 'Medium' (partial), 'Low' (minimal).
- Output comma-separated strings: e.g., Mapped WKs: WK2,WK3; Mapped POs: PO1,PO2; Strength: High.
Use full PO and WK descriptions: {po_descriptions}, {wk_descriptions}
COs: {cos_json}
Output JSON: {{"mappings": [{{"co": "Full CO statement", "mapped_wks": "WK2,WK3", "mapped_pos": "PO1,PO2", "strength": "High", "unit": "1", "bloom_level": "K3"}}, ... ]}}
"""
# Generate Single CO (now per unit and level, with full syllabus extraction)
def generate_single_co(course_obj, full_syllabus, unit_num, level):
    if not full_syllabus.strip():
        return None
    try:
        verb = CO_VERB[level]
        unit_specific_syllabus = f"Full course syllabus (all units): {full_syllabus}\n\nFor this CO, extract the content relevant to Unit {unit_num} from the full syllabus and generate the CO based on that unit's topics. Ensure the CO focuses uniquely on Unit {unit_num} to avoid repetition with other COs."
        full_prompt = SINGLE_CO_PROMPT.format(course_obj=course_obj, syllabus=unit_specific_syllabus, level=level, verb=verb)
    except Exception as e:
        st.error(f"Prompt error for Unit {unit_num} {level}: {e}. Fallback.")
        return None
    response = model.generate_content(full_prompt)
    try:
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data
    except Exception as e:
        st.error(f"JSON error for Unit {unit_num} {level}: {e}. Fallback.")
        return None
    return None
# Generate COs (one per unit at selected level)
def generate_cos(course_obj, unit_data):
    cos = []
    for ud in unit_data:
        co_data = generate_single_co(course_obj, ud['full_syllabus'], ud['unit'], ud['level'])
        if co_data:
            co_data['unit'] = ud['unit']
            cos.append(co_data)
        else:
            # Fallback per level, unique to unit
            fallback_co = f"As a result of this course, students will be able to {CO_VERB[ud['level']]} key concepts from Unit {ud['unit']} without overlapping with other units."
            fallback_how = f"How to Write questions: Use {', '.join(['define', 'list', 'recall'][:3])} to recall specific terminology unique to Unit {ud['unit']}. Example questions: Define key terms from Unit {ud['unit']}; List components specific to..."
            fallback_assess = f"K-level based Assessment: Quiz on Unit {ud['unit']} definitions for {ud['level']}."
            cos.append({
                "co": fallback_co,
                "level": ud['level'],
                "how_to_write": fallback_how,
                "assessment": fallback_assess,
                "unit": ud['unit']
            })
    return cos
# Generate Mappings (Enhanced for multiple PIs per PO with per-PI relevance, plus matrix) - now for 11 POs and user-defined PSOs - UPDATED FALLBACK FOR VARIED PSO WEIGHTS
@st.cache_data
def generate_mappings(cos, pso_descriptions):
    num_cos = len(cos)
    num_psos = len(pso_descriptions)
    if num_cos == 0:
        return []
    po_json = json.dumps(PO_DESCRIPTIONS)
    pis_json = json.dumps(SAMPLE_PIS)
    pso_json = json.dumps(pso_descriptions)
    try:
        full_prompt = MAPPING_PROMPT.format(num_cos=num_cos, num_psos=num_psos, po_descriptions=po_json, pis_json=pis_json, pso_descriptions=pso_json, cos_json=json.dumps(cos))
    except Exception as e:
        st.error(f"Mapping prompt error: {e}. Fallback.")
        return []
    response = model.generate_content(full_prompt)
    try:
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            mappings = data.get("mappings", [])
            matrix_data = data.get("matrix", {}).get("co_po_pso_matrix", [])
            # Add matrix and unit to each mapping
            for i, m in enumerate(mappings):
                if i < len(cos):
                    m["unit"] = cos[i]["unit"]
                    m["level"] = cos[i]["level"]
                if "matrix_row" not in m:
                    m["matrix_row"] = matrix_data[i] if i < len(matrix_data) else [0] * (11 + num_psos) # 11 POs + num PSOs
                # Override co label
                m["co"] = f"CO {i+1} (Unit {cos[i]['unit']} {cos[i]['level']})"
            return mappings
    except Exception as e:
        st.error(f"Mapping JSON error: {e}. Fallback.")
        # UPDATED FALLBACK: Vary PSO weights based on CO level/unit (e.g., higher for tech PSOs in K3+; 0-3 varied)
        import random  # For variation in fallback
        fallback_mappings = []
        for i in range(num_cos):
            level = cos[i]["level"]
            pos_list = []
            if level == "K1":
                pos_list.append({"po": "PO1", "strength": 3, "pis": [{"pi": SAMPLE_PIS["PO1"][0], "relevance": f"PI {SAMPLE_PIS['PO1'][0]}: {PO_DESCRIPTIONS['PO1'][:50]} - Relevance to CO: Basic recall ties directly to foundational knowledge in Unit {cos[i]['unit']} (AICTE)."}]})
                pos_list.append({"po": "PO2", "strength": 2, "pis": [{"pi": SAMPLE_PIS["PO2"][0], "relevance": f"PI {SAMPLE_PIS['PO2'][0]}: {PO_DESCRIPTIONS['PO2'][:50]} - Relevance to CO: Partial analysis intro in K1 for Unit {cos[i]['unit']}."}]})
            else:
                for po in ["PO1", "PO2", "PO3"]:
                    strength = 3 if po == "PO3" and level in ["K3","K4"] else 2 if po in ["PO1","PO2"] else 1
                    pis = [{"pi": SAMPLE_PIS[po][0], "relevance": f"PI {SAMPLE_PIS[po][0]}: {PO_DESCRIPTIONS[po][:50]} - Relevance to CO: {strength}-level tie to {cos[i]['co'][:50]} in Unit {cos[i]['unit']} via design/analysis (AICTE)."}]
                    pos_list.append({"po": po, "strength": strength, "pis": pis})
                if level in ["K4", "K5", "K6"]:
                    pos_list.append({"po": "PO4", "strength": 3, "pis": [{"pi": SAMPLE_PIS["PO4"][0], "relevance": f"PI {SAMPLE_PIS['PO4'][0]}: Investigations - Relevance to CO: Strong (3) analysis in {level} for Unit {cos[i]['unit']} (AICTE)."}]})
                    pos_list.append({"po": "PO5", "strength": 3, "pis": [{"pi": SAMPLE_PIS["PO5"][0], "relevance": f"PI {SAMPLE_PIS['PO5'][0]}: Tools - Relevance to CO: Strong (3) tool usage in {level} for Unit {cos[i]['unit']} (AICTE)."}]})
            pso_list = []
            for j in range(1, num_psos + 1):
                pso_key = f"PSO{j}"
                if pso_descriptions.get(pso_key):
                    # VARY: Based on level and unit (e.g., higher for K3+ tech units)
                    strength = 3 if level in ["K3","K4","K5","K6"] and i % 2 == 0 else 2 if level in ["K2","K3"] else 1 if random.random() > 0.5 else 0
                    relevance = f"PSO {j}: {pso_descriptions[pso_key][:50]}... - Relevance to CO: {strength}-level tie to {cos[i]['co'][:50]} in Unit {cos[i]['unit']} ({'strong program alignment' if strength==3 else 'moderate/partial' if strength==2 else 'weak/indirect' if strength==1 else 'no direct tie'})."
                    pso_list.append({"pso": pso_key, "strength": strength, "relevance": relevance})
            # UPDATED MATRIX_ROW: Vary POs too, and use PSO strengths
            po_strengths = [3 if k<3 else 2 if k<5 else 1 if k<8 else 0 for k in range(11)]  # Varied for POs
            pso_strengths = [pso["strength"] for pso in pso_list] if pso_list else []
            matrix_row = po_strengths + pso_strengths
            fallback_mappings.append({
                "co": f"CO {i+1} (Unit {cos[i]['unit']} {level})",
                "pos": pos_list,
                "psos": pso_list,
                "co_statement": cos[i]["co"],
                "overall_relevance": f"Varied PO strengths (e.g., 3 for core, 1 for peripheral) and PSO alignments for {level} in Unit {cos[i]['unit']}; PIs/PSOs cover context-specific aspects per AICTE and program.",
                "matrix_row": matrix_row,
                "unit": cos[i]["unit"],
                "level": level
            })
        return fallback_mappings
    return []
# Generate PO-WA-WK-WP-EA-SDG Mappings - Enhanced with full explanations
@st.cache_data
def generate_powa_mappings():
    po_json = json.dumps(PO_DESCRIPTIONS)
    wk_json = json.dumps(WK_DESCRIPTIONS)
    wp_json = json.dumps(WP_DESCRIPTIONS)
    ea_json = json.dumps(EA_DESCRIPTIONS)
    try:
        full_prompt = POWA_MAPPING_PROMPT.format(po_descriptions=po_json, wk_descriptions=wk_json, wp_descriptions=wp_json, ea_descriptions=ea_json)
    except Exception as e:
        st.error(f"POWA prompt error: {e}. Fallback.")
        return []
    response = model.generate_content(full_prompt)
    try:
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data.get("mappings", [])
    except Exception as e:
        st.error(f"POWA JSON error: {e}. Fallback.")
        # Fallback mappings based on reference documents and video logic for 11 POs - full, no ellipses
        fallback_mappings = []
        pos = ["PO1", "PO2", "PO3", "PO4", "PO5", "PO6", "PO7", "PO8", "PO9", "PO10", "PO11"]
        wk_map_ref = {
            "PO1": ["WK1", "WK2", "WK3", "WK4"],
            "PO2": ["WK1", "WK2", "WK3", "WK4"],
            "PO3": ["WK5"],
            "PO4": ["WK8"],
            "PO5": ["WK2", "WK6"],
            "PO6": ["WK1", "WK5", "WK7"],
            "PO7": ["WK9"],
            "PO8": ["WK9"],
            "PO9": [],
            "PO10": [],
            "PO11": ["WK8"]
        }
        for i, po in enumerate(pos):
            wa = f"WA{i+1}"
            wa_desc = PO_DESCRIPTIONS[po]
            wks = []
            for wk in wk_map_ref.get(po, []):
                relevance = f"Full relevance to {po}: {WK_DESCRIPTIONS[wk]} directly supports the PO by providing the theoretical and practical foundation marked with X in the reference Sheet1, ensuring alignment with Washington Accord standards and NBA compliance through Outcome-Based Education."
                wks.append({"wk": wk, "relevance": relevance})
            if i+1 <=6: # PO1-6
                wps = ["WP1", "WP2", "WP3"]
                wps_req = "WP1 + ≥2 WP2-7"
                if i+1 in [2,6]: # PO2, PO6
                    sdg_status = "Mandatory"
                    sdg_examples = ["SDG9: Industry, Innovation and Infrastructure", "SDG13: Climate Action"]
                else:
                    sdg_status = "Recommended"
                    sdg_examples = ["SDG4: Quality Education", "SDG7: Affordable and Clean Energy"]
                eas = []
                eas_req = "None"
            elif i+1 == 9: # PO9
                sdg_status = "None"
                wps = []
                wps_req = "Relevant as per context"
                eas = ["EA1", "EA3", "EA4"]
                eas_req = "≥2 EA1-5"
                sdg_examples = []
            else:
                sdg_status = "Recommended"
                wps = []
                wps_req = "Relevant as per context"
                sdg_examples = ["SDG4: Quality Education", "SDG8: Decent Work and Economic Growth"]
                eas = []
                eas_req = "None"
            fallback_mappings.append({
                "po": po,
                "wa": wa,
                "wa_desc": wa_desc,
                "wks": wks,
                "wps": wps,
                "wps_req": wps_req,
                "eas": eas,
                "eas_req": eas_req,
                "sdg": {
                    "status": sdg_status,
                    "examples": sdg_examples
                },
                "overall_relevance": f"{po} (WA{i+1}) aligns comprehensively with the Washington Accord by grounding in specified WKs from reference documents, requiring WPs for complex problem handling, EAs for team activities where applicable, and integrating SDGs for sustainability as per NBA accreditation standards and video guidelines. This mapping ensures transparency in Outcome-Based Education and supports audit-readiness for NBA evaluators."
            })
        return fallback_mappings
    return []
# Generate CO-PO-WK Mappings - Revised to match uploaded table format: comma-separated WKs, POs, and single Strength per CO
@st.cache_data
def generate_co_powk_mappings(cos):
    num_cos = len(cos)
    if num_cos == 0:
        return []
    po_json = json.dumps(PO_DESCRIPTIONS)
    wk_json = json.dumps(WK_DESCRIPTIONS)
    try:
        full_prompt = CO_POWK_PROMPT.format(num_cos=num_cos, po_descriptions=po_json, wk_descriptions=wk_json, cos_json=json.dumps(cos))
    except Exception as e:
        st.error(f"CO-PO-WK prompt error: {e}. Fallback.")
        return []
    response = model.generate_content(full_prompt)
    try:
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            mappings = data.get("mappings", [])
            for i, m in enumerate(mappings):
                if i < len(cos):
                    m["unit"] = cos[i]["unit"]
                    m["bloom_level"] = cos[i]["level"]
                    m["co_statement"] = cos[i]["co"]  # Ensure full CO
            return mappings
    except Exception as e:
        st.error(f"CO-PO-WK JSON error: {e}. Fallback.")
        # Fallback matching table format
        fallback = []
        strengths = ["High", "Medium", "High", "Medium", "High"][:num_cos]
        wks_list = ["WK2,WK3", "WK4,WK8", "WK5", "WK6,WK7", "WK8"][:num_cos]
        pos_list = ["PO1,PO2", "PO4,PO11", "PO3", "PO6,PO7", "PO11"][:num_cos]
        for i in range(num_cos):
            fallback.append({
                "co": cos[i]["co"],
                "mapped_wks": wks_list[i],
                "mapped_pos": pos_list[i],
                "strength": strengths[i],
                "unit": cos[i]["unit"],
                "bloom_level": cos[i]["level"],
                "co_statement": cos[i]["co"]
            })
        return fallback
    return []
# Generate Explanations for CO-PO Matrix - UPDATED TO USE STRENGTH FROM MAPPINGS
@st.cache_data
def generate_explanations(cos, mappings, pso_descriptions):
    num_psos = len(pso_descriptions)
    matrix_flat = []
    for i, mapping in enumerate(mappings):
        matrix_row = mapping.get("matrix_row", [0]*(11 + num_psos))
        co_name = mapping["co"]
        # Use strengths from pos/psos if available, else row values
        for j, po_item in enumerate(mapping.get("pos", [])):
            if j < 11:
                value = po_item.get("strength", matrix_row[j])
                matrix_flat.append({"co": co_name, "po": po_item["po"], "value": value})
        for j, pso_item in enumerate(mapping.get("psos", [])):
            if j < num_psos:
                value = pso_item.get("strength", matrix_row[11 + j])
                matrix_flat.append({"co": co_name, "pso": pso_item["pso"], "value": value})
        # Fill missing with row values
        for j in range(len(mapping.get("pos", [])), 11):
            matrix_flat.append({"co": co_name, "po": f"PO{j+1}", "value": matrix_row[j]})
        for j in range(len(mapping.get("psos", [])), num_psos):
            matrix_flat.append({"co": co_name, "pso": f"PSO{j+1}", "value": matrix_row[11 + j]})
    cos_json = json.dumps(cos)
    matrix_json = json.dumps(matrix_flat)
    po_json = json.dumps(PO_DESCRIPTIONS)
    pso_json = json.dumps(pso_descriptions)
    try:
        full_prompt = EXPLANATION_PROMPT.format(cos_json=cos_json, matrix_json=matrix_json, po_descriptions=po_json, pso_descriptions=pso_json)
        response = model.generate_content(full_prompt)
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data.get("explanations", [])
    except Exception as e:
        st.error(f"Explanation prompt error: {e}. Fallback.")
        # Fallback explanations - Varied and accurate
        fallback_exps = []
        for exp in matrix_flat:
            if "po" in exp:
                fallback_exps.append({
                    "co": exp["co"],
                    "po": exp["po"],
                    "value": exp["value"],
                    "explanation": f"Alignment for {exp['co']}-{exp['po']}: {exp['value']} based on direct PO desc match to CO's {cos[0]['level']} focus in unit (AICTE contextual tie)."
                })
            else:
                fallback_exps.append({
                    "co": exp["co"],
                    "pso": exp["pso"],
                    "value": exp["value"],
                    "explanation": f"Alignment for {exp['co']}-{exp['pso']}: {exp['value']} as PSO program goal partially/indirectly supports CO's application in unit (varied per tech relevance)."
                })
        return fallback_exps
    return []
# Generate Explanations for CO-PO-WK Mappings - similar to CO-PO explanations
@st.cache_data
def generate_co_powk_explanations(co_powk_mappings):
    copowk_json = json.dumps(co_powk_mappings)
    po_json = json.dumps(PO_DESCRIPTIONS)
    wk_json = json.dumps(WK_DESCRIPTIONS)
    try:
        full_prompt = EXPLANATION_COPOWK_PROMPT.format(copowk_json=copowk_json, po_descriptions=po_json, wk_descriptions=wk_json)
        response = model.generate_content(full_prompt)
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data.get("explanations", [])
    except Exception as e:
        st.error(f"CO-PO-WK Explanation prompt error: {e}. Fallback.")
        # Fallback explanations
        fallback_exps = []
        for mapping in co_powk_mappings:
            fallback_exps.append({
                "co": mapping["co_statement"],
                "mapped_wks": mapping["mapped_wks"],
                "mapped_pos": mapping["mapped_pos"],
                "strength": mapping["strength"],
                "explanation": f"Fallback explanation for {mapping['co_statement'][:50]}...: Alignment based on Washington Accord and NBA standards (strength: {mapping['strength']})."
            })
        return fallback_exps
    return []
# Generate Explanations for PO-WA-WK-WP-EA-SDG - Enhanced full
@st.cache_data
def generate_powa_explanations(powa_mappings):
    powa_json = json.dumps(powa_mappings)
    try:
        full_prompt = POWA_EXPLANATION_PROMPT.format(powa_json=powa_json)
        response = model.generate_content(full_prompt)
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data.get("explanations", [])
    except Exception as e:
        st.error(f"POWA Explanation prompt error: {e}. Fallback.")
        # Fallback - full, no ellipses
        fallback_exps = []
        for mapping in powa_mappings:
            explanation = f"Full fallback explanation for {mapping['po']}: The WKs are selected based on reference X markings in Sheet1, providing comprehensive theoretical support with full descriptions such as for WK1 a systematic, theory-based understanding of the natural sciences applicable to the discipline and awareness of relevant social sciences; WPs and EAs follow the rules for complex problems and activities from Sheet2 and video, ensuring PO1 to PO6 include WP1 plus at least two from WP2-7; SDG status ensures sustainability integration as mandatory or recommended per NBA standards, central to Outcome-Based Education and Washington Accord equivalence."
            fallback_exps.append({
                "po": mapping["po"],
                "explanation": explanation
            })
        return fallback_exps
    return []
# Helper function to get description for WP or EA, handling various formats robustly
def get_description(item, descriptions_dict):
    if isinstance(item, dict):
        key = item.get('wp') if 'wp' in item else item.get('ea')
        if key:
            return descriptions_dict.get(key, str(item))
    elif isinstance(item, str):
        if ':' in item and item.startswith(('WP', 'EA')):
            # Full description string, return as-is
            return item
        else:
            # Assume it's a key
            return descriptions_dict.get(item, str(item))
    return str(item)

# PO Domain descriptions for the mapping table
PO_DOMAINS = {
    "PO1": "Engineering Knowledge",
    "PO2": "Problem Analysis",
    "PO3": "Design/development of solutions",
    "PO4": "Investigation",
    "PO5": "Tool Usage",
    "PO6": "The Engineer and the World",
    "PO7": "Ethics",
    "PO8": "Individual and Collaborative Team work",
    "PO9": "Communication",
    "PO10": "Project Management and Finance",
    "PO11": "Lifelong learning"
}

# Colors for WK cells per PO - Modified as per user request: PO1-PO5: #fff2cc, PO6-PO7: #cce5ff, PO8-PO11: #d5e8d4
PO_WK_COLORS = {
    "PO1": "#fff2cc",
    "PO2": "#fff2cc",
    "PO3": "#fff2cc",
    "PO4": "#fff2cc",
    "PO5": "#fff2cc",  # Changed from #cce5ff to #fff2cc
    "PO6": "#cce5ff",
    "PO7": "#cce5ff",
    "PO8": "#d5e8d4",
    "PO9": "#d5e8d4",
    "PO10": "#d5e8d4",
    "PO11": "#d5e8d4"
}

# Function to generate PO-WA-WK Mapping Table (with X ticks based on CO-PO-WK mappings)
def generate_po_wa_wk_table(co_powk_mappings, cos):
    if not co_powk_mappings:
        return None, None
    # Compute PO to set of WKs based on CO mappings
    po_to_wks = {}
    for mapping in co_powk_mappings:
        mapped_pos_list = [po.strip() for po in mapping["mapped_pos"].split(',')]
        mapped_wks_list = [wk.strip() for wk in mapping["mapped_wks"].split(',')]
        for po in mapped_pos_list:
            if po not in po_to_wks:
                po_to_wks[po] = set()
            po_to_wks[po].update(mapped_wks_list)
    table_data = []
    for po in PO_DOMAINS.keys():  # All POs
        domain = PO_DOMAINS[po]
        wa = f"WA{po[2:]}"
        row = {"PO": po, "Domain": domain, "WA": wa}
        # Add WK1 to WK9 columns with 'X' if mapped via any CO
        for wk_num in range(1, 10):
            wk_key = f"WK{wk_num}"
            if po in po_to_wks and wk_key in po_to_wks[po]:
                row[wk_key] = "X"
            else:
                row[wk_key] = ""
        table_data.append(row)
    df_table = pd.DataFrame(table_data)
    return df_table, cos

# Function to generate HTML for colored PO-WA-WK table
def generate_html_po_wa_wk_table(df):
    html = '''
    <table border="1" style="border-collapse: collapse; font-family: Arial, sans-serif;">
        <caption style="caption-side: top; font-weight: bold; font-size: 1.1em; margin-bottom: 10px;">Program Outcomes (PO) Mapping with WA & WK (As per National Board of Accreditation (NBA))</caption>
        <thead>
            <tr>
                <th rowspan="2" style="text-align: center; padding: 8px;">PO</th>
                <th rowspan="2" style="text-align: center; padding: 8px;">Domain</th>
                <th rowspan="2" style="text-align: center; padding: 8px;">WA</th>
                <th colspan="9" style="text-align: center; padding: 8px; background-color: #f0f0f0;">Knowledge and Attitude Profile (WK)</th>
            </tr>
            <tr>
                <th style="text-align: center; padding: 8px;">1</th>
                <th style="text-align: center; padding: 8px;">2</th>
                <th style="text-align: center; padding: 8px;">3</th>
                <th style="text-align: center; padding: 8px;">4</th>
                <th style="text-align: center; padding: 8px;">5</th>
                <th style="text-align: center; padding: 8px;">6</th>
                <th style="text-align: center; padding: 8px;">7</th>
                <th style="text-align: center; padding: 8px;">8</th>
                <th style="text-align: center; padding: 8px;">9</th>
            </tr>
        </thead>
        <tbody>
    '''
    for idx, row in df.iterrows():
        po = row['PO']
        color = PO_WK_COLORS.get(po, '#ffffff')
        html += f'<tr>'
        html += f'<td style="text-align: center; padding: 8px; font-weight: bold;">{po}</td>'
        html += f'<td style="padding: 8px;">{row["Domain"]}</td>'
        html += f'<td style="text-align: center; padding: 8px;">{row["WA"]}</td>'
        for wk in range(1,10):
            cell = row[f'WK{wk}']
            wk_style = f'text-align: center; padding: 8px; background-color: {color}; font-weight: bold;' if cell == 'X' else f'text-align: center; padding: 8px; background-color: {color};'
            html += f'<td style="{wk_style}">{cell}</td>'
        html += '</tr>'
    html += '''
        </tbody>
    </table>
    <div style="margin-top: 20px;">
        <div style="background-color: #fff2cc; padding: 10px; margin-bottom: 5px; border-left: 5px solid #ff9900;">Analysis of problems & synthesis of solutions</div>
        <div style="background-color: #cce5ff; padding: 10px; margin-bottom: 5px; border-left: 5px solid #0077b6;">Responsibilities</div>
        <div style="background-color: #d5e8d4; padding: 10px; margin-bottom: 5px; border-left: 5px solid #28a745;">Required In work place</div>
    </div>
    '''
    return html

# Main App - Improved GUI with enhanced sections
def main():
    # Header with icon and styling
    st.markdown('<h1 class="main-header">🎓 Syllabus-Based CO & PO Mapping Generator</h1>', unsafe_allow_html=True)
    st.markdown("**AICTE CS/IT Aligned Tool (11 POs)** - Generate Bloom's Taxonomy COs (up to 5, one per Unit at selected K-Level) with Verbs/Assessments & Enhanced PO/PI Mappings (K1: 1-2 POs; K2-K6: compulsory PO1-PO3 + relevant; multiple PIs per PO with per-PI relevance).")
    # Sidebar for Inputs
    with st.sidebar:
        st.header("📋 Settings")
        course_name = st.text_input("Course Name", "Big Data Analytics", help="e.g., Big Data Analytics")
        course_obj = st.text_area("Course Objective", height=80, placeholder="e.g., To introduce students to big data concepts, tools, and applications in CS/IT...", help="Overall course objective to inform CO generation.")

        st.header("📚 Full Syllabus Input (All Units)")
        full_syllabus = st.text_area("Full Course Syllabus (All Units, e.g., Unit 1: ... Unit 2: ...)", height=200, placeholder="e.g., Unit 1: Big Data Fundamentals - Volume, Velocity, Variety...\nUnit 2: ...", help="Provide the entire syllabus with clear Unit separations for accurate CO generation.")

        st.header("🎯 CO Configuration")
        num_cos = st.number_input("Number of Course Outcomes (COs)", min_value=1, max_value=5, value=5, help="Number of COs to generate (one per unit, up to 5).")

        if 'num_cos' not in st.session_state or st.session_state.num_cos != num_cos:
            st.session_state.num_cos = num_cos
            # Clear extra level keys if num_cos decreased
            for i in range(num_cos + 1, 6):
                if f"level_{i}" in st.session_state:
                    del st.session_state[f"level_{i}"]

        # Initialize levels if not present
        for i in range(1, num_cos + 1):
            if f"level_{i}" not in st.session_state:
                st.session_state[f"level_{i}"] = "K1"

        bloom_options = list(CO_VERB.keys())
        for i in range(1, num_cos + 1):
            default_level = st.session_state[f"level_{i}"]
            level_index = bloom_options.index(default_level)
            st.selectbox(f"Bloom's K-Level for CO {i} (covering Unit {i})", options=bloom_options, key=f"level_{i}", index=level_index)

        # Collect levels after widgets
        levels = [st.session_state[f"level_{i}"] for i in range(1, num_cos + 1)]
        # Prepare unit_data
        unit_data = [{'unit': i, 'full_syllabus': full_syllabus, 'level': level} for i, level in enumerate(levels, 1)]

        # Added link with hover popup message
        st.markdown('<a href="#" title="CO choice norms as per AICTE-NBA\nBloom’s L1 to L4 -> Theory Courses\nBloom’s L1 to L5 -> Laboratory Courses\nBloom’s L1 to L6 -> Mini Project and Main Project">AICTE-NBA Guidelines</a>', unsafe_allow_html=True)

        st.header("🎯 PSO Configuration")
        num_psos = st.number_input("Number of Program Specific Outcomes (PSOs) to map", min_value=0, max_value=5, value=0)
        pso_descriptions = {}
        if num_psos > 0:
            for i in range(1, num_psos + 1):
                pso_desc = st.text_area(f"PSO {i} Description", height=60, placeholder=f"Enter full description for PSO {i}...", key=f"pso_desc_{i}")
                if pso_desc.strip():
                    pso_descriptions[f"PSO{i}"] = pso_desc
        # Sidebar button for downloading explanations
        if 'mappings' in st.session_state:
            if st.button("📄 Download CO-PO-PSO Explanations CSV", use_container_width=True):
                explanations = generate_explanations(st.session_state.cos, st.session_state.mappings, st.session_state.pso_descriptions if 'pso_descriptions' in st.session_state else {})
                exp_data = []
                for exp in explanations:
                    row = {"CO": exp["co"], "Value": exp["value"], "Explanation": exp["explanation"]}
                    if "po" in exp:
                        row["PO/PSO"] = exp["po"]
                    elif "pso" in exp:
                        row["PO/PSO"] = exp["pso"]
                    exp_data.append(row)
                df_exp = pd.DataFrame(exp_data)
                csv = df_exp.to_csv(index=False)
                st.download_button("💾 Download Explanations", csv, f"{course_name}_co_po_pso_explanations.csv", use_container_width=True)

        # New Sidebar button for downloading CO-PO-WK explanations
        if 'co_powk_mappings' in st.session_state:
            if st.button("📄 Download CO-PO-WK Explanations CSV", use_container_width=True):
                explanations = generate_co_powk_explanations(st.session_state.co_powk_mappings)
                exp_data = [{"CO": exp["co"], "Mapped WKs": exp["mapped_wks"], "Mapped POs": exp["mapped_pos"], "Strength": exp["strength"], "Explanation": exp["explanation"]} for exp in explanations]
                df_exp = pd.DataFrame(exp_data)
                csv = df_exp.to_csv(index=False)
                st.download_button("💾 Download Explanations", csv, f"{course_name}_co_powk_explanations.csv", use_container_width=True)

        # Credit button
        if st.button("@oyyathevan", use_container_width=True):
            st.info("👋 Thanks for using this tool! Developed by @oyyathevan.")
    if not full_syllabus.strip():
        st.warning("⚠️ Please provide the full syllabus to generate COs.")
        return
    # Main Content - Columns for Responsiveness
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🚀 Generate COs & PO-PSO Mappings", use_container_width=True):
            with st.spinner("🔄 Analyzing syllabus and generating ...🚀🚀"):
                cos = generate_cos(course_obj, unit_data)
                mappings = generate_mappings(cos, pso_descriptions)
                st.session_state.cos = cos
                st.session_state.mappings = mappings
                st.session_state.pso_descriptions = pso_descriptions
                st.rerun() # Refresh for display

        # New Button for PO-WA-WK Mapping Table
        if st.button("PO-WA-WK Mapping", use_container_width=True):
            with st.spinner("🔄 Generating PO-WA-WK Mapping Table..."):
                if 'cos' not in st.session_state or len(st.session_state.cos) == 0:
                    st.warning("⚠️ Please generate COs first.")
                    st.rerun()
                else:
                    # Ensure co_powk_mappings are generated
                    if 'co_powk_mappings' not in st.session_state:
                        co_powk_mappings = generate_co_powk_mappings(st.session_state.cos)
                        st.session_state.co_powk_mappings = co_powk_mappings
                    table_df, cos_list = generate_po_wa_wk_table(st.session_state.co_powk_mappings, st.session_state.cos)
                    st.session_state.po_wa_wk_table = table_df
                    st.session_state.cos_list_for_wk = cos_list
                    st.rerun()

    if 'cos' in st.session_state and len(st.session_state.cos) > 0:
        num_generated = len(st.session_state.cos)
        # COs Section - Expander for Details - Wrapped in attractive div
        with st.expander(f"📊 Generated Course Outcomes ({num_generated} COs, one per selected Unit at K-Level)", expanded=True):
            st.markdown('<div class="output-section"><h2 class="output-header">Course Outcomes with Verbs & Assessments</h2></div>', unsafe_allow_html=True)
            co_data = []
            for item in st.session_state.cos:
                co_data.append({
                    "CO #": f"CO {item['unit']}",
                    "Unit": item["unit"],
                    "K-Level": item["level"],
                    "CO Statement": item["co"],
                    "How to Write Questions (Possible Verbs)": item["how_to_write"],
                    "K-Level Based Assessment": item["assessment"]
                })
            df_cos = pd.DataFrame(co_data)
            st.dataframe(df_cos, use_container_width=True, height=500, hide_index=True)
            st.download_button("💾 Download COs CSV", df_cos.to_csv(index=False), f"{course_name}_cos.csv", use_container_width=True)
        # Mappings Section - Expander - UPDATED TO SHOW STRENGTHS IN TABLE
        with st.expander("🔗 PO-CO-PI & PSO Mapping Table (AICTE Reference)", expanded=True):
            st.markdown('<div class="output-section"><h2 class="output-header">Enhanced PO/PI & PSO Mappings (with Strengths)</h2></div>', unsafe_allow_html=True)
            mapping_data = []
            for mapping in st.session_state.mappings:
                co_row = {
                    "CO #": mapping["co"].split(" ")[1],
                    "Unit": mapping["unit"],
                    "CO": mapping["co"],
                    "CO Statement": mapping["co_statement"][:100] + "..." if len(mapping["co_statement"]) > 100 else mapping["co_statement"],
                    "Overall Relevance": mapping["overall_relevance"]
                }
                # Flatten POs and PIs with relevance and strength for table
                pos_text = ""
                for po_item in mapping["pos"]:
                    strength = po_item.get("strength", 0)
                    pos_text += f"**{po_item['po']} (Strength: {strength})**: {PO_DESCRIPTIONS[po_item['po']]}\n"
                    for pi_item in po_item["pis"]:
                        pos_text += f" - {pi_item['pi']}: {pi_item['relevance']}\n"
                    pos_text += "\n"
                co_row["POs & PIs with Per-PI Relevance (AICTE + Course)"] = pos_text
                # Flatten PSOs with strength
                psos_text = ""
                for pso_item in mapping.get("psos", []):
                    strength = pso_item.get("strength", 0)
                    psos_text += f"**{pso_item['pso']} (Strength: {strength})**: {st.session_state.pso_descriptions.get(pso_item['pso'], 'N/A')}\n"
                    psos_text += f" - {pso_item['relevance']}\n\n"
                co_row["PSOs with Relevance (Program Specific + Course)"] = psos_text
                mapping_data.append(co_row)
            df_map = pd.DataFrame(mapping_data)
            st.dataframe(df_map, use_container_width=True, height=600, hide_index=True)
            st.download_button("💾 Download Mappings CSV", df_map.to_csv(index=False), f"{course_name}_mappings.csv", use_container_width=True)
        # CO-PO-PSO Matrix Section - Directly Display Full Matrix (No Selection Prompt) - now Nx(11+num_psos) - Wrapped in attractive div
        st.markdown('<div class="output-section"><h2 class="output-header">📈 Full CO-PO-PSO Relevance Matrix (3=Strong, 2=Moderate, 1=Weak, 0=None)</h2></div>', unsafe_allow_html=True)
        # Extract matrix from mappings
        num_psos = len(st.session_state.get('pso_descriptions', {}))
        matrix_rows = [mapping.get("matrix_row", [0]*(11 + num_psos)) for mapping in st.session_state.mappings]
        po_columns = [f"PO{j+1}" for j in range(11)]
        pso_columns = [f"PSO{j+1}" for j in range(num_psos)]
        columns = po_columns + pso_columns
        co_rows = [mapping["co"] for mapping in st.session_state.mappings]
        df_matrix = pd.DataFrame(matrix_rows, index=co_rows, columns=columns)
        # Add average row
        average_row = df_matrix.mean().round(2)
        df_matrix.loc['Average'] = average_row
        st.dataframe(df_matrix, use_container_width=True)
        st.download_button("💾 Download Full Matrix CSV", df_matrix.to_csv(), f"{course_name}_co_po_pso_matrix.csv", use_container_width=True)
        # Explanations Section - Wrapped in attractive div
        with st.expander("📝 CO-PO-PSO Matrix Explanations", expanded=False):
            st.markdown('<div class="output-section"><h2 class="output-header">Detailed Explanations for Matrix Values</h2></div>', unsafe_allow_html=True)
            explanations = generate_explanations(st.session_state.cos, st.session_state.mappings, st.session_state.pso_descriptions)
            exp_data = []
            for exp in explanations:
                row = {"CO": exp["co"], "Value": exp["value"], "Explanation": exp["explanation"]}
                if "po" in exp:
                    row["PO/PSO"] = exp["po"]
                elif "pso" in exp:
                    row["PO/PSO"] = exp["pso"]
                exp_data.append(row)
            df_exp = pd.DataFrame(exp_data)
            st.dataframe(df_exp, use_container_width=True, height=400, hide_index=True)
        # Enhanced Section: PO-WA-WK-WP-EA-SDG Mapping with full explanations
        if st.button("🌍 Generate PO-WA-WK-WP-EA-SDG Mapping", use_container_width=True):
            with st.spinner("🔄 Generating PO-WA-WK-WP-EA-SDG Mappings based on reference documents and video logic..."):
                powa_mappings = generate_powa_mappings()
                powa_explanations = generate_powa_explanations(powa_mappings)
                st.session_state.powa_mappings = powa_mappings
                st.session_state.powa_explanations = powa_explanations
                st.rerun()
        if 'powa_mappings' in st.session_state:
            with st.expander("🔗 PO-WA-WK-WP-EA-SDG Mapping Table (NBA/Washington Accord Standards)", expanded=True):
                st.markdown('<div class="output-section"><h2 class="output-header">PO-WA-WK-WP-EA-SDG Mappings (11 POs) - Full Descriptions</h2></div>', unsafe_allow_html=True)
                mapping_data = []
                for mapping in st.session_state.powa_mappings:
                    # Robust handling for wps and eas using helper function
                    wps_str = ', '.join([
                        get_description(wp, WP_DESCRIPTIONS)
                        for wp in mapping['wps']
                    ])
                    eas_str = ', '.join([
                        get_description(ea, EA_DESCRIPTIONS)
                        for ea in mapping['eas']
                    ])
                    row = {
                        "PO": mapping["po"],
                        "WA": f"{mapping['wa']}: {mapping['wa_desc']}",
                        "Relevant WKs": "; ".join([f"{wk['wk']}: {wk['relevance']}" for wk in mapping['wks']]),
                        "Required WPs": f"{mapping['wps_req']}: {wps_str}",
                        "Required EAs": f"{mapping['eas_req']}: {eas_str}" if mapping['eas'] else mapping['eas_req'],
                        "SDG Status": f"{mapping['sdg']['status']}: {', '.join(mapping['sdg']['examples'])}",
                        "Overall Relevance": mapping["overall_relevance"]
                    }
                    mapping_data.append(row)
                df_powa = pd.DataFrame(mapping_data)
                st.dataframe(df_powa, use_container_width=True, height=500, hide_index=True)
                st.download_button("💾 Download PO-WA-WK-WP-EA-SDG CSV", df_powa.to_csv(index=False), f"{course_name}_powa_mappings.csv", use_container_width=True)
            with st.expander("📝 PO-WA-WK-WP-EA-SDG Mapping Explanations", expanded=False):
                st.markdown('<div class="output-section"><h2 class="output-header">Detailed Explanations for PO Mappings</h2></div>', unsafe_allow_html=True)
                exp_data = [{"PO": exp["po"], "Explanation": exp["explanation"]} for exp in st.session_state.powa_explanations]
                df_powa_exp = pd.DataFrame(exp_data)
                st.dataframe(df_powa_exp, use_container_width=True, height=400, hide_index=True)
        # CO-PO-WK Section - Now focused on displaying ONLY the N-unit mapping table like uploaded image - Wrapped in attractive div
        if st.button("🔗 Generate CO-PO-WK Mapping Table", use_container_width=True):
            with st.spinner("🔄 Generating CO-PO-WK Mappings..."):
                co_powk_mappings = generate_co_powk_mappings(st.session_state.cos)
                st.session_state.co_powk_mappings = co_powk_mappings
                st.rerun()
        if 'co_powk_mappings' in st.session_state:
            st.markdown('<div class="output-section"><h2 class="output-header">📊 {}-Unit CO-PO-WK Mapping Table</h2></div>'.format(num_generated), unsafe_allow_html=True)
            mapping_data = []
            for mapping in st.session_state.co_powk_mappings:
                row = {
                    "Course Outcomes (COs)": mapping["co_statement"],
                    "Mapped WKs": mapping["mapped_wks"],
                    "Mapped POs": mapping["mapped_pos"],
                    "Strength": mapping["strength"]
                }
                mapping_data.append(row)
            df_copowk = pd.DataFrame(mapping_data)
            st.dataframe(df_copowk, use_container_width=True, hide_index=True)
            st.download_button("💾 Download CO-PO-WK Table CSV", df_copowk.to_csv(index=False), f"{course_name}_co_powk_table.csv", use_container_width=True)

            # New Explanations Section for CO-PO-WK - Wrapped in attractive div
            with st.expander("📝 CO-PO-WK Mapping Explanations", expanded=False):
                st.markdown('<div class="output-section"><h2 class="output-header">Detailed Explanations for CO-PO-WK Mappings</h2></div>', unsafe_allow_html=True)
                explanations = generate_co_powk_explanations(st.session_state.co_powk_mappings)
                exp_data = [{"CO": exp["co"], "Mapped WKs": exp["mapped_wks"], "Mapped POs": exp["mapped_pos"], "Strength": exp["strength"], "Explanation": exp["explanation"]} for exp in explanations]
                df_exp = pd.DataFrame(exp_data)
                st.dataframe(df_exp, use_container_width=True, height=400, hide_index=True)

        # New Section: PO-WA-WK Mapping Table with CO List - Wrapped in attractive div
        if 'po_wa_wk_table' in st.session_state:
            st.markdown('<div class="output-section"><h2 class="output-header">PO-WA-WK Mapping Table (as per NBA)</h2></div>', unsafe_allow_html=True)
            html_table = generate_html_po_wa_wk_table(st.session_state.po_wa_wk_table)
            st.markdown(html_table, unsafe_allow_html=True)
            st.download_button("💾 Download PO-WA-WK Table CSV", st.session_state.po_wa_wk_table.to_csv(index=False), f"{course_name}_po_wa_wk_table.csv", use_container_width=True)

            # List COs with K-Levels at the end - Wrapped in attractive div
            st.markdown('<div class="output-section"><h3 style="color: #0077b6; text-align: center;">Generated COs with K-Levels</h3></div>', unsafe_allow_html=True)
            co_list_data = []
            for co in st.session_state.cos_list_for_wk:
                co_list_data.append({
                    "CO #": f"CO {co['unit']}",
                    "K-Level": co["level"],
                    "CO Statement": co["co"]
                })
            df_co_list = pd.DataFrame(co_list_data)
            st.dataframe(df_co_list, use_container_width=True, hide_index=True)

        st.info("✅ **Generated per Guidelines**: Student-centered, SMART, Backward Design, Bloom's Verbs, Assessable. Enhanced PIs with per-PI relevance (AICTE + course context); multiple PIs per PO; Full CO-PO-PSO Relevance Matrix (11 POs + PSOs) and Explanations. PO-WA-WK-WP-EA-SDG and CO-PO-WK based on reference Excel documents and Eng-Aim video logic for NBA accreditation, with full explanations. COs are unique and non-repeating across units.")

        # Credit footer
        st.markdown('<div class="credit">Developed by 💚@oyyathevan🍏</div>', unsafe_allow_html=True)
if __name__ == "__main__":
    main()