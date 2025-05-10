import { Button, Card, Flex, Image, Space, Tag, theme, Tooltip, Typography } from "antd";
import {
  EnvironmentOutlined,
  ClockCircleOutlined,
  StarFilled,
  StarOutlined,
  AuditOutlined,
  BookOutlined,
  BarChartOutlined,
  GlobalOutlined,
  DollarOutlined,
} from "@ant-design/icons";
import { DetailJob } from "../../../../lib/types/job";
import { blueDark, orange } from "@ant-design/colors";
import { extractDomainFromUrl, formatDateToEngPeriodString } from "../../../../lib/helpers/string";
import AIButton from "../../../../components/ai-button";
import { useMobile } from "../../../../hooks/use-mobile";
import ReactMarkdown from 'react-markdown';
import { MouseEvent } from "react";

const { Text, Title } = Typography;

interface JobDetailProps {
  job: DetailJob;
  isFavorite: boolean;
  handleToggleFavorite?: (e: MouseEvent) => void;
  handleJobAnalysisClick?: (id: string) => void;
  isAnalyzing?: boolean;
}

const JobDetail = ({ job, isFavorite, handleToggleFavorite, handleJobAnalysisClick, isAnalyzing = false }: JobDetailProps) => {
  const { isMobile: isTablet } = useMobile(1024);
  const { token } = theme.useToken();

  const handleCreateCVClick = (id: string) => {
    console.log(`Create CV for job ID: ${id}`);
    // TODO: Implement create CV logic here
  };

  const renderContent = (content: string) => {
    return (
      <div className="markdown-content">
        <ReactMarkdown>
          {content}
        </ReactMarkdown>
      </div>
    );
  };

  return (
    <Card
      className="scrollbar-custom"
      style={{
        borderRadius: 8,
        position: 'relative',
        height: '100%',
        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
      }}
      styles={{
        body: {
          overflowY: 'auto',
          padding: '12px 24px'
        },
        header: {
          position: 'sticky',
          top: -4,
          backgroundColor: 'white',
          zIndex: 1,
        }
      }}
      title={
        <Flex vertical style={{ padding: '8px 0' }}>
          <Flex horizontal justify="space-between" align="center">
            <Flex horizontal gap="small" align="center" justify="start">
              <div style={{
                borderRadius: 4,
                backgroundColor: '#fafafa',
                padding: 2,
              }}>
                <Image
                  src={job.company.logo}
                  alt={`${job.company.name} logo`}
                  fallback={`https://placehold.co/100x100?text=${job.company.name[0]}`}
                  style={{
                    width: 60,
                    height: 60,
                    objectFit: "contain"
                  }}
                />
              </div>
              <Flex vertical>
                <Title level={3} style={{ margin: 0, fontWeight: 600 }}>
                  {job.title}
                </Title>
                <Text strong>
                  {job.company.name}
                </Text>
              </Flex>
            </Flex>
            <Flex vertical align="center" justify="end">
              <Tooltip title={isFavorite ? "Remove from favorites" : "Add to favorites"} color={blueDark[3]}>
                <Button
                  type="text"
                  shape="circle"
                  icon={isFavorite ? <StarFilled style={{ color: orange.primary, fontSize: 20 }} /> : <StarOutlined style={{ fontSize: 20, color: token.colorIcon }} />}
                  onClick={handleToggleFavorite}
                />
              </Tooltip>
              {job.datePosted && (
                <Text type="secondary" style={{ fontSize: 13 }}>
                  <ClockCircleOutlined /> {formatDateToEngPeriodString(job.datePosted)}
                </Text>
              )}
            </Flex>
          </Flex>
          <Flex
            horizontal={!isTablet}
            vertical={isTablet}
            align="center"
            gap="small"
          >
            <Button
              type="text"
              icon={<GlobalOutlined />}
              style={{
                color: token.colorPrimary,
                fontWeight: 600,
              }}
              onClick={(e: React.MouseEvent) => {
                e.stopPropagation();
                window.open(job.originalUrl, "_blank");
              }}
            >
              Apply on {extractDomainFromUrl(job.originalUrl)}
            </Button>

            <Space>
              <AIButton
                icon={<BarChartOutlined />}
                loading={isAnalyzing}
                disabled={isAnalyzing}
                onClick={(e: MouseEvent) => {
                  e.stopPropagation();
                  if (handleJobAnalysisClick) {
                    handleJobAnalysisClick(job.id);
                  }
                }}
              >
                {isAnalyzing ? "Analyzing..." : "Job Analysis"}
              </AIButton>

              <AIButton
                icon={<BookOutlined />}
                onClick={(e: MouseEvent) => {
                  e.stopPropagation();
                  handleCreateCVClick(job.id);
                }}
              >
                Create CV
              </AIButton>
            </Space>
          </Flex>
        </Flex>
      }
    >

      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <Space direction="vertical" size="middle">
          <Flex vertical wrap="wrap" gap="small">
            <Space>
              <EnvironmentOutlined />
              <Text>{job.location}</Text>
            </Space>
            {job.type && (
              <Space>
                <AuditOutlined />
                <Text>{job.type}</Text>
              </Space>
            )}
            {job.salary && (
              <Space>
                <DollarOutlined />
                <Text>{job.salary}</Text>
              </Space>
            )}
          </Flex>

          <Space wrap style={{ width: '100%' }}>
            {job.skills.map((skill, index) => (
              <Tag key={index} color={token.colorInfoBg} style={{ padding: "4px 12px", borderRadius: 8, borderColor: token.colorInfoBorder }}>
                <Text style={{ color: token.colorInfoActive }}>{skill}</Text>
              </Tag>
            ))}
          </Space>
        </Space>

        <Space direction="vertical" size="middle">
          <div>
            <Title level={3} style={{ margin: 0 }}>Description</Title>
            <div className="markdown-content">
              {renderContent(job.jobDescription)}
            </div>
          </div>

          {job.jobRequirements && (
            <div>
              <Title level={3} style={{ margin: 0 }}>Requirements</Title>
              <div className="markdown-content">
                {renderContent(job.jobRequirements)}
              </div>
            </div>
          )}

          {job.benefit && (
            <div>
              <Title level={3} style={{ margin: 0 }}>Benefits</Title>
              <div className="markdown-content">
                {renderContent(job.benefit)}
              </div>
            </div>
          )}

          {job.company.description && (
            <div>
              <Title level={3} style={{ margin: 0 }}>About Company</Title>
              <div className="markdown-content" style={{ lineHeight: 1.6 }}>
                {renderContent(job.company.description)}
              </div>
            </div>
          )}
        </Space>
      </Space>
    </Card>
  );
};

export default JobDetail;