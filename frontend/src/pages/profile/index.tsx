import { useEffect, useState } from 'react';
import { message } from 'antd';
import { useForm } from 'react-hook-form';
import { motion } from 'framer-motion';
import { Project, Experience, Education, BasicInfoFormData } from '../../lib/types/user';
import { userAPI } from '../../services/user';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../../contexts/auth/auth-context';

import ProfileHeader from './components/profile-header';
import ContactInfoSection from './components/contact-section';
import SkillsSection from './components/skill-section';
import ExperienceSection from './components/experience-section';
import EducationSection from './components/education-section';
import ProjectsSection from './components/projects-section';
import { EducationModal, ExperienceModal, ProjectModal } from './components/modals';


const MyProfile = () => {
  const [messageApi, contextHolder] = message.useMessage({ top: 50 });
  const [editingSections, setEditingSections] = useState<boolean>(false);

  const basicInfoForm = useForm<BasicInfoFormData>();
  const { control: basicInfoControl, handleSubmit: handleBasicInfoSubmit, setValue: setBasicInfoValue, watch: watchBasicInfo, reset: resetBasicInfoForm } = basicInfoForm;

  const [isEducationModalVisible, setIsEducationModalVisible] = useState(false);
  const [isExperienceModalVisible, setIsExperienceModalVisible] = useState(false);
  const [isProjectModalVisible, setIsProjectModalVisible] = useState(false);

  const [editingEducation, setEditingEducation] = useState<Education | null>(null);
  const [editingExperience, setEditingExperience] = useState<Experience | null>(null);
  const [newProject, setNewProject] = useState<Project | null>(null);

  const [newSkill, setNewSkill] = useState('');
  const [skillsList, setSkillsList] = useState<string[]>([]);
  const [originalSkills, setOriginalSkills] = useState<string[]>([]);
  const [editingSkills, setEditingSkills] = useState(false);

  const [editMode, setEditMode] = useState(false);

  const [educationDeletingIds, setEducationDeletingIds] = useState<string[]>([]);
  const [experienceDeletingIds, setExperienceDeletingIds] = useState<string[]>([]);
  const [projectDeletingIds, setProjectDeletingIds] = useState<string[]>([]);

  const { user } = useAuth();
  const queryClient = useQueryClient();

  const { data: userData, isLoading: isLoadingUserData } = useQuery({
    queryKey: ['userData'],
    queryFn: () => userAPI.getUserDetail(user?.id || ''),
  });

  useEffect(() => {
    if (userData) {
      setBasicInfoValue('name', userData.name || '');
      setBasicInfoValue('headline', userData.headline || '');
      setBasicInfoValue('location', userData.location || '');
      setBasicInfoValue('introduction', userData.introduction || '');
      setBasicInfoValue('phone_number', userData.phone_number || '');
      setBasicInfoValue('linkedin_url', userData.linkedin_url || '');
      setBasicInfoValue('github_url', userData.github_url || '');
      setBasicInfoValue('email', userData.email || '');

      const skills = userData.skills?.map(skill => skill.name) || [];
      setSkillsList(skills);
      setOriginalSkills(skills);
    }
  }, [userData, setBasicInfoValue]);

  const experiencesList = userData?.experiences || [];
  const educationsList = userData?.educations || [];
  const projectsList = userData?.projects || [];

  const { mutate: updateBasicInfo, isPending: isUpdatingBasicInfo } = useMutation({
    mutationFn: (data: BasicInfoFormData) =>
      userAPI.updateBasicInfo(user?.id || '', data),
    onSuccess: () => {
      messageApi.success('Profile information updated successfully!');
      queryClient.invalidateQueries({ queryKey: ['userData'] });
      setEditingSections(false);
    },
    onError: () => {
      messageApi.error('Failed to update profile information');
    }
  });

  const { mutate: updateSkills, isPending: isUpdatingSkills } = useMutation({
    mutationFn: (skills: string[]) =>
      userAPI.updateSkills(user?.id || '', skills),
    onSuccess: () => {
      messageApi.success('Skills updated successfully!');
      queryClient.invalidateQueries({ queryKey: ['userData'] });
      setEditingSkills(false);
    },
    onError: () => {
      messageApi.error('Failed to update skills');
    }
  });

  const { mutate: addEducation, isPending: isAddingEducation } = useMutation({
    mutationFn: (education: Education) =>
      userAPI.addEducation(user?.id || '', education),
    onSuccess: () => {
      messageApi.success('Education added successfully!');
      queryClient.invalidateQueries({ queryKey: ['userData'] });
    },
    onError: () => {
      messageApi.error('Failed to add education');
    }
  });

  const { mutate: updateEducation, isPending: isUpdatingEducation } = useMutation({
    mutationFn: (education: Education) =>
      userAPI.updateEducation(user?.id || '', education),
    onSuccess: () => {
      messageApi.success('Education updated successfully!');
      queryClient.invalidateQueries({ queryKey: ['userData'] });
    },
    onError: () => {
      messageApi.error('Failed to update education');
    }
  });

  const { mutate: deleteEducation, isPending: isDeletingEducation } = useMutation({
    mutationFn: (educationId: string) =>
      userAPI.deleteEducation(user?.id || '', educationId),
  });

  const { mutate: addExperience, isPending: isAddingExperience } = useMutation({
    mutationFn: (experience: Experience) =>
      userAPI.addExperience(user?.id || '', experience),
    onSuccess: () => {
      messageApi.success('Experience added successfully!');
      queryClient.invalidateQueries({ queryKey: ['userData'] });
    },
    onError: () => {
      messageApi.error('Failed to add experience');
    }
  });

  const { mutate: updateExperience, isPending: isUpdatingExperience } = useMutation({
    mutationFn: (experience: Experience) =>
      userAPI.updateExperience(user?.id || '', experience),
    onSuccess: () => {
      messageApi.success('Experience updated successfully!');
      queryClient.invalidateQueries({ queryKey: ['userData'] });
    },
    onError: () => {
      messageApi.error('Failed to update experience');
    }
  });

  const { mutate: deleteExperience, isPending: isDeletingExperience } = useMutation({
    mutationFn: (experienceId: string) =>
      userAPI.deleteExperience(user?.id || '', experienceId),
  });

  const { mutate: addProject, isPending: isAddingProject } = useMutation({
    mutationFn: (project: Project) =>
      userAPI.addProject(user?.id || '', project),
    onSuccess: () => {
      messageApi.success('Project added successfully!');
      queryClient.invalidateQueries({ queryKey: ['userData'] });
    },
    onError: () => {
      messageApi.error('Failed to add project');
    }
  });

  const { mutate: updateProject, isPending: isUpdatingProject } = useMutation({
    mutationFn: (project: Project) =>
      userAPI.updateProject(user?.id || '', project),
    onSuccess: () => {
      messageApi.success('Project updated successfully!');
      queryClient.invalidateQueries({ queryKey: ['userData'] });
    },
    onError: () => {
      messageApi.error('Failed to update project');
    }
  });

  const { mutate: deleteProject, isPending: isDeletingProject } = useMutation({
    mutationFn: (projectId: string) =>
      userAPI.deleteProject(user?.id || '', projectId),
  });

  const watchName = watchBasicInfo('name', '');
  const watchHeadline = watchBasicInfo('headline', '');
  const watchLocation = watchBasicInfo('location', '');
  const watchIntroduction = watchBasicInfo('introduction', '');
  const watchPhoneNumber = watchBasicInfo('phone_number', '');
  const watchLinkedin = watchBasicInfo('linkedin_url', '');
  const watchGithub = watchBasicInfo('github_url', '');
  const watchEmail = watchBasicInfo('email', '');

  const onSubmitBasicInfo = (data: BasicInfoFormData) => {
    updateBasicInfo(data);
  };

  const handleEditProfile = () => {
    setEditingSections(true);
  };

  const handleCancelEditProfile = () => {
    if (userData) {
      resetBasicInfoForm({
        name: userData.name || '',
        headline: userData.headline || '',
        location: userData.location || '',
        introduction: userData.introduction || '',
        phone_number: userData.phone_number || '',
        linkedin_url: userData.linkedin_url || '',
        github_url: userData.github_url || '',
        email: userData.email || '',
      });
    }
    setEditingSections(false);
  };

  const handleSubmitSkills = () => {
    updateSkills(skillsList);
    setOriginalSkills([...skillsList]);
  };

  const handleCancelSkillsEdit = () => {
    setSkillsList([...originalSkills]);
    setEditingSkills(false);
  };

  const handleAddSkill = () => {
    if (newSkill.trim() && !skillsList.includes(newSkill.trim())) {
      setSkillsList([...skillsList, newSkill.trim()]);
      setNewSkill('');
    }
  };

  const handleRemoveSkill = (skillToRemove: string) => {
    const updatedSkills = skillsList.filter(skill => skill !== skillToRemove);
    setSkillsList(updatedSkills);
  };

  const openEducationModal = (education?: Education) => {
    if (education) {
      setEditingEducation({ ...education });
      setEditMode(true);
    } else {
      setEditingEducation({
        id: Date.now().toString(),
        major: '',
        school_name: '',
        degree_type: '',
        is_current: false,
        description: '',
        start_date: '',
        end_date: ''
      });
      setEditMode(false);
    }
    setIsEducationModalVisible(true);
  };

  const handleAddEducation = (data: Education) => {
    if (editMode) {
      updateEducation(data);
    } else {
      addEducation(data);
    }

    setIsEducationModalVisible(false);
    setEditingEducation(null);
    setEditMode(false);
  };

  const handleDeleteEducation = (educationId: string) => {
    deleteEducation(educationId, {
      onSuccess: () => {
        setEducationDeletingIds(educationDeletingIds.filter(id => id !== educationId));
        messageApi.success('Education deleted successfully!');
        queryClient.invalidateQueries({ queryKey: ['userData'] });
      },
      onError: () => {
        setEducationDeletingIds(educationDeletingIds.filter(id => id !== educationId));
        messageApi.error('Failed to delete education');
      }
    });
  };

  const openExperienceModal = (experience?: Experience) => {
    if (experience) {
      setEditingExperience({ ...experience });
      setEditMode(true);
    } else {
      setEditingExperience({
        id: Date.now().toString(),
        company: '',
        position: '',
        start_date: '',
        end_date: '',
        description: ''
      });
      setEditMode(false);
    }
    setIsExperienceModalVisible(true);
  };

  const handleAddExperience = (data: Experience) => {
    if (editMode) {
      updateExperience(data!);
    } else {
      addExperience(data!);
    }

    setIsExperienceModalVisible(false);
    setEditingExperience(null);
    setEditMode(false);
  };

  const handleDeleteExperience = (experienceId: string) => {
    setExperienceDeletingIds([...experienceDeletingIds, experienceId]);
    deleteExperience(experienceId, {
      onSuccess: () => {
        setExperienceDeletingIds(experienceDeletingIds.filter(id => id !== experienceId));
        messageApi.success('Experience deleted successfully!');
        queryClient.invalidateQueries({ queryKey: ['userData'] });
      },
      onError: () => {
        setExperienceDeletingIds(experienceDeletingIds.filter(id => id !== experienceId));
        messageApi.error('Failed to delete experience');
      }
    });
  };

  const openProjectModal = (project?: Project) => {
    if (project) {
      setNewProject({ ...project });
      setEditMode(true);
    } else {
      setNewProject({
        id: Date.now().toString(),
        project_name: '',
        role: '',
        description: '',
        achievement: '',
        start_date: '',
        end_date: ''
      });
      setEditMode(false);
    }
    setIsProjectModalVisible(true);
  };

  const handleAddProject = () => {
    if (editMode) {
      updateProject(newProject!);
    } else {
      addProject(newProject!);
    }

    setIsProjectModalVisible(false);
    setNewProject(null);
    setEditMode(false);
  };

  const handleDeleteProject = (projectId: string) => {
    setProjectDeletingIds([...projectDeletingIds, projectId]);
    deleteProject(projectId, {
      onSuccess: () => {
        setProjectDeletingIds(projectDeletingIds.filter(id => id !== projectId));
        messageApi.success('Education deleted successfully!');
        queryClient.invalidateQueries({ queryKey: ['userData'] });
      },
      onError: () => {
        setProjectDeletingIds(projectDeletingIds.filter(id => id !== projectId));
        messageApi.error('Failed to delete education');
      }
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      style={{ margin: '0 auto', maxWidth: '800px' }}
    >
      {contextHolder}

      <ProfileHeader
        editingSections={editingSections}
        name={watchName}
        headline={watchHeadline}
        location={watchLocation}
        introduction={watchIntroduction}
        handleEditProfile={handleEditProfile}
        handleCancelEdit={handleCancelEditProfile}
        handleBasicInfoSubmit={handleBasicInfoSubmit(onSubmitBasicInfo)}
        basicInfoControl={basicInfoControl}
        isUpdatingBasicInfo={isUpdatingBasicInfo}
      />

      {!editingSections && (
        <ContactInfoSection
          email={watchEmail}
          phoneNumber={watchPhoneNumber}
          linkedin={watchLinkedin}
          github={watchGithub}
        />
      )}

      <SkillsSection
        editingSections={editingSections}
        skillsList={skillsList}
        editingSkills={editingSkills}
        setEditingSkills={setEditingSkills}
        newSkill={newSkill}
        setNewSkill={setNewSkill}
        handleAddSkill={handleAddSkill}
        handleRemoveSkill={handleRemoveSkill}
        onSubmitSkills={handleSubmitSkills}
        isUpdatingSkills={isUpdatingSkills}
        onCancelEdit={handleCancelSkillsEdit}
      />

      <ExperienceSection
        experiencesList={experiencesList}
        openExperienceModal={openExperienceModal}
        handleDeleteExperience={handleDeleteExperience}
        isDeletingExperience={isDeletingExperience}
        deletingIds={experienceDeletingIds}
      />

      <EducationSection
        educationsList={educationsList}
        openEducationModal={openEducationModal}
        handleDeleteEducation={handleDeleteEducation}
        isDeletingEducation={isDeletingEducation}
        deletingIds={educationDeletingIds}
      />

      <ProjectsSection
        projectsList={projectsList}
        openProjectModal={openProjectModal}
        handleDeleteProject={handleDeleteProject}
        isDeletingProject={isDeletingProject}
        deletingIds={projectDeletingIds}
      />

      <EducationModal
        isVisible={isEducationModalVisible}
        editMode={editMode}
        editingEducation={editingEducation}
        isAddingEducation={isAddingEducation}
        isUpdatingEducation={isUpdatingEducation}
        handleAddEditEducation={handleAddEducation}
        closeModal={() => setIsEducationModalVisible(false)}
      />

      <ExperienceModal
        isVisible={isExperienceModalVisible}
        editMode={editMode}
        editingExperience={editingExperience}
        isAddingExperience={isAddingExperience}
        isUpdatingExperience={isUpdatingExperience}
        handleAddEditExperience={handleAddExperience}
        closeModal={() => setIsExperienceModalVisible(false)}
      />

      <ProjectModal
        isVisible={isProjectModalVisible}
        editMode={editMode}
        newProject={newProject}
        isAddingProject={isAddingProject}
        isUpdatingProject={isUpdatingProject}
        setNewProject={setNewProject}
        handleAddProject={handleAddProject}
        closeModal={() => setIsProjectModalVisible(false)}
      />
    </motion.div>
  );
};

export default MyProfile;
