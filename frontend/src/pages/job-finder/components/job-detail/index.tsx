import { Button, Card, Flex, Image, Space, Tag, Tooltip, Typography, Divider } from "antd";
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
import { Job } from "../../../../lib/types/job";
import { blue, blueDark, gray, orange } from "@ant-design/colors";
import { extractDomainFromUrl, formatDateToEngPeriodString } from "../../../../lib/helpers/string";
import AIButton from "../../../../components/ai-button";
import { useMobile } from "../../../../hooks/use-mobile";
import ReactMarkdown from 'react-markdown';
import styles from './styles.module.css';

const { Text, Title } = Typography;

interface JobDetailProps {
  job: Job;
  isFavorite: boolean;
  handleToggleFavorite?: (e: MouseEvent) => void;
}

const JobDetail = ({ job, isFavorite, handleToggleFavorite }: JobDetailProps) => {
  const { isMobile } = useMobile(1024);

  const handleJobAnalysisClick = (id: string) => {
    console.log(`Job Analysis for job ID: ${id}`);
    // TODO: Implement job analysis logic here
  };

  const handleCreateCVClick = (id: string) => {
    console.log(`Create CV for job ID: ${id}`);
    // TODO: Implement create CV logic here
  };

  // Function to render content as Markdown if it contains markdown syntax
  const renderContent = (content: string) => {
    return (
      <ReactMarkdown>{content}</ReactMarkdown>
    );
  };

  return (
    <Card
      className="scrollbar-custom"
      style={{
        borderRadius: 16,
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
        overflowY: 'auto',
      }}
      title={
        <Flex horizontal justify="space-between" align="center">
          <Flex horizontal gap="middle" align="center" justify="start">
            <div style={{
              borderRadius: 4,
              backgroundColor: '#fafafa',
              padding: 2,
            }}>
              <Image
                src={job.company.logo}
                alt={`${job.company.name} logo`}
                fallback="https://placehold.co/100x100?text=Logo"
                style={{
                  width: 60,
                  height: 60,
                  objectFit: "contain"
                }}
                preview={false}
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
          <Flex vertical align="center">
            <Tooltip title={isFavorite ? "Remove from favorites" : "Add to favorites"} color={blueDark[1]}>
              <Button
                type="text"
                shape="circle"
                icon={isFavorite ? <StarFilled style={{ color: orange.primary, fontSize: 20 }} /> : <StarOutlined style={{ color: gray[3], fontSize: 20 }} />}
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
      }
      styles={{
        header: {
          padding: '16px 24px',
        },
        body: {
          padding: '24px',
        },
      }}
    >
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
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
              <Tag key={index} color={blue[0]} style={{ padding: "4px 12px", borderRadius: 8 }}>
                <Text>{skill}</Text>
              </Tag>
            ))}
          </Space>
        </Space>

        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <div>
            <Title level={3} style={{ margin: 0 }}>Description</Title>
            <div className={styles['markdown-content']}>
              {renderContent(job.jobDescription)}
            </div>
          </div>

          {job.jobRequirements && (
            <div>
              <Title level={3} style={{ margin: 0 }}>Requirements</Title>
              <div className={styles['markdown-content']}>
                {renderContent(job.jobRequirements)}
              </div>
            </div>
          )}

          {job.benefit && (
            <div>
              <Title level={3} style={{ margin: 0 }}>Benefits</Title>
              <div className={styles['markdown-content']}>
                {renderContent(job.benefit)}
              </div>
            </div>
          )}

          {job.company.description && (
            <div>
              <Title level={3} style={{ margin: 0 }}>About Company</Title>
              <div className={styles['markdown-content']} style={{ lineHeight: 1.6 }}>
                {renderContent(job.company.description)}
              </div>
            </div>
          )}
        </Space>

        <Divider style={{ margin: '12px 0' }} />

        <Flex
          horizontal={!isMobile}
          vertical={isMobile}
          gap="middle"
          justify="space-between"
          align={isMobile ? "stretch" : "center"}
        >
          <Button
            type="text"
            icon={<GlobalOutlined />}
            size="large"
            style={{
              color: blue.primary,
            }}
            onClick={(e: React.MouseEvent) => {
              e.stopPropagation();
              window.open(job.originalUrl, "_blank");
            }}
          >
            Apply on {extractDomainFromUrl(job.originalUrl)}
          </Button>

          <Flex gap="small" wrap="wrap" justify={isMobile ? "center" : "flex-end"}>
            <AIButton
              icon={<BarChartOutlined />}
              onClick={(e: React.MouseEvent) => {
                e.stopPropagation();
                handleJobAnalysisClick(job.id);
              }}
            >
              Job Analysis
            </AIButton>

            <AIButton
              icon={<BookOutlined />}
              onClick={(e: React.MouseEvent) => {
                e.stopPropagation();
                handleCreateCVClick(job.id);
              }}
            >
              Create CV
            </AIButton>
          </Flex>
        </Flex>
      </Space>
    </Card>
  );
};

export default JobDetail;