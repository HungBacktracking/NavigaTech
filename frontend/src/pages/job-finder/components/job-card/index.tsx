import { Button, Card, Flex, Image, Space, Tag, theme, Tooltip, Typography } from "antd";
import { EnvironmentOutlined, ClockCircleOutlined, StarFilled, StarOutlined, AuditOutlined, BarChartOutlined } from "@ant-design/icons";
import { Job } from "../../../../lib/types/job";
import { blue, blueDark, orange } from "@ant-design/colors";
import { extractDomainFromUrl, formatDateToEngPeriodString } from "../../../../lib/helpers/string";
import AIButton from "../../../../components/ai-button";
import { useMobile } from "../../../../hooks/use-mobile";
import { MouseEvent } from "react";

const { Text, Title } = Typography;

interface JobCardProps {
  job: Job;
  handleToggleFavorite: (e: MouseEvent) => void;
  handleSelectJob: (job: Job) => void;
  handleJobAnalysisClick: (id: string) => void;
  isSelected: boolean;
  isAnalyzing?: boolean;
}

const JobCard = ({
  job,
  handleSelectJob,
  handleToggleFavorite,
  handleJobAnalysisClick,
  isSelected = false,
  isAnalyzing = false
}: JobCardProps) => {
  const { isMobile: isTablet } = useMobile(1024);
  const { token } = theme.useToken();

  return (
    <Card
      hoverable
      title={
        <Flex
          justify="space-between"
          align="center"
        >
          <Flex
            gap="middle"
            align="center"
            justify="start"
            style={{ padding: 0 }}>
            <div style={{ padding: 2, borderRadius: 4, backgroundColor: '#fafafa' }}>
              <Image
                src={job.logo_url || undefined}
                alt={`${job.company_name} logo`}
                fallback={`https://placehold.co/100x100/?text=${job.company_name[0]}`}
                style={{
                  width: 40,
                  height: 40,
                  borderRadius: 8,
                }}
                preview={false}
              />
            </div>
            <Flex vertical>
              <Title level={4} style={{ color: token.colorPrimary, margin: 0, fontWeight: 500, textWrap: "wrap" }}>
                {job.job_name}
              </Title>
              <Text type="secondary">
                {job.company_name}
              </Text>
            </Flex>
          </Flex>
          <Tooltip title={job.is_favorite ? "Remove from favorites" : "Add to favorites"} color={blueDark[3]}>
            <Button
              type="text"
              shape="circle"
              icon={job.is_favorite ? <StarFilled style={{ color: orange.primary, fontSize: 20 }} /> : <StarOutlined style={{ fontSize: 20, color: token.colorIcon }} />}
              onClick={handleToggleFavorite}
              style={{ marginLeft: "auto" }}
            />
          </Tooltip>
        </Flex>
      }
      onClick={() => handleSelectJob(job)}
      style={{
        borderRadius: 16,
        border: isSelected ? `0.5px solid ${blue[3]}` : undefined,
        boxShadow: isSelected ? `0 0 12px ${blue[2]}` : undefined,
        position: isSelected ? 'relative' : undefined,
      }}
      styles={{
        header: {
          padding: '8px 12px'
        },
        body: {
          padding: '12px 16px'
        },
      }}
    >
      {isSelected && (
        <div
          style={{
            position: 'absolute',
            left: 0,
            top: 10,
            bottom: 10,
            width: 4,
            backgroundColor: blue[3],
            borderRadius: 24,
            transition: 'all 0.3s ease-in-out',
          }}
        />
      )}
      <Space direction="vertical" size="middle" style={{ width: "100%" }}>
        <Flex vertical gap="small">
          {job.location && (
            <Space>
              <EnvironmentOutlined />
              {job.location}
            </Space>
          )}
          <Flex gap="large" wrap="wrap">
            {job.job_type && (
              <Space>
                <AuditOutlined />
                {job.job_type}
              </Space>
            )}
            {job && <span>{job.benefit}</span>}
          </Flex>
          {job.date_posted && (
            <Space>
              <ClockCircleOutlined />
              {formatDateToEngPeriodString(job.date_posted)}
            </Space>
          )}
        </Flex>
        {job.job_level && (
          <Tag color={token.colorWarningBg} style={{ padding: "2px 8px", fontSize: 12, borderRadius: 8, borderColor: token.colorWarningBorder }}>
            <Text>{job.job_level.toUpperCase()}</Text>
          </Tag>
        )}
        <Space wrap>
          {job.skills && job.skills.split(",").map((skill, index) => (
            <Tag key={index} color={token.colorInfoBg} style={{ padding: "2px 8px", fontSize: 12, borderRadius: 8 }}>
              <Text>{skill}</Text>
            </Tag>
          ))}
        </Space>
        <Flex
          vertical={isTablet}
          gap="small"
          justify="space-between"
          align="center"
          style={{ margin: "4px 0 0 0" }}>
          <a
            href={job.job_url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
          >
            {extractDomainFromUrl(job.job_url)}
          </a>

          <Space>
            <AIButton
              icon={<BarChartOutlined />}
              loading={isAnalyzing}
              onClick={(e: MouseEvent) => {
                e.stopPropagation();
                handleJobAnalysisClick(job.id);
              }}
              disabled={isAnalyzing}
            >
              {isAnalyzing ? "Analyzing..." : job.is_analyze ? "Re-Analyze" : "Analyze"}
            </AIButton>
          </Space>
        </Flex>
      </Space>

    </Card>
  );
};

export default JobCard;