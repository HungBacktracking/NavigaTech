interface AnalysisResult {
  id: string;
  jobId: string;
  matchScore: number;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  createdAt: Date;
}

interface JobAnalysisRequest {
  jobId: string;
  resumeText?: string;
  userProfile?: {
    skills: string[];
    experience: string;
    education: string;
  };
}

// Mock analysis results
const mockAnalysisResults: AnalysisResult[] = [
  {
    id: "a1",
    jobId: "1",
    matchScore: 85,
    strengths: [
      "Strong experience with React and TypeScript",
      "Experience with modern frontend frameworks",
      "Good understanding of performance optimization"
    ],
    weaknesses: [
      "Limited experience with NextJS",
      "No mention of testing frameworks in resume",
      "Limited experience with GraphQL"
    ],
    recommendations: [
      "Highlight your React and TypeScript experience in your application",
      "Consider adding a section about performance optimization in your cover letter",
      "Try to gain some experience with NextJS through personal projects"
    ],
    createdAt: new Date("2025-04-28")
  },
  {
    id: "a2",
    jobId: "2",
    matchScore: 70,
    strengths: [
      "Experience with UI/UX design principles",
      "Knowledge of accessible design",
      "Portfolio includes relevant projects"
    ],
    weaknesses: [
      "Limited experience with Figma",
      "No formal design education mentioned",
      "Limited experience with design systems"
    ],
    recommendations: [
      "Take a Figma course to strengthen your technical skills",
      "Emphasize your accessibility knowledge in your application",
      "Include more details about collaborative design work"
    ],
    createdAt: new Date("2025-04-29")
  }
];

export const jobAnalysisApi = {
  /**
   * Analyze job match based on resume or user profile
   */
  analyzeJobMatch: async (request: JobAnalysisRequest): Promise<AnalysisResult> => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        // Simulate a possible analysis failure
        if (Math.random() < 0.1) {
          reject(new Error("Analysis failed due to server error"));
          return;
        }
        
        // Check if we have a mock analysis for this job
        const existingAnalysis = mockAnalysisResults.find(a => a.jobId === request.jobId);
        
        if (existingAnalysis) {
          resolve(existingAnalysis);
        } else {
          // Generate a new random analysis
          const newAnalysis: AnalysisResult = {
            id: `a${Date.now()}`,
            jobId: request.jobId,
            matchScore: Math.floor(Math.random() * 40) + 60, // Random score between 60-100
            strengths: [
              "Your technical skills match the job requirements",
              "Your experience level is appropriate for this position",
              "You have relevant project experience"
            ],
            weaknesses: [
              "Missing some specific technical skills mentioned in the job",
              "Your resume could better highlight relevant experience",
              "Consider adding more details about your achievements"
            ],
            recommendations: [
              "Tailor your resume to highlight relevant skills",
              "Prepare to discuss how your experience relates to the job requirements",
              "Consider taking a course in one of the required technologies"
            ],
            createdAt: new Date()
          };
          
          mockAnalysisResults.push(newAnalysis);
          resolve(newAnalysis);
        }
      }, 2000); // Longer timeout to simulate AI processing
    });
  },
  
  getAnalysisHistory: async (): Promise<AnalysisResult[]> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(mockAnalysisResults);
      }, 800);
    });
  },
  
  getAnalysisById: async (analysisId: string): Promise<AnalysisResult | null> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const analysis = mockAnalysisResults.find(a => a.id === analysisId);
        resolve(analysis || null);
      }, 500);
    });
  },
  
  deleteAnalysis: async (analysisId: string): Promise<boolean> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const index = mockAnalysisResults.findIndex(a => a.id === analysisId);
        if (index !== -1) {
          mockAnalysisResults.splice(index, 1);
          resolve(true);
        } else {
          resolve(false);
        }
      }, 700);
    });
  }
};