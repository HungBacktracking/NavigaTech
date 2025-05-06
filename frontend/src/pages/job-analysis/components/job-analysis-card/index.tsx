import { Button, Card, Flex, Image, Space, Tag, Typography, Progress, Popconfirm } from "antd";
import {
  EnvironmentOutlined, ClockCircleOutlined, AuditOutlined,
  BookOutlined, DeleteOutlined,
  CheckCircleFilled, CloseCircleFilled,
  DollarCircleOutlined,
  EyeOutlined,
  ArrowsAltOutlined,
  SettingOutlined
} from "@ant-design/icons";
import { JobAnalysis } from "../../../../lib/types/job";
import { blue, green, red, yellow } from "@ant-design/colors";
import { extractDomainFromUrl, formatDateToEngPeriodString } from "../../../../lib/helpers/string";
import AIButton from "../../../../components/ai-button";
import { useMobile } from "../../../../hooks/use-mobile";
import { MouseEvent } from "react";
import { BoxArrowUpRight } from "react-bootstrap-icons";

const { Text, Title } = Typography;

interface JobAnalysisCardProps {
  jobAnalysis: JobAnalysis;
  isDeletingJob: boolean;
  handleDeleteJob: (jobId: string) => void;
  handleToggleCV: (jobId: string) => void;
  handleViewDetail: (jobId: string) => void;
}

const JobAnalysisCard = ({
  jobAnalysis,
  isDeletingJob,
  handleDeleteJob,
  handleToggleCV,
  handleViewDetail,
}: JobAnalysisCardProps) => {
  const { isMobile: isTablet } = useMobile(1024);

  const getMatchScoreColor = (score: number) => {
    if (score >= 75) return green.primary;
    if (score >= 50) return blue.primary;
    if (score >= 25) return yellow[6];
    return red.primary;
  };

  return (
    <Card
      hoverable
      title={
        <Flex
          horizontal
          justify="space-between"
          align="center"
        >
          <Flex
            horizontal
            gap="middle"
            align="center"
            justify="start"
            style={{ padding: 0 }}>
            <div style={{ padding: 2, borderRadius: 4, backgroundColor: '#fafafa' }}>
              <Image
                src={jobAnalysis.companyLogo}
                alt={`${jobAnalysis.companyName} logo`}
                fallback={`https://placehold.co/100x100?text=${jobAnalysis.companyName[0]}`}
                style={{
                  width: 48,
                  height: 48,
                }}
              />
            </div>
            <Flex vertical>
              <Title level={4} style={{ margin: 0, fontWeight: 500, textWrap: "wrap" }}>
                {jobAnalysis.title}
              </Title>
              <Text type="secondary">
                {jobAnalysis.companyName}
              </Text>
            </Flex>
          </Flex>
          <Button
            type="text"
            icon={<BoxArrowUpRight />}
            href={jobAnalysis.originalUrl}
            target="_blank"
            onClick={(e: MouseEvent) => e.stopPropagation()}
            style={{
              color: blue[5],
              fontWeight: 600,
            }}
          >
            {extractDomainFromUrl(jobAnalysis.originalUrl)}
          </Button>
        </Flex>
      }
      style={{
        borderRadius: 16,
      }}
      styles={{
        header: {
          padding: '12px 24px 8px',
        },
        body: {
          padding: '12px 24px'
        },
      }}
    >
      <Space direction="vertical" size="middle" style={{ width: "100%" }}>
        <Flex
          justify="space-between"
          align="start"
          wrap={isTablet ? "wrap" : "nowrap"}
          gap={isTablet ? "middle" : undefined}
        >
          <Flex vertical gap="small" style={{ flex: 1 }}>
            <Flex wrap="wrap" gap={isTablet ? "small" : "large"}>
              <Space>
                <EnvironmentOutlined />
                {jobAnalysis.location}
              </Space>
              {jobAnalysis.type && (
                <Space>
                  <AuditOutlined />
                  {jobAnalysis.type}
                </Space>
              )}
              {jobAnalysis.salary && (
                <Space>
                  <DollarCircleOutlined />
                  {jobAnalysis.salary}
                </Space>
              )}
            </Flex>
            <Space style={{ fontWeight: 500 }}>
              <ClockCircleOutlined />
              <span>{formatDateToEngPeriodString(jobAnalysis.datePosted)}</span>
            </Space>
            <Space style={{ fontWeight: 500 }}>
              <SettingOutlined />
              <span>Analyzed on {jobAnalysis.analyzedAt.toLocaleString()}</span>
            </Space>
            <Space wrap>
              {jobAnalysis.skills.map((skill, index) => (
                <Tag key={index} color={blue[0]} style={{ padding: "2px 8px", fontSize: 12, borderRadius: 8, borderColor: blue[2] }}>
                  <Text style={{ color: blue[6] }}>{skill}</Text>
                </Tag>
              ))}
            </Space>
          </Flex>

          <div style={{ textAlign: 'center', minWidth: 100, marginRight: 16 }}>
            <Progress
              type="circle"
              percent={jobAnalysis.matchScore}
              size={100}
              strokeColor={getMatchScoreColor(jobAnalysis.matchScore)}
              format={(percent) => (
                <div style={{ fontSize: 24, color: getMatchScoreColor(jobAnalysis.matchScore) }}>
                  {percent}%
                </div>
              )}
            />
            <div style={{ marginTop: 4, fontWeight: 500 }}>Match Score</div>
          </div>
        </Flex>

        <Flex
          justify="space-between"
          align="center"
          wrap="wrap"
        >
          <Flex align="center" gap="small" style={{ flex: 1 }}>
            <CheckCircleFilled style={{ color: green.primary }} />
            <Text>
              {jobAnalysis.strengths[0]}
            </Text>
          </Flex>
          <Flex align="center" gap="small" style={{ flex: 1 }}>
            <CloseCircleFilled style={{ color: red.primary }} />
            <Text>
              {jobAnalysis.weaknesses[0]}
            </Text>
          </Flex>
        </Flex>

        <Flex
          justify="space-between"
          align="center"
          wrap={isTablet ? "wrap" : "nowrap"}
          gap={isTablet ? "middle" : undefined}
        >
          <Space>
            <Tag
              color={jobAnalysis.isCreatedCV ? green[0] : red[0]}
              style={{
                borderRadius: 16,
                padding: "4px 12px",
                borderColor: jobAnalysis.isCreatedCV ? green[4] : red[4],
                color: jobAnalysis.isCreatedCV ? green[6] : red[6],
              }}
            >
              {jobAnalysis.isCreatedCV ? "CV Created" : "No CV Created"}
            </Tag>
            {jobAnalysis.isCreatedCV ? (
              <AIButton
                icon={<BookOutlined />}
                onClick={(e: MouseEvent) => {
                  e.stopPropagation();
                  handleToggleCV(jobAnalysis.id);
                }}
              >
                Create CV
              </AIButton>
            ) : (
              <Button
                icon={<EyeOutlined />}
                type="primary"
                shape="round"
                onClick={(e: MouseEvent) => {
                  e.stopPropagation();
                  handleToggleCV(jobAnalysis.id);
                }}
              >
                View CV
              </Button>
            )}
          </Space>
          <Space>
            <Popconfirm
              title="Are you sure to delete this job analysis?"
              description="This action cannot be undone."
              onConfirm={() => handleDeleteJob(jobAnalysis.id)}
              okText="Yes"
              cancelText="No"
              placement="topRight"
            >
              <Button
                icon={<DeleteOutlined />}
                danger
                type="primary"
                shape="round"
                color="danger"
                loading={isDeletingJob}
              >
                {isDeletingJob ? "Deleting..." : "Delete"}
              </Button>
            </Popconfirm>
            <Button
              icon={<ArrowsAltOutlined />}
              type="primary"
              shape="round"
              onClick={(e: MouseEvent) => {
                e.stopPropagation();
                handleViewDetail(jobAnalysis.id);
              }}
            >
              Detail
            </Button>
          </Space>
        </Flex>
      </Space>
    </Card>
  );
};

export default JobAnalysisCard;