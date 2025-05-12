import React, { useEffect } from 'react';
import { Form, Input, Modal, DatePicker } from 'antd';
import { Education, Experience, Project } from '../../../../lib/types/user';
import dayjs from 'dayjs';
import { useForm, Controller } from 'react-hook-form';

interface EducationModalProps {
  isVisible: boolean;
  editMode: boolean;
  editingEducation: Education | null;
  isAddingEducation: boolean;
  isUpdatingEducation: boolean;
  handleAddEditEducation: (data: Education) => void;
  closeModal: () => void;
}

interface ExperienceModalProps {
  isVisible: boolean;
  editMode: boolean;
  editingExperience: Experience | null;
  isAddingExperience: boolean;
  isUpdatingExperience: boolean;
  handleAddEditExperience: (data: Experience) => void;
  closeModal: () => void;
}

interface ProjectModalProps {
  isVisible: boolean;
  editMode: boolean;
  newProject: Project | null;
  isAddingProject: boolean;
  isUpdatingProject: boolean;
  setNewProject: (project: Project | null) => void;
  handleAddProject: () => void;
  closeModal: () => void;
}

export const EducationModal = ({
  isVisible,
  editMode,
  editingEducation,
  isAddingEducation,
  isUpdatingEducation,
  handleAddEditEducation,
  closeModal
}: EducationModalProps) => {
  const { control, handleSubmit, formState: { errors }, reset, watch } = useForm<Education>({
    defaultValues: {
      id: editingEducation?.id || '',
      major: editingEducation?.major || '',
      school_name: editingEducation?.school_name || '',
      degree_type: editingEducation?.degree_type || '',
      is_current: editingEducation?.is_current || false,
      description: editingEducation?.description || '',
      start_date: editingEducation?.start_date || '',
      end_date: editingEducation?.end_date || ''
    }
  });

  React.useEffect(() => {
    if (editingEducation) {
      reset({
        id: editingEducation.id,
        major: editingEducation.major,
        school_name: editingEducation.school_name,
        degree_type: editingEducation.degree_type,
        is_current: editingEducation.is_current,
        description: editingEducation.description,
        start_date: editingEducation.start_date,
        end_date: editingEducation.end_date
      });
    }
  }, [editingEducation, reset]);

  const isCurrent = watch('is_current');

  const onSubmit = (data: Education) => {
    handleAddEditEducation(data);
  };

  return (
    <Modal
      title={editMode ? "Edit Education" : "Add Education"}
      open={isVisible}
      onOk={handleSubmit(onSubmit)}
      confirmLoading={isAddingEducation || isUpdatingEducation}
      onCancel={closeModal}
      okText={editMode ? "Save" : "Add"}
    >
      <Form layout="vertical">
        <Form.Item
          label="Institution"
          required
          validateStatus={errors.school_name ? "error" : ""}
          help={errors.school_name?.message}
        >
          <Controller
            name="school_name"
            control={control}
            rules={{ required: "Institution name is required" }}
            render={({ field }) => (
              <Input
                {...field}
                placeholder="University/College Name"
              />
            )}
          />
        </Form.Item>
        <Form.Item label="Major">
          <Controller
            name="major"
            control={control}
            render={({ field }) => (
              <Input
                {...field}
                placeholder="Your field of study"
              />
            )}
          />
        </Form.Item>
        <Form.Item label="Degree">
          <Controller
            name="degree_type"
            control={control}
            render={({ field }) => (
              <Input
                {...field}
                placeholder="Degree/Certificate"
              />
            )}
          />
        </Form.Item>
        <Form.Item label="Current">
          <Controller
            name="is_current"
            control={control}
            render={({ field: { value, onChange } }) => (
              <>
                <input
                  type="checkbox"
                  checked={value}
                  onChange={(e) => onChange(e.target.checked)}
                  style={{ marginRight: 8 }}
                />
                <span>I currently study here</span>
              </>
            )}
          />
        </Form.Item>
        <Form.Item label="Start Date">
          <Controller
            name="start_date"
            control={control}
            render={({ field: { value, onChange } }) => (
              <DatePicker
                style={{ width: '100%' }}
                value={value ? dayjs(value) : null}
                onChange={(date) => onChange(date ? date.toISOString() : '')}
                placeholder="Select start date"
                format="YYYY-MM-DD"
              />
            )}
          />
        </Form.Item>
        <Form.Item label="End Date">
          <Controller
            name="end_date"
            control={control}
            render={({ field: { value, onChange } }) => (
              <DatePicker
                style={{ width: '100%' }}
                value={value ? dayjs(value) : null}
                onChange={(date) => onChange(date ? date.toISOString() : '')}
                placeholder="Select end date or leave empty"
                format="YYYY-MM-DD"
                disabled={isCurrent}
              />
            )}
          />
        </Form.Item>
        <Form.Item label="Description">
          <Controller
            name="description"
            control={control}
            render={({ field }) => (
              <Input.TextArea
                {...field}
                placeholder="Details about your education"
                rows={4}
              />
            )}
          />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export const ExperienceModal = ({
  isVisible,
  editMode,
  editingExperience,
  isAddingExperience,
  isUpdatingExperience,
  handleAddEditExperience: handleAddExperience,
  closeModal
}: ExperienceModalProps) => {
  const { control, handleSubmit, formState: { errors }, reset } = useForm<Experience>({
    defaultValues: {
      id: editingExperience?.id || '',
      company: editingExperience?.company || '',
      position: editingExperience?.position || '',
      start_date: editingExperience?.start_date || '',
      end_date: editingExperience?.end_date || '',
      description: editingExperience?.description || ''
    }
  });

  useEffect(() => {
    if (editingExperience) {
      reset({
        id: editingExperience.id,
        company: editingExperience.company,
        position: editingExperience.position,
        start_date: editingExperience.start_date,
        end_date: editingExperience.end_date,
        description: editingExperience.description
      });
    }
  }, [editingExperience, reset]);

  const onSubmit = (data: Experience) => {
    handleAddExperience(data);
  };

  return (
    <Modal
      title={editMode ? "Edit Experience" : "Add Experience"}
      open={isVisible}
      onOk={handleSubmit(onSubmit)}
      confirmLoading={isAddingExperience || isUpdatingExperience}
      onCancel={closeModal}
      okText={editMode ? "Save" : "Add"}
    >
      <Form layout="vertical">
        <Form.Item
          label="Company"
          required
          validateStatus={errors.company ? "error" : ""}
          help={errors.company?.message}
        >
          <Controller
            name="company"
            control={control}
            rules={{ required: "Company name is required" }}
            render={({ field }) => (
              <Input
                {...field}
                placeholder="Company Name"
              />
            )}
          />
        </Form.Item>
        <Form.Item
          label="Position"
          required
          validateStatus={errors.position ? "error" : ""}
          help={errors.position?.message}
        >
          <Controller
            name="position"
            control={control}
            rules={{ required: "Position is required" }}
            render={({ field }) => (
              <Input
                {...field}
                placeholder="Job Title"
              />
            )}
          />
        </Form.Item>
        <Form.Item label="Start Date">
          <Controller
            name="start_date"
            control={control}
            render={({ field: { value, onChange } }) => (
              <DatePicker
                style={{ width: '100%' }}
                value={value ? dayjs(value) : null}
                onChange={(date) => onChange(date ? date.toISOString() : '')}
                placeholder="Select start date"
                format="YYYY-MM-DD"
              />
            )}
          />
        </Form.Item>
        <Form.Item label="End Date">
          <Controller
            name="end_date"
            control={control}
            render={({ field: { value, onChange } }) => (
              <DatePicker
                style={{ width: '100%' }}
                value={value ? dayjs(value) : null}
                onChange={(date) => onChange(date ? date.toISOString() : '')}
                placeholder="Select end date or leave empty"
                format="YYYY-MM-DD"
              />
            )}
          />
        </Form.Item>
        <Form.Item label="Description">
          <Controller
            name="description"
            control={control}
            render={({ field }) => (
              <Input.TextArea
                {...field}
                placeholder="Details about your role and responsibilities"
                rows={4}
              />
            )}
          />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export const ProjectModal = ({
  isVisible,
  editMode,
  newProject,
  isAddingProject,
  isUpdatingProject,
  setNewProject,
  handleAddProject,
  closeModal
}: ProjectModalProps) => {
  const { control, handleSubmit, formState: { errors }, reset } = useForm<Project>({
    defaultValues: {
      id: newProject?.id || '',
      project_name: newProject?.project_name || '',
      role: newProject?.role || '',
      description: newProject?.description || '',
      achievement: newProject?.achievement || '',
      start_date: newProject?.start_date || '',
      end_date: newProject?.end_date || ''
    }
  });

  React.useEffect(() => {
    if (newProject) {
      reset({
        id: newProject.id,
        project_name: newProject.project_name,
        role: newProject.role,
        description: newProject.description,
        achievement: newProject.achievement,
        start_date: newProject.start_date,
        end_date: newProject.end_date
      });
    }
  }, [newProject, reset]);

  const onSubmit = (data: Project) => {
    setNewProject(data);
    handleAddProject();
  };

  return (
    <Modal
      title={editMode ? "Edit Project" : "Add Project"}
      open={isVisible}
      onOk={handleSubmit(onSubmit)}
      confirmLoading={isAddingProject || isUpdatingProject}
      onCancel={closeModal}
      okText={editMode ? "Save" : "Add"}
    >
      <Form layout="vertical">
        <Form.Item
          label="Project Name"
          required
          validateStatus={errors.project_name ? "error" : ""}
          help={errors.project_name?.message}
        >
          <Controller
            name="project_name"
            control={control}
            rules={{ required: "Project name is required" }}
            render={({ field }) => (
              <Input
                {...field}
                placeholder="Project Name"
              />
            )}
          />
        </Form.Item>
        <Form.Item label="Role">
          <Controller
            name="role"
            control={control}
            render={({ field }) => (
              <Input
                {...field}
                placeholder="Your role in the project"
              />
            )}
          />
        </Form.Item>
        <Form.Item label="Start Date">
          <Controller
            name="start_date"
            control={control}
            render={({ field: { value, onChange } }) => (
              <DatePicker
                style={{ width: '100%' }}
                value={value ? dayjs(value) : null}
                onChange={(date) => onChange(date ? date.toISOString() : '')}
                placeholder="Select start date"
                format="YYYY-MM-DD"
              />
            )}
          />
        </Form.Item>
        <Form.Item label="End Date">
          <Controller
            name="end_date"
            control={control}
            render={({ field: { value, onChange } }) => (
              <DatePicker
                style={{ width: '100%' }}
                value={value ? dayjs(value) : null}
                onChange={(date) => onChange(date ? date.toISOString() : '')}
                placeholder="Select end date or leave empty"
                format="YYYY-MM-DD"
              />
            )}
          />
        </Form.Item>
        <Form.Item label="Description">
          <Controller
            name="description"
            control={control}
            render={({ field }) => (
              <Input.TextArea
                {...field}
                placeholder="Project details"
                rows={4}
              />
            )}
          />
        </Form.Item>
        <Form.Item label="Achievement">
          <Controller
            name="achievement"
            control={control}
            render={({ field }) => (
              <Input.TextArea
                {...field}
                placeholder="What you achieved with this project"
                rows={2}
              />
            )}
          />
        </Form.Item>
      </Form>
    </Modal>
  );
};