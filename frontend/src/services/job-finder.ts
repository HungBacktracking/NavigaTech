import { Job } from "../lib/types/job";

const mockJobs: Job[] = [
  {
    id: "1",
    title: "Senior Frontend Developer",
    originalUrl: "https://example.com/jobs/1",
    company: {
      name: "Google",
      logo: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/1200px-Google_%22G%22_Logo.svg.png",
      address: "Mountain View, CA",
      description: "Leading technology company"
    },
    location: "Remote / San Francisco",
    datePosted: new Date("2025-04-10"),
    skills: ["React", "TypeScript", "CSS", "Redux"],
    jobDescription: "We are looking for an experienced Frontend Developer to join our team...",
    jobRequirements: "5+ years of experience with modern JavaScript frameworks",
    type: "Full-time",
    salary: "$120K - $150K",
    benefit: "Health insurance, 401k, flexible hours",
    isExpired: false,
  },
  {
    id: "2",
    title: "UX/UI Designer",
    originalUrl: "https://example.com/jobs/2",
    company: {
      name: "Microsoft",
      logo: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Microsoft_logo.svg/1200px-Microsoft_logo.svg.png",
      address: "Redmond, WA"
    },
    location: "Hybrid / Seattle",
    datePosted: new Date("2025-04-20"),
    skills: ["Figma", "User Research", "Prototyping"],
    jobDescription: "Design intuitive interfaces for our flagship products...",
    type: "Contract",
    salary: "$90K - $110K",
    isExpired: false,
  },
  {
    id: "3",
    title: "Backend Engineer",
    originalUrl: "https://example.com/jobs/3",
    company: {
      name: "Startup XYZ",
      logo: "https://cdn.worldvectorlogo.com/logos/grab-2.svg"

    },
    location: "On-site / New York",
    datePosted: new Date("2025-04-25"),
    skills: ["Node.js", "MongoDB", "Express", "AWS"],
    jobDescription: "Help us scale our backend infrastructure...",
    type: "Part-time",
    salary: "$80K - $100K",
    isExpired: false,
  }
];

export const jobApi = {
  getJobs: async () => {
    return new Promise<Job[]>((resolve) => {
      setTimeout(() => {
        resolve(mockJobs);
      }, 1000);
    });
  }
};
