import { JobAnalysis, Job, JobAnalysisQueryParams, JobAnalysisDetail } from "../lib/types/job";
import { PaginatedResponse } from "../lib/types/pagination";

const jobIdToAnalysisIdMap = new Map<string, string>([
  ["1", "aj1"],
  ["2", "aj2"],
  ["3", "aj3"]
]);

const getRandomScore = (min = 35, max = 95) => Math.floor(Math.random() * (max - min + 1)) + min;

const possibleStrengths = [
  "Strong experience with required technologies",
  "Excellent communication skills",
  "Proven track record in similar roles",
  "Experience with agile methodologies",
  "Strong problem-solving abilities",
  "Experience with cloud platforms",
  "Proficient in multiple programming languages",
  "Experience with relevant frameworks",
  "Strong database knowledge",
  "Experience with CI/CD pipelines",
  "Leadership experience",
  "Strong analytical thinking",
  "Experience with system design",
  "Knowledge of best practices",
  "Experience with testing frameworks"
];

const possibleWeaknesses = [
  "Limited experience with some required technologies",
  "No certification in relevant areas",
  "Lack of experience in specific industry",
  "Limited management experience",
  "Needs improvement in communication skills",
  "Lack of experience with specific tools",
  "Limited cloud platform experience",
  "Limited knowledge of specific frameworks",
  "Limited experience with specific databases",
  "Limited experience with machine learning",
  "No experience with DevOps",
  "Limited mobile development experience",
  "No experience with specific programming languages"
];

const mockJobAnalyses: JobAnalysis[] = [
  {
    id: "aj1",
    title: "Senior Frontend Developer",
    companyName: "Google",
    companyLogo: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/1200px-Google_%22G%22_Logo.svg.png",
    location: "Remote / San Francisco",
    datePosted: new Date("2025-04-10"),
    originalUrl: "https://example.com/jobs/1",
    skills: ["React", "TypeScript", "CSS", "Redux", "GraphQL"],
    type: "Full-time",
    level: "Senior",
    salary: "$120K - $150K",
    matchScore: 85,
    isCreatedCV: true,
    weaknesses: ["Limited experience with NextJS", "No mention of testing frameworks"],
    strengths: ["Strong experience with React and TypeScript", "Experience with modern frontend frameworks"],
    analyzedAt: new Date("2025-05-01")
  },
  {
    id: "aj2",
    title: "UX/UI Designer",
    companyName: "Microsoft",
    companyLogo: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Microsoft_logo.svg/1200px-Microsoft_logo.svg.png",
    location: "Hybrid / Seattle",
    datePosted: new Date("2025-04-20"),
    originalUrl: "https://example.com/jobs/2",
    skills: ["Figma", "User Research", "Prototyping", "Design Systems"],
    type: "Contract",
    level: "Mid-level",
    salary: "$90K - $110K",
    matchScore: 70,
    isCreatedCV: false,
    weaknesses: ["Limited experience with Figma", "No formal design education mentioned"],
    strengths: ["Experience with UI/UX design principles", "Knowledge of accessible design"],
    analyzedAt: new Date("2025-05-02")
  },
  {
    id: "aj3",
    title: "Backend Engineer",
    companyName: "Startup XYZ",
    companyLogo: "https://cdn.worldvectorlogo.com/logos/grab-2.svg",
    location: "On-site / New York",
    datePosted: new Date("2025-04-25"),
    originalUrl: "https://example.com/jobs/3",
    skills: ["Node.js", "MongoDB", "Express", "AWS"],
    type: "Part-time",
    level: "Junior",
    salary: "$80K - $100K",
    matchScore: 92,
    isCreatedCV: true,
    weaknesses: ["Limited cloud deployment experience"],
    strengths: ["Strong Node.js and Express background", "Experience with containerization"],
    analyzedAt: new Date("2025-05-03")
  }
];

const createAnalysisFromJob = (job: Job): JobAnalysis => {
  const numStrengths = Math.floor(Math.random() * 3) + 3;
  const numWeaknesses = Math.floor(Math.random() * 3) + 3;
  
  const shuffledStrengths = [...possibleStrengths].sort(() => 0.5 - Math.random());
  const shuffledWeaknesses = [...possibleWeaknesses].sort(() => 0.5 - Math.random());
  
  const selectedStrengths = shuffledStrengths.slice(0, numStrengths);
  const selectedWeaknesses = shuffledWeaknesses.slice(0, numWeaknesses);
  
  const matchScore = getRandomScore();
  
  const analysisId = "aj" + (mockJobAnalyses.length + 1);
  
  const newAnalysis: JobAnalysis = {
    ...job,
    id: analysisId,
    matchScore,
    isCreatedCV: false,
    weaknesses: selectedWeaknesses,
    strengths: selectedStrengths,
    analyzedAt: new Date()
  };
  
  mockJobAnalyses.unshift(newAnalysis);
  
  jobIdToAnalysisIdMap.set(job.id, analysisId);

  return newAnalysis;
}

// Add sample feedback texts with markdown format
const generalFeedbackSamples = [
  `## Overall Assessment\n\nYour profile shows a **good alignment** with this job position. You have several relevant skills and experiences that make you a promising candidate. However, there are some areas where strengthening your profile could significantly improve your chances.\n\n**Key recommendations:**\n- Highlight your experience *${possibleStrengths[Math.floor(Math.random() * 3)]}*\n- Consider obtaining certifications in relevant technologies\n- Tailor your resume to emphasize specific project outcomes`,
  
  `## General Overview\n\nYour profile demonstrates **moderate alignment** with this role's requirements. While you possess many of the fundamental skills required, there are several areas where additional experience or training would be beneficial.\n\n**Suggested improvements:**\n- Focus on gaining practical experience with the required technologies\n- Develop deeper knowledge in specific technical areas\n- Emphasize your problem-solving abilities with concrete examples`,
  
  `## Profile Evaluation\n\nYour profile shows a **strong match** with this position. Your experience and skill set align well with the job requirements, making you a competitive candidate for this role.\n\n**Key strengths:**\n- Extensive experience in similar roles\n- Strong technical background in required areas\n- Demonstrated success in comparable projects\n\nContinue emphasizing these aspects in your application materials.`
];

const roleFeedbackSamples = [
  `## Role Fit Analysis\n\nYour previous roles have prepared you well for this position. Your experience as a developer shows a **clear progression** that aligns with the career trajectory for this role. However, there's room to better demonstrate your leadership capabilities.\n\n**Recommendations:**\n- Highlight team leadership experiences\n- Quantify the impact of your technical decisions\n- Emphasize cross-functional collaboration instances`,
  
  `## Role Compatibility\n\nYour experience level **partially matches** the seniority required for this position. While you have relevant experience, the role may require more depth in certain areas.\n\n**Areas to address:**\n- Demonstrate experience with larger-scale projects\n- Show progression in technical responsibility\n- Highlight instances where you've mentored others or led technical decisions`,
  
  `## Position Alignment\n\nYour career history shows a **very strong alignment** with this role's requirements. Your progression through similar positions has equipped you with the exact experience profile this employer is seeking.\n\n**Key points to emphasize:**\n- Your specific experience with similar technologies\n- Your history of success in comparable roles\n- Your understanding of the industry-specific challenges`
];

const skillsFeedbackSamples = [
  `## Technical Skills Assessment\n\nYour technical skills profile is **moderately aligned** with this position. While you have experience with several key technologies, there are some gaps in areas that are important for this role.\n\n**Skills to highlight:**\n- ✅ Strong background in React and frontend development\n- ✅ Experience with TypeScript and modern JS practices\n\n**Skills to develop:**\n- ❓ Limited experience with GraphQL\n- ❓ No mention of experience with CI/CD pipelines\n- ❓ Consider gaining experience with container technologies`,
  
  `## Skills Evaluation\n\nYour skills profile shows a **strong match** with the technical requirements. You possess most of the critical skills needed for success in this position.\n\n**Notable strengths:**\n- ✅ Extensive experience with required programming languages\n- ✅ Strong background in system architecture\n- ✅ Demonstrable experience with necessary frameworks\n\n**Consider developing:**\n- ❓ More experience with specific cloud services\n- ❓ Knowledge of industry-specific technologies`,
  
  `## Technical Capabilities\n\nYour technical skills are **partially aligned** with this role. While you have a good foundation, there are several key areas where additional experience would significantly strengthen your candidacy.\n\n**Strong points:**\n- ✅ Solid programming fundamentals\n- ✅ Experience with relevant databases\n\n**Areas for improvement:**\n- ❓ Limited experience with required frameworks\n- ❓ Need to develop deeper knowledge of deployment practices\n- ❓ Consider gaining experience with emerging technologies in this field`
];

const workExperienceFeedbackSamples = [
  `## Work Experience Analysis\n\nYour work history shows **relevant experience** in similar roles. The projects you've worked on demonstrate capabilities that align with this position's requirements.\n\n**Highlights:**\n- Your experience leading development teams is particularly relevant\n- Your track record of delivering projects on time will be valued\n\n**Suggestions:**\n- Quantify your achievements with more metrics\n- Provide more details about specific technical challenges you've overcome\n- Highlight experience with technologies specifically mentioned in the job description`,
  
  `## Professional Background Review\n\nYour work experience shows **some alignment** with this role. While you have worked in the industry, your specific project experience may not fully demonstrate all the capabilities sought for this position.\n\n**Strengths to emphasize:**\n- Your experience in collaborative development environments\n- Your ability to adapt to various technical requirements\n\n**Areas to address:**\n- Demonstrate more experience with enterprise-scale applications\n- Highlight any relevant domain knowledge\n- Consider showcasing side projects that demonstrate relevant skills`,
  
  `## Career History Evaluation\n\nYour work experience demonstrates a **strong fit** for this position. The progression of your career shows deliberate development in areas critical to this role.\n\n**Key relevant experiences:**\n- Your background in similar industry sectors\n- Your history of working with similar technology stacks\n- Your demonstrated ability to solve complex technical problems\n\n**Continue to highlight:**\n- Specific projects with technologies mentioned in the job description\n- Instances where you've improved processes or performance`
];

const educationFeedbackSamples = [
  `## Education Assessment\n\nYour educational background is **well-aligned** with this position. Your formal education provides a strong foundation for the technical requirements of this role.\n\n**Key strengths:**\n- Relevant degree in computer science or related field\n- Specialized coursework in relevant technologies\n\n**Enhancement opportunities:**\n- Consider additional certifications in specialized areas\n- Highlight any relevant continuing education\n- Emphasize practical applications of your academic knowledge`,
  
  `## Academic Background Review\n\nYour education is **partially matched** to this role. While your degree provides a foundation, specific technical training in key areas would strengthen your profile.\n\n**Positives:**\n- Your educational foundation in core principles\n- Relevant academic projects\n\n**Consider adding:**\n- Specialized certifications in job-specific technologies\n- Self-directed learning in key technical areas\n- Examples of how you've applied academic knowledge to practical problems`,
  
  `## Educational Qualifications\n\nYour educational background shows a **strong correlation** with this role's requirements. Your specialized academic focus is directly relevant to the technical needs of this position.\n\n**Significant advantages:**\n- Advanced degree in a directly relevant field\n- Specialized academic research in applicable areas\n- Recent educational experiences with modern technologies\n\n**Leverage these by:**\n- Drawing direct connections between your academic work and job requirements\n- Highlighting any publications or significant projects`
];

const languageFeedbackSamples = [
  `## Language Skills Assessment\n\nYour language skills are **adequately aligned** with the position requirements. Your proficiency in English appears sufficient for the technical communication needed in this role.\n\n**Strengths:**\n- Professional-level English proficiency\n- Clear technical communication skills\n\n**Potential improvements:**\n- Consider highlighting any experience with international teams\n- Emphasize technical documentation skills\n- Showcase any additional languages that might be valuable`,
  
  `## Communication Capabilities\n\nYour language and communication skills appear **well-matched** to this position. Your ability to convey technical concepts clearly will be an asset in this role.\n\n**Notable strengths:**\n- Strong technical writing demonstrated in your materials\n- Clear articulation of complex concepts\n\n**Enhancement opportunities:**\n- Highlight experience presenting technical information to non-technical stakeholders\n- Emphasize collaborative communication experiences`,
  
  `## Language Proficiency Evaluation\n\nYour language skills show **strong alignment** with this role's requirements. Your multilingual capabilities could be a significant advantage for this position.\n\n**Key advantages:**\n- Fluency in multiple languages relevant to the company's markets\n- Demonstrated ability to communicate technical concepts across language barriers\n- Experience with international teams or clients\n\n**Leverage by:**\n- Highlighting specific instances where your language skills benefited previous projects\n- Emphasizing cultural adaptability alongside language proficiency`
];

const getRandomFeedback = (samples: string[]) => {
  const randomIndex = Math.floor(Math.random() * samples.length);
  return samples[randomIndex];
};

export const jobAnalysisApi = {
  getJobAnalyses: async (params: JobAnalysisQueryParams): Promise<PaginatedResponse<JobAnalysis>> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        let filteredAnalyses = [...mockJobAnalyses];

        if (params.search) {
          const searchLower = params.search.toLowerCase();
          filteredAnalyses = filteredAnalyses.filter(analysis => 
            analysis.title.toLowerCase().includes(searchLower) || 
            analysis.companyName.toLowerCase().includes(searchLower)
          );
        }

        const total = filteredAnalyses.length;
        const totalPages = Math.ceil(total / params.pageSize);
        const startIdx = (params.page - 1) * params.pageSize;
        const endIdx = startIdx + params.pageSize;

        const paginatedAnalyses = filteredAnalyses.slice(startIdx, endIdx);

        resolve({
          items: paginatedAnalyses,
          total,
          page: params.page,
          pageSize: params.pageSize,
          totalPages
        })
      }, 1000);
    });
  },

  getAnalysisJobById: async (jobId: string): Promise<JobAnalysis | null> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const job = mockJobAnalyses.find(j => j.id === jobId);
        resolve(job || null);
      }, 500);
    });
  },

  createAnalysisFromJobId: async (jobId: string): Promise<JobAnalysis | null> => {
    return new Promise((resolve, reject) => {
      setTimeout(async () => {
        try {
          // Check if analysis already exists
          const existingAnalysisId = jobIdToAnalysisIdMap.get(jobId);
          if (existingAnalysisId) {
            const existingAnalysis = mockJobAnalyses.find(a => a.id === existingAnalysisId);
            if (existingAnalysis) {
              existingAnalysis.analyzedAt = new Date();
              existingAnalysis.matchScore = getRandomScore(35, 95);
              resolve(existingAnalysis);
              return;
            }
          }

          // If not, we need to fetch the job details first
          try {
            const { jobApi } = await import('./job-finder');
            const job = await jobApi.getDetailJob(jobId);
            if (!job) {
              resolve(null);
              return;
            }

            const simpleJob: Job = {
              id: job.id,
              title: job.title,
              companyName: job.company?.name || "Unknown Company",
              companyLogo: job.company?.logo || "",
              originalUrl: job.originalUrl,
              location: job.location,
              datePosted: job.datePosted,
              skills: job.skills,
              type: job.type,
              level: job.level,
              salary: job.salary
            };

            const analysis = createAnalysisFromJob(simpleJob);
            resolve(analysis);
          } catch (error) {
            reject(error);
          }
        } catch (error) {
          reject(error);
        }
      }, 5000);
    });
  },
  
  deleteJobAnalysis: async (analysisId: string): Promise<boolean> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const index = mockJobAnalyses.findIndex(job => job.id === analysisId);
        if (index !== -1) {
          for (const [jobId, mappedAnalysisId] of jobIdToAnalysisIdMap.entries()) {
            if (mappedAnalysisId === analysisId) {
              jobIdToAnalysisIdMap.delete(jobId);
              break;
            }
          }
          
          mockJobAnalyses.splice(index, 1);
          resolve(true);
        } else {
          resolve(false);
        }
      }, 700);
    });
  },

  createCV: async (jobId: string): Promise<boolean> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const job = mockJobAnalyses.find(j => j.id === jobId);
        if (job) {
          job.isCreatedCV = !job.isCreatedCV;
          resolve(job.isCreatedCV);
        } else {
          resolve(false);
        }
      }, 500);
    });
  },

  getAnalysisJobDetailById: async (jobAnalysisId: string): Promise<JobAnalysisDetail | null> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const jobAnalysis = mockJobAnalyses.find(j => j.id === jobAnalysisId);
        
        if (!jobAnalysis) {
          resolve(null);
          return;
        }
        
        const detailedAnalysis: JobAnalysisDetail = {
          ...jobAnalysis,
          generalFeedback: getRandomFeedback(generalFeedbackSamples) ?? "No feedback available",
          roleFeedback: getRandomFeedback(roleFeedbackSamples) ?? "No feedback available",
          skillsFeedback: getRandomFeedback(skillsFeedbackSamples) ?? "No feedback available",
          workExperienceFeedback: getRandomFeedback(workExperienceFeedbackSamples) ?? "No feedback available",
          educationFeedback: getRandomFeedback(educationFeedbackSamples) ?? "No feedback available",
          languageFeedback: getRandomFeedback(languageFeedbackSamples) ?? "No feedback available",
        };
        
        resolve(detailedAnalysis);
      }, 800);
    });
  }
};
