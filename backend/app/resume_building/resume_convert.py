import json

from app.schema.user_schema import UserDetailResponse


class ResumeConverter:
    def __init__(self, data: UserDetailResponse):
        self.data = data

    def remove_duplicate_experiences_by_company(self):
        """
        Remove duplicate experiences based on company name.
        """
        seen_companies = set()
        unique_experiences = []

        for experience in self.data.get('experiences', []):
            company_name = experience.get('company_name', '')
            if company_name not in seen_companies:
                unique_experiences.append(experience)
                seen_companies.add(company_name)

        self.data['experiences'] = unique_experiences

    def build_resume_text(self):
        """
        Build the resume text from the provided data.
        """
        # Extracting basic information
        full_name = self.data.get("name", "N/A")
        email = self.data.get("email", "N/A")
        phone_number = self.data.get("phone_number", "N/A")
        location = self.data.get("location", "N/A")
        introduction = self.data.get(
            "introduction", "No introduction provided.")

        # Extracting skills
        skills = "\n".join([skill.get("name", "No skill name")
                           for skill in self.data.get("skills", [])])

        # Extracting project experience
        projects = "\n".join([f"Project name: {project.get('project_name', 'N/A')}\n"
                              f"Description: {project.get('description', 'No description provided.')}\n"
                              for project in self.data.get("projects", [])]) if self.data.get("projects") else "No project experience listed."

        # Extracting work experience
        experiences = "\n".join([f"Company: {exp.get('company_name', 'N/A')}\n"
                                 f"Title: {exp.get('title', 'N/A')}\n"
                                 f"Location: {exp.get('location', 'N/A')}\n"
                                 f"Description: {exp.get('description', 'No description provided.')}\n"
                                 f"Start Date: {exp.get('start_date', 'N/A')}\n"
                                 f"End Date: {exp.get('end_date', 'N/A')}\n"
                                 for exp in self.data.get("experiences", [])]) if self.data.get("experiences") else "No work experience listed."

        # Extracting education
        education_details = "\n".join([f"Major: {edu.get('major', 'N/A')}\n"
                                      f"School: {edu.get('school_name', 'N/A')}\n"
                                       f"Degree: {edu.get('degree_type', 'N/A')}\n"
                                       f"GPA: {edu.get('gpa', 'N/A')}\n"
                                       for edu in self.data.get("educations", [])]) if self.data.get("educations") else "No education information listed."

        full_resume_text = f"""
            Full Name: {full_name}
            Email: {email}
            Phone: {phone_number}
            Location: {location}
            Education Details:
            {education_details}
            
            Introduction:
            {introduction}
            
            Skills:
            {skills if skills else "No skills listed."}
            
            Project Experience:
            {projects}
            
            Work Experience:
            {experiences}
        """
        return full_resume_text.strip()

    @classmethod
    def process_json(cls, json_file):
        """
        Process the JSON file to generate the resume text.
        """
        # Load and process the data
        json_data = json.loads(json_file)
        resume = cls(json_data)

        # Remove duplicate experiences and build the resume text
        resume.remove_duplicate_experiences_by_company()
        return resume.build_resume_text()
