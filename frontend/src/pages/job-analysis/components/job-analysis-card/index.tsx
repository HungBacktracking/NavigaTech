import { Button, Card, Flex, Image, Space, Tag, Typography, Progress, Popconfirm, theme } from "antd";
import {
  EnvironmentOutlined, ClockCircleOutlined, AuditOutlined,
  DeleteOutlined,
  CheckCircleFilled, CloseCircleFilled,
  DollarCircleOutlined,
  ArrowsAltOutlined,
} from "@ant-design/icons";
import { JobFavoriteResponse } from "../../../../lib/types/job";
import { blue, green, red, yellow } from "@ant-design/colors";
import { extractDomainFromUrl, formatDateToEngPeriodString } from "../../../../lib/helpers/string";
import { useMobile } from "../../../../hooks/use-mobile";
import { MouseEvent } from "react";
import { BoxArrowUpRight } from "react-bootstrap-icons";

const { Text, Title } = Typography;

interface JobAnalysisCardProps {
  jobAnalytic: JobFavoriteResponse;
  isDeletingJobAnalytic: boolean;
  handleDeleteJobAnalytic: (jobId: string) => void;
  handleViewDetail: (jobId: string) => void;
}

const JobAnalysisCard = ({
  jobAnalytic,
  isDeletingJobAnalytic,
  handleDeleteJobAnalytic,
  handleViewDetail,
}: JobAnalysisCardProps) => {
  const { isMobile: isTablet } = useMobile(1024);
  const { token } = theme.useToken();


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
                src={jobAnalytic.logo_url || undefined}
                alt={`${jobAnalytic.company_name} logo`}
                fallback={`https://placehold.co/100x100?text=${jobAnalytic.company_name[0]}`}
                style={{
                  width: 48,
                  height: 48,
                }}
              />
            </div>
            <Flex vertical>
              <Title level={4} style={{ margin: 0, fontWeight: 500, textWrap: "wrap" }}>
                {jobAnalytic.job_name}
              </Title>
              <Text type="secondary">
                {jobAnalytic.company_name}
              </Text>
            </Flex>
          </Flex>
          <Button
            type="text"
            icon={<BoxArrowUpRight />}
            href={jobAnalytic.job_url}
            target="_blank"
            onClick={(e: MouseEvent) => e.stopPropagation()}
            style={{
              color: token.colorPrimary,
              fontWeight: 600,
            }}
          >
            {extractDomainFromUrl(jobAnalytic.job_url)}
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
            <Flex vertical gap={isTablet ? "small" : "large"}>
              <Space>
                <EnvironmentOutlined />
                {jobAnalytic.location || 'Remote'}
              </Space>
              {jobAnalytic.company_name && (
                <Space>
                  <AuditOutlined />
                  {jobAnalytic.company_name}
                </Space>
              )}
              {jobAnalytic.job_type && (
                <Space>
                  <AuditOutlined />
                  {jobAnalytic.job_type}
                </Space>
              )}
              {jobAnalytic.benefit && (
                <Space>
                  <DollarCircleOutlined />
                  {jobAnalytic.benefit}
                </Space>
              )}
            </Flex>
            {jobAnalytic.date_posted && (
              <Space style={{ fontWeight: 500 }}>
                <ClockCircleOutlined />
                <span>{formatDateToEngPeriodString(jobAnalytic.date_posted)}</span>
              </Space>
            )}
            {/* <Space style={{ fontWeight: 500 }}>
              <SettingOutlined />
              <span>Analyzed on {analyzedAt.toLocaleString()}</span>
            </Space> */}
            <Space wrap>
              {jobAnalytic.skills && jobAnalytic.skills.split("<br>").map((skill, index) => (
                <Tag key={index} color={token.colorInfoBg} style={{ padding: "2px 8px", fontSize: 12, borderRadius: 8, borderColor: token.colorInfoBorder }}>
                  <Text style={{ color: token.colorInfoActive }}>{skill}</Text>
                </Tag>
              ))}
            </Space>
          </Flex>

          <div style={{ textAlign: 'center', minWidth: 100, marginRight: 16 }}>
            <Progress
              type="circle"
              percent={parseFloat(((jobAnalytic.job_analytics?.match_overall || 0) * 100).toFixed(2))}
              size={100}
              strokeColor={getMatchScoreColor((jobAnalytic.job_analytics?.match_overall || 0) * 100)}
              format={() => (
                <div style={{ fontSize: 24, color: getMatchScoreColor((jobAnalytic.job_analytics?.match_overall || 0) * 100) }}>
                  {parseFloat(((jobAnalytic.job_analytics?.match_overall || 0) * 100).toFixed(2))}%
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
            <CheckCircleFilled style={{ color: token.colorSuccess }} />
            <Text>
              {jobAnalytic.job_analytics?.strengths.split("<br>").slice(0, 1)}
            </Text>
          </Flex>
          <Flex align="center" gap="small" style={{ flex: 1 }}>
            <CloseCircleFilled style={{ color: token.colorError }} />
            <Text>
              {jobAnalytic.job_analytics?.weaknesses.split("<br>").slice(0, 1)}
            </Text>
          </Flex>
        </Flex>

        <Flex
          justify="space-between"
          align="center"
          wrap={isTablet ? "wrap" : "nowrap"}
          gap={isTablet ? "middle" : undefined}
        >
          {/* <Space>
            <Tag
              color={job.resume_url ? token.colorSuccessBg : token.colorErrorBg}
              style={{
                borderRadius: 16,
                padding: "4px 12px",
                borderColor: job.resume_url ? token.colorSuccessBorder : token.colorErrorBorder,
                color: job.resume_url ? token.colorSuccessActive : token.colorErrorActive,
              }}
            >
              {job.resume_url ? "CV Created" : "No CV Created"}
            </Tag>
            {!job.resume_url ? (
              <AIButton
                icon={<BookOutlined />}
                onClick={(e: MouseEvent) => {
                  e.stopPropagation();
                  handleToggleCV(analytics.id);
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
                  handleToggleCV(analytics.id);
                }}
              >
                View CV
              </Button>
            )}
          </Space> */}
          <Space>
            <Popconfirm
              title="Are you sure to delete this job analysis?"
              description="This action cannot be undone."
              onConfirm={() => handleDeleteJobAnalytic(jobAnalytic.id)}
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
                loading={isDeletingJobAnalytic}
              >
                {isDeletingJobAnalytic ? "Deleting..." : "Delete"}
              </Button>
            </Popconfirm>
            <Button
              icon={<ArrowsAltOutlined />}
              type="primary"
              shape="round"
              onClick={(e: MouseEvent) => {
                e.stopPropagation();
                handleViewDetail(jobAnalytic.id);
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