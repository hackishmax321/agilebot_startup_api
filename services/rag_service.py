import os
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.embedding_model = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, openai_api_key=self.openai_api_key)
        
        # Initialize ChromaDB
        self.persist_directory = "./chroma_db"
        self.vector_store = self._initialize_vector_store()
        
        # Load initial sample PDF
        self._load_initial_documents()
        
        # Create retrieval chain
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
        
        # RAG prompt template
        self.rag_prompt_template = ChatPromptTemplate.from_template("""
        Answer based on this context:
        {context}

Role: Scrum Master
Question: How does Agile methodology apply to our mobile projects?
Answer: Agile guides our mobile development through iterative 2-week sprints focused on rapid delivery, continuous feedback, and frequent releases.


Role: Scrum Master
Question: What is our typical sprint duration for app development?
Answer: Two weeks per sprint.

Role: Scrum Master
Question: How do we handle scope changes mid-sprint?
Answer: They are discouraged; critical changes go through a Sprint Interruption Review and are added to the next sprint if approved.

Role: Scrum Master
Question: What's our approach to MVP (Minimum Viable Product) development?
Answer: We use MoSCoW prioritization to deliver only the essential features for early validation.

Role: Scrum Master
Question: How do we conduct sprint planning for mobile projects?
Answer: We review the backlog, estimate using story points, and consider dependencies like APIs, UI readiness, and QA cycles.

Role: Scrum Master
Question: What's our definition of "Done" for a mobile app feature?
Answer: It must pass tests, be code-reviewed, merged to develop, included in a test build, and documented.

Role: Scrum Master
Question: What's our process for code reviews in mobile projects?
Answer: All pull requests require unit tests, linting, and at least one senior developer approval using a standard review checklist.

Role: Scrum Master
Question: How do we deal with blockers during day-to-day standups?
Answer: Blockers are logged in Jira and escalated to the Scrum Master immediately.

Role: Scrum Master
Question: What's our escalation critical path for major mobile bugs?
Answer: Critical bugs are tagged (P0/P1), triaged by Tech/QA Leads, and patched via a CI/CD hotfix path.



Role: Scrum Master
Question: Where can I find archived mobile project retrospectives?
Answer: In the Confluence “Retrospective Hub” under the Mobile Projects space.

Role: Scrum Master
Question: How do we document mobile app architecture?
Answer: Using markdown and diagrams stored in the GitLab system-design repo with version-controlled updates.

Role: Scrum Master
Question: What's our mobile app code branching model?
Answer: We use Git Flow: main for releases, develop for integration, and feature branches per task.

Role: Scrum Master
Question: How do we manage technical debt in mobile projects?
Answer: We log it in Jira with Tech Debt tags and address it during every third sprint via scheduled refactor tickets.

Role: Scrum Master
Question: What's our third-party SDK and library policy?
Answer: Only approved libraries listed in our internal SDK registry can be used, subject to periodic license and security review.

Role: Scrum Master
Question: How do we authenticate securely in mobile apps?
Answer: We use OAuth 2.0 with token rotation and device-level encryption, following OWASP Mobile Security Guidelines.

Role: Software Engineer
Question: What are the programming languages for iOS development?
Answer: Swift (primary) and Objective-C (legacy support).

Role: Software Engineer
Question: What are the frameworks used for Android development?
Answer: Kotlin (primary) with Java support and Android Jetpack libraries.

Role: Software Engineer
Question: Do we employ cross-platform tools like Flutter or React Native?
Answer: Yes, we use Flutter and React Native for hybrid mobile apps.

Role: Software Engineer
Question: How to improve code reviews in Agile?
Answer: In Agile, code reviews can be improved by setting clear coding standards, keeping reviews small and manageable, and using automated tools to handle routine checks. Reviews should focus on collaboration and knowledge sharing rather than just fault-finding, making them a learning opportunity for the whole team. Timeboxing the process and integrating it into the regular workflow ensures timely feedback without delaying delivery.

Role: Software Engineer
Question: Which IDE do we utilize for mobile application development?
Answer: Xcode for iOS, Android Studio for Android, and VS Code for cross-platform.

Role: Software Engineer
Question: What is our branch strategy for mobile application code?
Answer: Git Flow: main (release), develop (integration), feature/*, hotfix/*.

Role: Software Engineer
Question: How do we handle API integrations in mobile applications?
Answer: Using REST/GraphQL APIs via Retrofit (Android) and Alamofire (iOS).

Role: Software Engineer
Question: What tools do we utilize for backend interaction?
Answer: Custom SDKs, Axios, Retrofit, and GraphQL clients depending on the stack.

Role: Software Engineer
Question: Do we employ CI/CD pipelines for mobile applications?
Answer: Yes, via GitHub Actions and Fastlane for automated builds and deployment.

Role: Software Engineer
Question: How do we handle app secrets and env variables?
Answer: Stored in encrypted .env files and managed securely through CI key vaults.

Role: Software Engineer
Question: What is our strategy for caching in mobile applications?
Answer: Local storage using SharedPreferences (Android), Core Data (iOS), or Hive.



Role: Software Engineer
Question: What is our frontend framework (React, Vue, Next.js ?
Answer: React and Next.js for web interfaces.



Role: Software Engineer
Question: Do we use a CMS (WordPress, Contentful) ?
Answer: Yes, we use Contentful for headless CMS integration.

Role: Software Engineer
Question: What is our hosting solution (AWS, Vercel, Netlify) ?
Answer: Vercel for frontend hosting and AWS for backend services.

Role: Software Engineer
Question: How do we web-optimize images and media ?
Answer: Using Cloudinary and Next.js <Image> components for responsive optimisation.

Role: Software Engineer
Question: What is our strategy for lazy loading ?
Answer: Dynamic imports and scroll-triggered rendering using Intersection Observer.

Role: Software Engineer
Question: How do we handle offline functionality and syncing data ?
Answer: Local databases (Room, Core Data) with sync queues upon reconnect.

Role: Software Engineer
Question: What is our policy for encrypting sensitive data ?
Answer: AES encryption with secure key management and platform-specific keychains.

Role: Software Engineer
Question: How do we protect against reverse engineering of our products ?
Answer: Code obfuscation, anti-debugging measures, and integrity checks.

Role: Software Engineer
Question: What is our process for receiving security vulnerability reports ?
Answer: Via a public disclosure form; triaged by AppSec and tracked in Jira.


Role: Software Engineer
Question: How do we track and reduce crash rates ?
Answer: We use Firebase Crashlytics and Sentry for real-time crash monitoring, link issues to Jira for triage, and resolve them in the next sprint with enforced pre-release QA to prevent recurrence.





Role: Business Analyst
Question: What are the User stories and acceptance criteria for the redesign site ?
Answer: User stories follow the format “As a [user], I want [goal] so that [benefit]” and acceptance criteria are written in Gherkin-style Given-When-Then format; both are maintained in Jira and linked to EPICs in the redesign project backlog.

Role: Business Analyst
Question: Who are the key stakeholders in the redesign project ?
Answer: Key stakeholders include the Product Owner, UX Lead, Marketing Director, Engineering Manager, and external brand consultants, all of whom participate in sprint reviews and prioritisation ceremonies.



Role: Business Analyst
Question: How do we define success for the new site ?
Answer: Success is defined by OKRs including bounce rate reduction, improved conversion rates, accessibility compliance, and sprint velocity consistency; these are reviewed during release retrospectives.

Role: Business Analyst
Question: What are teracebility materix for all the projects 
Answer: 
Traceability matrices map requirements to user stories, test cases, and business objectives; they’re auto-generated in Confluence or Excel via Jira integrations and updated post each sprint cycle.

Role: Business Analyst
Question: What are teracebility materix for all the projects 
Answer: We maintain forward and backward traceability from business requirements to test cases and deployment. Tools like Jira-Excel plugins or Confluence templates are used. Some teams automate this using Xray or TestRail integrations.

Role: Business Analyst
Question: How do we handle multilingualities ?
Answer: We use i18n libraries (e.g., i18next, Android/iOS locale APIs) with JSON/PO translation files. Content is extracted and translated using tools like Lokalise or Crowdin. QA includes linguistic validation and locale-based regression testing.

Role: Business Analyst
Question: What is our competitive analysis for this product release ?
Answer: We benchmark against 3–5 competitors using SWOT and feature parity matrices. Market trends and user sentiment (via reviews/social listening) are also analyzed. This feeds into backlog prioritization and UX goals.

Role: Business Analyst
Question: How does this product align with our existing portfolio ?
Answer: Multilingual support is handled via locale files and i18n libraries, and content is managed using translation-ready CMS platforms; stories include language test cases as part of Definition of Done. We use i18n libraries (e.g., i18next, Android/iOS locale APIs) with JSON/PO translation files. Content is extracted and translated using tools like Lokalise or Crowdin. QA includes linguistic validation and locale-based regression testing.



Role: Business Analyst
Question: How do we prioritise and definning requirements by the Invest Method in ongoing pojects ?
Answer: We write stories that are Independent, Negotiable, Valuable, Estimable, Small, and Testable; stories failing INVEST are split or refined during backlog grooming with Product Owner oversight.                                          Stories are split or rewritten to ensure they are Independent, Negotiable, Valuable, Estimable, Small, and Testable. Planning poker and grooming workshops help reinforce INVEST compliance.



Role: Business Analyst
Question: How do we prioritise and definning requirements by the Moscow Method in ongoing pojects ?
Answer: We categorize features as Must-have, Should-have, Could-have, or Won’t-have based on value, risk, and delivery feasibility. Used in MVP definition and release planning.Requirements are classified into Must-have, Should-have, Could-have, and Won’t-have based on business value, effort estimates, and sprint capacity, and are revisited during sprint planning and retrospectives.



Role: Business Analyst
Question: How do we capture and act on user feedback ?
Answer: User feedback is collected through in-app prompts, surveys, and support channels, tagged in Jira, triaged weekly, and converted into feature requests or backlog items with linked customer stories. Via in-app prompts, NPS surveys, Zendesk tickets, and product feedback boards (like Canny). Insights are reviewed biweekly, tagged in Jira, and converted into backlog items or research tasks.



Role: Business Analyst
Question: What's our workflow for user feature requests ?
Answer: Requests enter the triage board, are validated against personas, prioritized using value/effort grids, and converted into EPICs or spikes. Low-value requests may be marked for research or rejected with rationale. Feature requests enter the intake board, are validated against user personas, prioritized in the triage queue, scoped into EPICs, and refined into actionable stories during grooming with the team.

Role: Business Analyst
Question: How does CATWOE impact for ongoing projects 

Answer: CATWOE helps us frame business problems by identifying Customers, Actors, Transformation, Worldview, Owners, and Environmental constraints, guiding backlog refinement and stakeholder alignment. CATWOE helps clarify business needs, stakeholder expectations, and system boundaries. It’s used during initial requirement workshops and project scope reviews for stakeholder alignment.



Role: Business Analyst
Question: Who develops technical documentation for the product ?
Answer: Technical documentation is collaboratively developed by the Business Analyst, Technical Writer, and Developers post-sprint; all docs are stored in the Confluence space under the product section, git repos with stakeholder review pre-release.

Role: Business Analyst
Question: What's our process for feature prioritization ?
Answer: Features are prioritised using weighted scoring models, MoSCoW classification, and stakeholder input; prioritisation occurs during refinement sessions and is visualised in the product roadmap. MoSCoW, WSJF (Weighted Shortest Job First), and Kano models are commonly used. Stakeholder value scoring and dev capacity help finalise sprint scopes.

Role: Business Analyst
Question: What are the use cases for all the existing projects ?
Answer: Use cases cover core workflows, edge scenarios, and exceptions. They are written in UML or user narrative form and stored in the solution design repository. Documented in a standardised format in Confluence and traced to EPICs and stories in Jira, updated quarterly during architecture and requirements alignment reviews.

Role: Business Analyst
Question: Explain the SWOT Analysis for all the projects ?
Answer: SWOT analysis is done at the initiative level to assess Strengths, Weaknesses, Opportunities, and Threats and is reviewed in portfolio planning to mitigate risks and identify innovation areas. Each project undergoes SWOT reviews pre-kickoff and at major milestones. Strengths may include reusable codebases; threats often involve tech debt or third-party dependencies.

Role: Business Analyst
Question: What are the requirements gathering tools employed for each and every project ?
Answer: We use tools like Jira for story capture, Miro for workshops, Confluence for documentation, and Figma for UI requirement mapping during discovery and sprint zero phases.

Role: Business Analyst
Question: What are user stories for mobile app ?
Answer: Mobile app stories are written to reflect platform-specific behaviors (e.g., touch interactions, offline support) and include device compatibility and performance criteria in acceptance tests.



Role: Business Analyst
Question: Show the EPIC Description of ongoing projects ?
Answer: Each EPIC includes a business objective, linked user stories, target releases, and measurable outcomes, and is tracked in Jira under the ongoing project roadmap view.

Role: Business Analyst
Question: Show all the data modelling techniques of the ongoing projects ?
Answer: We use ER diagrams, JSON schema definitions, and NoSQL models based on product architecture, documented in the Confluence Data Design section and versioned via Git.

Role: Business Analyst
Question: Define PESTLE Analysis of the projects ? 
Answer: PESTLE (Political, Economic, Social, Technological, Legal, Environmental) analysis is conducted annually to guide strategic decisions and is presented to stakeholders in PI planning sessions.



Role: Business Analyst
Question: Expain the point of estimation of all the projects ?
Answer: Story point estimation is done using planning poker or t-shirt sizing, guided by velocity tracking and historical data, with adjustments made per team capacity every sprint. Historical velocity and burndown charts guide adjustments. Risk buffers are built into high-uncertainty features.

Role: Business Analyst
Question: What Root Cause Analysis in exsisting projects ?
Answer: RCA is performed using 5 Whys or Fishbone diagrams during post-mortems, and findings are documented in retrospective actions with linked mitigation tasks in Jira.


Role: Business Analyst
Question: Show the Gap Analysis of all the projects ?
Answer: Gap analysis identifies discrepancies between current features and business goals, is tracked in the Confluence roadmap, and influences quarterly OKR and backlog planning.

Role: Business Analyst
Question: Explain the mind mapping for all the project ?
Answer: Mind maps are used during discovery sessions to explore user flows, system modules, and dependency paths and are stored in shared Miro boards linked to each project space.

Role: Business Analyst
Question: Explain the Functional Requirements of the ongoing projects ?
Answer: Defined as system actions triggered by user input, including login, form submission, and data updates. Linked directly to user stories and acceptance tests, and specify system behaviours such as use case flows, and business rules; they are derived from user stories and reviewed during sprint planning and refinement.

Role: Business Analyst
Question: Explain the Non- Functional Requirements of the ongoing projects ?
Answer: Non-functional requirements cover performance, scalability, security, and usability; these are embedded as technical stories or acceptance criteria within user-facing features. Often documented as technical stories or engineering constraints.

Role: Business Analyst
Question: What are the User Acceptance Test Cases identified before the implementation ?
Answer: Defined by stakeholders based on story acceptance criteria. Stored in QA test suites and Confluence. UAT sign-off is required before production release. UAT test cases are derived from user stories and acceptance criteria, reviewed by stakeholders, and stored in the QA test suite; sign-off is required before production release.

Role: QA Engineer
Question: What is our testing approach to our mobile app ?
Answer: We follow a hybrid approach, using both manual and automated testing to ensure full coverage. Automated tests handle regressions and repetitive tasks, while manual testing focuses on usability, visual checks, and exploratory testing.


Role: QA Engineer
Question: Do we manually test automatically test or both ?
Answer: We do both. Manual testing is used for new features, UX, and edge cases. Automated testing handles regression, smoke tests, and critical path validation for faster release cycles.

Role: QA Engineer
Question: What tools do we use to test UI (Appium, Espresso) ?
Answer: We use Appium for cross-platform UI automation, Espresso for Android UI testing, and XCUITest for iOS. We also leverage BrowserStack for testing on real devices.


Role: QA Engineer
Question: How do we regress test before we release ?
Answer: We run automated regression suites through our CI/CD pipeline and conduct manual regression for critical workflows. This ensures stability and detects issues introduced by new code.


Role: QA Engineer
Question: What is our crash reporting and monitoring process ?
Answer: We use Firebase Crashlytics or Sentry to monitor app crashes in real time. Alerts are triggered for high-priority issues, and logs help developers quickly identify and fix the root causes.


Role: QA Engineer
Question: What is our website test checklist ?
Answer: We check for UI consistency, functionality, form validations, broken links, accessibility, SEO tags, load speed, and responsiveness across devices and screen sizes.


Role: QA Engineer
Question: How do we cross-browser test ?
Answer: We use tools like BrowserStack or LambdaTest to test across all major browsers (Chrome, Firefox, Safari, Edge) and ensure compatibility on various OS versions.


Role: QA Engineer
Question: What is our mobile responsiveness testing process ?
Answer: We test using Chrome DevTools’ device emulator and real devices to validate layouts, touch functionality, and UI scaling across screen sizes and orientations.


Role: QA Engineer
Question: How do we do usability testing ?
Answer: We conduct internal usability reviews and user testing sessions. Feedback is collected via surveys or interviews, focusing on ease of use, clarity, and task completion flow.

Role: QA Engineer
Question: What is our smoke testing process before go-live ?
Answer: Before go-live, we run a minimal set of high-priority tests (smoke suite) to confirm that core app functions work, such as login, navigation, API responses, and data rendering.


Role: QA Engineer
Question: What is our beta testing plan ?
Answer: We release the app to a closed beta group using TestFlight (iOS) or Internal Testing (Google Play). Selected users test real-world scenarios and report feedback before the public launch.


Role: QA Engineer
Question: Who owns customer feedback during beta ?
Answer: The Product Manager owns beta feedback, coordinating with QA and developers to triage, prioritize, and resolve issues. QA verifies fixes before updates are pushed.


Role: QA Engineer
Question: What is our process for fixing early bugs/issues ?
Answer: Bugs are logged in our tracking tool (e.g., Jira), triaged by severity, and addressed by the dev team. Fixes undergo retesting by QA and are included in the next beta build.


Role: QA Engineer
Question: How do we test app performance (speed battery life)?
Answer: We use tools like Android Profiler, Xcode Instruments, and Firebase Performance Monitoring to test app launch time, UI response, memory usage, network calls, and battery consumption.

Role: QA Engineer
Question: What's our device and OS version support policy?
Answer: We support the latest two major OS versions (Android and iOS) and devices with a user base share above a defined threshold (e.g., 95%+ market coverage). Old OS support is dropped gradually with clear communication.

Role: Project Manager
Question: What is the website redesign timeline?
Answer: The redesign timeline is typically broken into phases: planning (2 weeks), design (3–4 weeks), development (4–6 weeks), QA/testing (2 weeks), and final launch preparation (1 week). The full project spans roughly 10–14 weeks, depending on scope and feedback cycles.


Role: Project Manager
Question: How much is our redesign budget?
Answer: The total redesign budget is £15,000, which includes costs for design resources, development, QA, content updates, testing tools, and contingency reserves for unexpected scope changes.

Role: Project Manager
Question: Who are the most critical stakeholders in our redesign initiative?
Answer: Key stakeholders include the Product Owner, Marketing Lead, CTO, and Customer Support Manager. Each plays a role in shaping the user experience, ensuring technical feasibility, and aligning with business goals.


Role: Project Manager
Question: What is our risk mitigation strategy for delays in going live?
Answer: Key stakeholders include the Product Owner, Marketing Lead, CTO, and Customer Support Manager. Each plays a role in shaping the user experience, ensuring technical feasibility, and aligning with business goals.


Role: Project Manager
Question: How do we process last-minute product change requests?
Answer: Late-stage changes must be submitted via a formal change request form, reviewed by the Project Manager and leads, and prioritised based on impact, effort, and go-live deadlines. Only high-impact fixes are approved close to launch.

Role: Project Manager
Question: What is the formal launch date and time of day?
Answer: The scheduled go-live is the 30th of each month at 9:00 AM GMT, when traffic and support staff availability are optimal for monitoring and handling initial feedback.


Role: Project Manager
Question: Who throws the "go live" switch?
Answer: The Lead Developer or DevOps Engineer is responsible for the deployment, under the approval of the Project Manager and after final QA sign-off.


Role: Project Manager
Question: What is our backup plan if the site crashes?
Answer: We have a rollback strategy to revert to the stable previous version, plus full backups taken before go-live. Our hosting provider and internal DevOps team are on standby for rapid issue resolution.


Role: Project Manager
Question: How do we handle spikes in customer support?
Answer: Extra support staff are scheduled during launch week. We prepare templated responses for common issues and escalate technical queries directly to Tier 2 support or engineering as needed.

Role: Project Manager
Question: What is our real-time issue escalation process?
Answer: All critical issues are logged in the incident management system (e.g., Jira or PagerDuty). The QA Lead or Support Manager flags the issue, and the DevOps and product teams are looped in within minutes for triage and resolution.


Role: Project Manager
Question: How are launch delays announced within the company?
Answer: Delays are immediately communicated through Slack and email with a clear reason, revised timeline, and next steps. A cross-functional update meeting is held if the delay exceeds one business day.
                                                                    

Role: Project Manager
Question: Who is our launch emergency contact?
Answer: The Project Manager is the first point of contact. A launch war room or emergency comms channel is created in Slack, where leads from QA, DevOps, and Product are all active.

Role: Project Manager
Question: What's our process for gathering launch feedback?
Answer: We collect feedback via post-launch surveys, stakeholder interviews, support logs, and analytics data. The findings are reviewed in a retrospective session to identify wins and improvement areas.

Role: Project Manager
Question: How do we document lessons learned?
Answer: Post-launch, we conduct a project retrospective, document key learnings in a shared Confluence or Notion page, and include recommendations for future rollouts. Action items are assigned for process improvements.

Role: Project Manager
Question: What's our product vision for the long term?
Answer: Our long-term vision is to create a scalable, accessible, and conversion-optimized website that supports continuous feature improvements, enhanced user personalization, and seamless cross-platform experiences aligned with business growth goals.

Question: {input}
If you don't know, say "I don't have information about that."
""")
        
        # Fallback prompt template for when context doesn't contain relevant information
        self.fallback_prompt_template = ChatPromptTemplate.from_template("""
        You are a helpful assistant. Answer the following question based on your general knowledge:

        Question: {input}
        
        Please provide a helpful and accurate response.
        """)
        
        # Create chains
        self.rag_chain = create_stuff_documents_chain(self.llm, self.rag_prompt_template)
        self.retrieval_chain = create_retrieval_chain(self.retriever, self.rag_chain)
        self.fallback_chain = self.fallback_prompt_template | self.llm

    def _initialize_vector_store(self):
        """Initialize or load existing vector store"""
        return Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_model
        )

    def _load_initial_documents(self):
        """Load sample.pdf and any other initial documents"""
        sample_path = os.path.join('uploads', 'sample.pdf')
        if os.path.exists(sample_path):
            try:
                self.load_document_from_file(sample_path)
                logger.info("Successfully loaded initial sample PDF")
            except Exception as e:
                logger.error(f"Failed to load initial sample PDF: {str(e)}")

    def load_document_from_file(self, file_path):
        """Process and index a PDF file"""
        try:
            logger.info(f"Processing file: {file_path}")
            
            # Load and split PDF
            loader = PyPDFLoader(file_path)
            pages = loader.load_and_split()
            
            # Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", " ", ""]
            )
            chunks = text_splitter.split_documents(pages)
            
            if not chunks:
                logger.warning("No content extracted from PDF")
                return False
            
            # Add to vector store
            self.vector_store.add_documents(chunks)
            self.vector_store.persist()
            
            logger.info(f"Added {len(chunks)} chunks from {os.path.basename(file_path)}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            return False

    def query(self, question):
        """Query the knowledge base with fallback to ChatGPT"""
        try:
            # First try to get relevant documents from the vector store
            relevant_docs = self.retriever.get_relevant_documents(question)
            
            # If no relevant documents found or documents don't contain useful information,
            # use the fallback to ChatGPT
            if not relevant_docs or self._should_use_fallback(relevant_docs, question):
                logger.info(f"No relevant context found for question: {question}. Using fallback to ChatGPT.")
                result = self.fallback_chain.invoke({"input": question})
                return result.content
            
            # If relevant documents found, use RAG chain
            result = self.retrieval_chain.invoke({"input": question})
            return result["answer"]
            
        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
            return "Sorry, I encountered an error processing your question."

    def _should_use_fallback(self, documents, question):
        """
        Determine whether to use fallback based on document relevance.
        This can be enhanced with more sophisticated relevance scoring.
        """
        # Simple check: if the retrieved documents are very short or don't seem relevant
        # based on content length and similarity to question
        total_content_length = sum(len(doc.page_content) for doc in documents)
        
        # If the total content is very short, likely not relevant
        if total_content_length < 100:
            return True
        
        # You could add more sophisticated relevance checks here, such as:
        # - Semantic similarity scoring
        # - Keyword matching
        # - Confidence threshold from the retriever
        
        return False

    def has_documents(self):
        """Check if vector store contains documents"""
        return self.vector_store._collection.count() > 0

# Singleton instance
rag_service = RAGService()