import { Job, DetailJob, JobQueryParams } from "../lib/types/job";
import { PaginatedResponse } from "../lib/types/pagination";

const generateMockDetailJobs = (count: number): DetailJob[] => {
  const mockJobsBase = [
    {
      id: "1",
      title: "Senior Frontend Developer",
      originalUrl: "https://example.com/jobs/1",
      company: {
        name: "Google",
        logo: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/1200px-Google_%22G%22_Logo.svg.png",
        address: "Mountain View, CA",
        description: "### About Google\n\nGoogle is a global technology leader focused on improving the ways people connect with information. We aspire to build products and provide services that improve the lives of billions of people around the world. Our mission is to organize the world's information and make it universally accessible and useful.\n\n### Our Culture\n\nAt Google, we don't just accept difference—we celebrate it, support it, and thrive on it for the benefit of our employees, our products, and our community. The cool thing about working at Google is that we're a community of different perspectives, identities, races, orientations, backgrounds, and beliefs.\n\n### Our Benefits\n\n* Competitive compensation\n* Generous time off\n* Healthcare coverage\n* Learning and development opportunities"
      },
      location: "Remote / San Francisco",
      datePosted: new Date("2025-04-10"),
      skills: ["React", "TypeScript", "CSS", "Redux", "GraphQL", "Jest", "Webpack", "NextJS", "Storybook"],
      jobDescription: "We are looking for an experienced Frontend Developer to join our team and help build innovative, high-performance user interfaces for our products that are used by billions of people worldwide.\n\n### What You'll Do\n\n* Design and develop new user-facing features using React.js and TypeScript\n* Build reusable components and libraries for future use\n* Translate designs and wireframes into high-quality code\n* Optimize components for maximum performance across a vast array of web-capable devices and browsers\n* Collaborate with back-end developers and designers to improve usability\n* Help maintain code quality, organization, and automation\n\n### Project Highlights\n\nYou'll be working on projects that impact millions of users daily. Our current focus is on:\n\n1. Improving the performance of our main application by 50%\n2. Implementing a new design system using the latest front-end technologies\n3. Building accessibility features to make our products more inclusive",
      jobRequirements: "### Required Qualifications\n\n* Bachelor's degree in Computer Science, related technical field, or equivalent practical experience\n* 5+ years of experience with modern JavaScript frameworks (React preferred)\n* Strong proficiency in TypeScript and modern JavaScript (ES6+)\n* In-depth knowledge of CSS, HTML, and frontend best practices\n* Experience with responsive and adaptive design\n* Understanding of cross-browser compatibility issues and ways to work around them\n* Familiarity with RESTful APIs and GraphQL\n* Experience with state management libraries (Redux, MobX, or similar)\n* Strong understanding of performance optimization and security issues\n\n### Preferred Qualifications\n\n* Experience with server-side rendering and static site generation\n* Knowledge of modern authorization mechanisms, such as JWT\n* Experience with testing frameworks such as Jest, React Testing Library\n* Familiarity with continuous integration and deployment (CI/CD)\n* Contributions to open source projects\n* Experience mentoring junior developers",
      type: "Full-time",
      level: "Senior",
      salary: "$120K - $150K",
      benefit: "### Benefits & Perks\n\n* **Health & Wellness**\n  * Comprehensive health insurance\n  * On-site fitness centers\n  * Mental health resources\n  * Wellness programs and incentives\n\n* **Workspace**\n  * Modern, collaborative workspace\n  * Latest hardware and software\n  * Remote work flexibility\n  * Employee resource groups\n\n* **Professional Development**\n  * Learning & development budget\n  * Internal hackathons and innovation contests\n  * Mentorship opportunities\n  * Conference attendance\n\n* **Financial Benefits**\n  * Competitive compensation\n  * 401(k) matching\n  * Stock purchase plan\n  * Performance bonuses",
      isExpired: false,
      isFavorite: false,
    },
    {
      id: "2",
      title: "UX/UI Designer",
      originalUrl: "https://example.com/jobs/2",
      company: {
        name: "Microsoft",
        logo: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Microsoft_logo.svg/1200px-Microsoft_logo.svg.png",
        address: "Redmond, WA",
        description: "### Microsoft: Where Innovation Meets Purpose\n\nAt Microsoft, our mission is to empower every person and every organization on the planet to achieve more. We're dedicated to creating technology that transforms the way people work, play, and communicate.\n\n### Our Vision\n\nMicrosoft is a leading global provider of software, services, devices and solutions that help people and businesses realize their full potential. Our diverse workforce is committed to making a lasting positive impact on our customers, partners, and communities around the world.\n\n### Core Values\n\n* Innovation\n* Diversity and inclusion\n* Corporate social responsibility\n* Trustworthy computing"
      },
      location: "Hybrid / Seattle",
      datePosted: new Date("2025-04-20"),
      skills: ["Figma", "User Research", "Prototyping", "Design Systems", "Wireframing", "UI Animation", "Accessibility", "Usability Testing"],
      jobDescription: "As a UX/UI Designer at Microsoft, you'll be responsible for creating intuitive, accessible, and delightful user experiences for our flagship products used by millions worldwide.\n\n### Key Responsibilities\n\n* Create wireframes, user flows, prototypes and high-fidelity mockups for various digital products\n* Collaborate with product managers, engineers, and researchers to define user experiences\n* Design and test user interface elements, navigation components, and visual interactions\n* Develop and maintain design systems for consistent user experiences\n* Conduct user research and usability testing to validate designs\n* Present design concepts and research findings to stakeholders\n\n### Recent Projects\n\n### Windows 12 Interface Redesign\nOur team led the redesign of core system interfaces, focusing on:\n\n* Simplified navigation\n* Enhanced accessibility features\n* Personalized user experiences\n* Seamless integration across devices\n\n### Microsoft 365 Experience Evolution\nWe reimagined collaboration tools to create a more unified experience:\n\n* Collaborative document editing\n* Real-time communication integration\n* AI-assisted content creation\n* Cross-platform consistency",
      jobRequirements: "### Qualifications\n\n* Bachelor's degree in Design, Human-Computer Interaction, or related field\n* 3+ years of experience designing user interfaces for web and mobile applications\n* Strong portfolio demonstrating UI/UX design process and outcomes\n* Proficiency with industry-standard design tools (Figma, Adobe XD, Sketch)\n* Experience with design systems and component libraries\n* Understanding of accessibility standards (WCAG) and inclusive design principles\n* Strong communication skills and ability to articulate design decisions\n\n### Desired Skills\n\n* Experience conducting user research and usability testing\n* Knowledge of front-end development technologies (HTML, CSS, JavaScript)\n* Understanding of motion design and animation principles\n* Experience with data visualization design\n* Background in enterprise software or complex applications\n* Knowledge of AR/VR interaction design",
      type: "Contract",
      level: "Mid-level",
      salary: "$90K - $110K",
      benefit: "### Benefits & Perks\n\n* **Health & Wellness**\n  * Comprehensive health insurance\n  * On-site fitness centers\n  * Mental health resources\n  * Wellness programs and incentives\n\n* **Workspace**\n  * Modern, collaborative workspace\n  * Latest hardware and software\n  * Remote work flexibility\n  * Employee resource groups\n\n* **Professional Development**\n  * Learning & development budget\n  * Internal hackathons and innovation contests\n  * Mentorship opportunities\n  * Conference attendance\n\n* **Financial Benefits**\n  * Competitive compensation\n  * 401(k) matching\n  * Stock purchase plan\n  * Performance bonuses",
      isExpired: false,
      isFavorite: false,
    },
    {
      id: "3",
      title: "Backend Engineer",
      originalUrl: "https://example.com/jobs/3",
      company: {
        name: "Startup XYZ",
        logo: "https://cdn.worldvectorlogo.com/logos/grab-2.svg",
        address: "New York, NY",
        description: "### About Startup XYZ\n\nStartup XYZ is a rapidly growing tech startup focused on revolutionizing the fintech industry through innovative solutions powered by artificial intelligence and machine learning. Founded in 2023, we've already secured $20M in Series A funding and are expanding our engineering team to meet growing demand.\n\n### Our Mission\n\nWe're building the next generation of financial tools that make complex financial decisions simple for everyday people. Our platform analyzes spending patterns, investment opportunities, and market trends to provide personalized recommendations.\n\n### Company Culture\n\nAt Startup XYZ, we believe in:\n\n* Rapid iteration and continuous learning\n* Transparent communication at all levels\n* Work-life balance and flexible scheduling\n* Diversity of thought and inclusive practices"
      },
      location: "On-site / New York",
      datePosted: new Date("2025-04-25"),
      skills: ["Node.js", "MongoDB", "Express", "AWS", "Kubernetes", "Docker", "Microservices", "Redis", "gRPC"],
      jobDescription: "### Overview\nJoin our engineering team at Startup XYZ and help us scale our backend infrastructure to support our rapidly growing user base. You'll be designing and implementing highly scalable, reliable, and maintainable backend services that power our financial analysis platform.\n\n### Role Description\nAs a Backend Engineer, you'll be part of a cross-functional team responsible for developing and maintaining our microservices architecture. You'll work closely with frontend engineers, data scientists, and product managers to build robust APIs that deliver personalized financial insights to our users.\n\n### Your Impact\nYour work will directly contribute to enabling our platform to:\n\n* Process financial transactions in real-time\n* Analyze large volumes of financial data efficiently\n* Generate personalized investment recommendations\n* Maintain the highest standards of data security and privacy\n\n### Technical Environment\n\nOur stack includes:\n\n```\nNode.js | Express | MongoDB | Redis | AWS Lambda | Docker | Kubernetes | gRPC\n```\n\nWe follow a microservices architecture with event-driven design patterns and implement CI/CD practices for rapid, reliable deployments.",
      jobRequirements: "### Required Skills & Experience\n\n* **Technical Background**\n  * 3+ years of professional experience building backend services\n  * Strong proficiency with Node.js and Express framework\n  * Experience with NoSQL databases, particularly MongoDB\n  * Familiarity with containerization using Docker and orchestration with Kubernetes\n  * Understanding of RESTful API design principles\n  * Experience with cloud services, preferably AWS\n\n* **Engineering Practices**\n  * Solid understanding of microservices architecture\n  * Experience with test-driven development\n  * Knowledge of CI/CD pipelines\n  * Understanding of observability (logging, monitoring, alerting)\n\n### Bonus Points For\n\n* Experience with message brokers (Kafka, RabbitMQ)\n* Knowledge of GraphQL\n* Understanding of financial technology domain\n* Contributions to open-source projects\n* Experience with gRPC and protocol buffers\n\n### Code Challenge Example\n\n```javascript\n// We might ask you to optimize something like this:\nconst processTransactions = async (userId, date) => {\n  const transactions = await Transaction.find({ userId, date });\n  // ...\n}\n```",
      type: "Part-time",
      level: "Junior",
      salary: "$80K - $100K",
      benefit: "### Startup Benefits\n\n### Compensation & Equity\n* Competitive salary\n* Equity package with early-stage company\n* Performance-based bonuses\n* Flexible spending account\n\n### Health & Wellness\n* Health insurance with 100% premium coverage\n* Dental and vision plans\n* Mental health resources\n* Gym membership reimbursement\n\n### Work Environment\n* Flexible work arrangements (part-time, hybrid)\n* Modern office in downtown NYC\n* Home office stipend\n* Latest equipment of your choice\n\n### Growth & Development\n* Learning budget for courses and certifications\n* Weekly tech talks and knowledge sharing\n* Mentorship program\n* Conference attendance opportunities\n\n### Additional Perks\n* Unlimited PTO policy\n* Catered lunches three times a week\n* Monthly team building events\n* Commuter benefits",
      isExpired: false,
      isFavorite: false,
    }
  ];

  const allJobs: DetailJob[] = [...mockJobsBase];
  
  // Start from ID 4 (we already have 1-3)
  for (let i = 4; i <= count; i++) {
    const baseJob = { ...mockJobsBase[Math.floor(Math.random() * mockJobsBase.length)] };
    
    // Generate random job level
    const jobLevels = ["Intern", "Entry-level", "Junior", "Mid-level", "Senior", "Lead", "Manager"];
    const randomLevel = jobLevels[Math.floor(Math.random() * jobLevels.length)];
    
    // Generate random job type
    const jobTypes = ["Full-time", "Part-time", "Contract", "Internship", "Temporary"];
    const randomType = jobTypes[Math.floor(Math.random() * jobTypes.length)];
    
    const newJob: DetailJob = {
      ...baseJob,
      id: i.toString(),
      originalUrl: baseJob.originalUrl + `?ref=${i}`,
      skills: baseJob.skills?.slice(0, Math.floor(Math.random() * baseJob.skills.length) + 1) || [],
      title: baseJob.title + " " + (i % 2 === 0 ? "(Senior)" : "(Junior)"),
      company: {
        ...baseJob.company,
        name: baseJob.company?.name + " " + (i % 3 === 0 ? "Inc." : "LLC"),
      },
      location: i % 3 === 0 ? "Remote / Global" : i % 2 === 0 ? "Hybrid / Chicago" : "On-site / Boston",
      type: randomType,
      level: randomLevel,
      datePosted: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000),
    };
    
    allJobs.push(newJob);
  }
  
  return allJobs;
};

const generateMockJobs = (mockDetailJobs: DetailJob[]): Job[] => {
  return mockDetailJobs.map((job) => ({
    id: job.id,
    title: job.title,
    companyName: job.company.name,
    companyLogo: job.company.logo,
    originalUrl: job.originalUrl,
    location: job.location,
    datePosted: job.datePosted,
    skills: job.skills,
    type: job.type,
    level: job.level,
    salary: job.salary,
    isExpired: job.isExpired,
    isFavorite: job.isFavorite,
  }));
};

const mockDetailJobs: DetailJob[] = generateMockDetailJobs(30);
const mockJobs: Job[] = generateMockJobs(mockDetailJobs);

const mockPromptSuggestions = [
  "Which jobs match best with my programming skills in Python and data analysis?",
  "How can I find jobs that utilize my communication and leadership abilities?", 
  "What careers would suit someone with strong analytical thinking and problem-solving skills?", 
  "Which industries value creative thinking and design skills the most?",
  "How do I identify jobs that match my technical and soft skills profile?",
  "What jobs are available for someone with project management experience but no certification?",
  "How can I leverage my foreign language skills in my job search?",
  "Which roles would best fit my background in research and statistical analysis?",
  "What career paths align with my skills in content creation and social media management?",
  "How do I find jobs that value my self-taught programming abilities without a CS degree?"
];

// Mock favorites storage
let favoriteJobIds: string[] = [];

const jobLevelOptions = [
  { value: "Intern", label: "Intern" },
  { value: "Entry-level", label: "Entry Level" },
  { value: "Junior", label: "Junior" },
  { value: "Mid-level", label: "Mid-level" },
  { value: "Senior", label: "Senior" },
  { value: "Lead", label: "Lead" },
  { value: "Manager", label: "Manager" },
  { value: "Director", label: "Director" },
  { value: "VP", label: "VP" },
  { value: "Executive", label: "Executive" },
  { value: "Principal", label: "Principal" },
  { value: "Chief", label: "Chief" },
  { value: "Head", label: "Head" },
];

const jobTitleOptions = [
  { value: "Frontend Developer", label: "Frontend Developer" },
  { value: "UX/UI Designer", label: "UX/UI Designer" },
  { value: "Backend Engineer", label: "Backend Engineer" },
  { value: "Data Scientist", label: "Data Scientist" },
  { value: "Product Manager", label: "Product Manager" },
  { value: "DevOps Engineer", label: "DevOps Engineer" },
  { value: "Full Stack Developer", label: "Full Stack Developer" },
  { value: "Software Engineer", label: "Software Engineer" },
  { value: "QA Engineer", label: "QA Engineer" },
  { value: "Business Analyst", label: "Business Analyst" },
  { value: "Project Manager", label: "Project Manager" },
  { value: "Data Analyst", label: "Data Analyst" },
  { value: "Marketing Specialist", label: "Marketing Specialist" },
  { value: "Sales Executive", label: "Sales Executive" },
  { value: "Customer Support", label: "Customer Support" },
  { value: "HR Manager", label: "HR Manager" },
  { value: "Network Administrator", label: "Network Administrator" },
  { value: "Cybersecurity Analyst", label: "Cybersecurity Analyst" },
  { value: "Cloud Engineer", label: "Cloud Engineer" },
  { value: "Game Developer", label: "Game Developer" },
  { value: "Mobile Developer", label: "Mobile Developer" },
];

export const jobApi = {
  getJobs: async (params: JobQueryParams): Promise<PaginatedResponse<Job>> => {
    return new Promise<PaginatedResponse<Job>>((resolve) => {
      setTimeout(() => {
        let filteredJobs = [...mockJobs];
        
        if (params.search) {
          const searchLower = params.search.toLowerCase();
          filteredJobs = filteredJobs.filter(job => 
            job.title.toLowerCase().includes(searchLower) || 
            job.companyName.toLowerCase().includes(searchLower) ||
            job.location.toLowerCase().includes(searchLower)
          );
        }
        
        if (params.filterByJobLevel && params.filterByJobLevel.length > 0) {
          filteredJobs = filteredJobs.filter(job => 
            job.level && params.filterByJobLevel?.includes(job.level)
          );
        }

        favoriteJobIds.forEach(jobId => {
          const jobIndex = filteredJobs.findIndex(job => job.id === jobId);
          if (jobIndex !== -1 && filteredJobs[jobIndex]) {
            filteredJobs[jobIndex].isFavorite = true;
          }
        });

        const total = filteredJobs.length;
        const totalPages = Math.ceil(total / params.pageSize);
        const startIndex = (params.page - 1) * params.pageSize;
        const endIndex = startIndex + params.pageSize;

        const paginatedJobs = filteredJobs.slice(startIndex, endIndex);

        resolve({
          items: paginatedJobs,
          total,
          page: params.page,
          pageSize: params.pageSize,
          totalPages
        });
      }, 1000);
    });
  },

  getDetailJob: async (jobId: string): Promise<DetailJob> => {
    return new Promise<DetailJob>((resolve, reject) => {
      setTimeout(() => {
        const job = mockDetailJobs.find(j => j.id === jobId);
        if (job) {
          resolve(job);
        } else {
          reject(new Error("Job not found"));
        }
      }, 1000);
    });
  },

  getPromptSuggestions: async () => {
    const randomSuggestions = mockPromptSuggestions.sort(() => 0.5 - Math.random()).slice(0, 3);
    return new Promise<string[]>((resolve) => {
      setTimeout(() => {
        resolve(randomSuggestions);
      }, 2000);
    });
  },
  
  toggleFavorite: async (jobId: string) => {
    return new Promise<{ jobId: string, isFavorite: boolean }>((resolve) => {
      setTimeout(() => {
        if (favoriteJobIds.includes(jobId)) {
          favoriteJobIds = favoriteJobIds.filter(id => id !== jobId);
        } else {
          favoriteJobIds.push(jobId);
        }
        
        const isFavorite = favoriteJobIds.includes(jobId);
        resolve({ jobId, isFavorite });
      }, 500);
    });
  },
  
  getJobLevelOptions: async () => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(jobLevelOptions);
      }, 500);
    });
  },
  
  getJobTitleOptions: async () => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(jobTitleOptions);
      }, 500);
    });
  },
  
  getFavoriteJobs: async ({ page, pageSize } : { page: number, pageSize: number }): Promise<PaginatedResponse<Job>> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const favoriteJobs = mockJobs.filter(job => favoriteJobIds.includes(job.id));
        const total = favoriteJobs.length;
        const totalPages = Math.ceil(total / pageSize);
        const startIndex = (page - 1) * pageSize;
        const endIndex = startIndex + pageSize;

        const paginatedJobs = favoriteJobs.slice(startIndex, endIndex);

        resolve({
          items: paginatedJobs,
          total,
          page,
          pageSize,
          totalPages
        });
      }, 500);
    });
  },
};
